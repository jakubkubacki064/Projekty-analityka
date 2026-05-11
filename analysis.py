
# PROJEKT: Analiza Kohortowa Klientów – AdventureWorks
# Stack:   Python (pandas, pyodbc, matplotlib, seaborn)

import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings("ignore")

# 1. KONFIGURACJA POŁĄCZENIA Z BAZĄ DANYCH

# Zmień poniższe wartości na swoje
SERVER   = "localhost"
DATABASE = "AdventureWorks2019"
# Jeśli używasz Windows Authentication (najczęściej lokalnie):
CONN_STR = (
    f"mssql+pyodbc://{SERVER}/{DATABASE}"
    f"?driver=ODBC+Driver+17+for+SQL+Server"
    f"&trusted_connection=yes"
)

engine = create_engine(CONN_STR)
print("✅ Połączono z bazą danych AdventureWorks")

# 2. POBIERANIE DANYCH Z SQL

def run_query(sql: str) -> pd.DataFrame:
    """Pomocnicza funkcja wykonująca zapytanie i zwracająca DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


# -- 2a. Dane kohortowe (retencja) --
sql_cohort = """
WITH CohortBase AS (
    SELECT
        CustomerID,
        DATEFROMPARTS(YEAR(MIN(OrderDate)), MONTH(MIN(OrderDate)), 1) AS CohortMonth
    FROM Sales.SalesOrderHeader
    WHERE OnlineOrderFlag = 1
    GROUP BY CustomerID
),
AllOrders AS (
    SELECT
        soh.CustomerID,
        cb.CohortMonth,
        DATEDIFF(MONTH, cb.CohortMonth, soh.OrderDate) AS CohortIndex
    FROM Sales.SalesOrderHeader soh
    JOIN CohortBase cb ON soh.CustomerID = cb.CustomerID
    WHERE soh.OnlineOrderFlag = 1 AND soh.Status = 5
)
SELECT
    CohortMonth,
    CohortIndex,
    COUNT(DISTINCT CustomerID) AS ActiveCustomers
FROM AllOrders
GROUP BY CohortMonth, CohortIndex
"""

# -- 2b. Trend nowi vs powracający --
sql_trend = """
WITH OrderDates AS (
    SELECT
        CustomerID,
        DATEFROMPARTS(YEAR(OrderDate), MONTH(OrderDate), 1) AS OrderMonth,
        ROW_NUMBER() OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS OrderRank
    FROM Sales.SalesOrderHeader
    WHERE OnlineOrderFlag = 1 AND Status = 5
)
SELECT
    OrderMonth,
    COUNT(CASE WHEN OrderRank = 1 THEN 1 END)  AS NewCustomers,
    COUNT(CASE WHEN OrderRank > 1 THEN 1 END)  AS ReturningCustomers
FROM OrderDates
GROUP BY OrderMonth
"""

# -- 2c. Segmentacja RFM --
sql_rfm = """
WITH RFM AS (
    SELECT
        CustomerID,
        DATEDIFF(DAY, MAX(OrderDate), '2014-06-30') AS Recency,
        COUNT(SalesOrderID)                          AS Frequency,
        ROUND(SUM(TotalDue), 2)                      AS Monetary
    FROM Sales.SalesOrderHeader
    WHERE OnlineOrderFlag = 1 AND Status = 5
    GROUP BY CustomerID
),
Scored AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY Recency ASC)    AS R,
        NTILE(4) OVER (ORDER BY Frequency DESC) AS F,
        NTILE(4) OVER (ORDER BY Monetary DESC)  AS M
    FROM RFM
)
SELECT
    CASE
        WHEN R + F + M >= 10 THEN 'Champions'
        WHEN R + F + M >= 7  THEN 'Loyal Customers'
        WHEN R >= 3 AND F <= 2 THEN 'At Risk'
        WHEN R <= 2            THEN 'Lost'
        ELSE                        'Potential Loyalists'
    END AS Segment,
    COUNT(*) AS CustomerCount
FROM Scored
GROUP BY
    CASE
        WHEN R + F + M >= 10 THEN 'Champions'
        WHEN R + F + M >= 7  THEN 'Loyal Customers'
        WHEN R >= 3 AND F <= 2 THEN 'At Risk'
        WHEN R <= 2            THEN 'Lost'
        ELSE                        'Potential Loyalists'
    END
"""

df_cohort = run_query(sql_cohort)
df_trend  = run_query(sql_trend)
df_rfm    = run_query(sql_rfm)
print("✅ Dane pobrane z SQL Server")


# 3. TRANSFORMACJA DANYCH W PANDAS

# -- 3a. Macierz retencji (pivot) --
df_cohort["CohortMonth"] = pd.to_datetime(df_cohort["CohortMonth"])

cohort_pivot = df_cohort.pivot_table(
    index="CohortMonth",
    columns="CohortIndex",
    values="ActiveCustomers"
)

# Obliczanie % retencji względem miesiąca bazowego (CohortIndex = 0)
cohort_size = cohort_pivot[0]
retention_matrix = cohort_pivot.divide(cohort_size, axis=0).round(4)
retention_matrix.index = retention_matrix.index.strftime("%Y-%m")
retention_matrix.columns = [f"Miesiąc {i}" for i in retention_matrix.columns]

# -- 3b. Trend --
df_trend["OrderMonth"] = pd.to_datetime(df_trend["OrderMonth"])
df_trend = df_trend.sort_values("OrderMonth")

print("✅ Dane przetransformowane")
print(f"\n📊 Liczba kohort: {len(retention_matrix)}")
print(f"📊 Segmenty RFM:\n{df_rfm.to_string(index=False)}")

# 4. WIZUALIZACJE

fig, axes = plt.subplots(2, 2, figsize=(18, 13))
fig.patch.set_facecolor("#0f1117")
fig.suptitle(
    "Analiza Kohortowa Klientów – AdventureWorks",
    fontsize=20, fontweight="bold", color="white", y=0.98
)

ACCENT   = "#00d4aa"
BG_COLOR = "#1a1d27"
TEXT_COL = "#e0e0e0"

def style_ax(ax, title):
    ax.set_facecolor(BG_COLOR)
    ax.set_title(title, color=TEXT_COL, fontsize=13, fontweight="bold", pad=10)
    ax.tick_params(colors=TEXT_COL, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#333")


# --- Wykres 1: Heatmapa retencji ---
ax1 = axes[0, 0]
mask = retention_matrix.isnull()
sns.heatmap(
    retention_matrix,
    ax=ax1,
    annot=True,
    fmt=".0%",
    cmap="YlOrRd_r",
    mask=mask,
    linewidths=0.5,
    linecolor="#0f1117",
    cbar_kws={"shrink": 0.8},
    annot_kws={"size": 8}
)
ax1.set_facecolor(BG_COLOR)
ax1.set_title("🔥 Macierz Retencji Klientów (%)", color=TEXT_COL,
              fontsize=13, fontweight="bold", pad=10)
ax1.set_xlabel("Miesiące od pierwszego zakupu", color=TEXT_COL, fontsize=9)
ax1.set_ylabel("Kohorta (miesiąc 1. zakupu)", color=TEXT_COL, fontsize=9)
ax1.tick_params(colors=TEXT_COL, labelsize=8)
ax1.xaxis.set_ticklabels(
    [f"M{i}" for i in range(len(retention_matrix.columns))],
    color=TEXT_COL
)


# --- Wykres 2: Rozmiar kohort (słupkowy) ---
ax2 = axes[0, 1]
cohort_bar = cohort_size.copy()
cohort_bar.index = pd.to_datetime(cohort_bar.index).strftime("%Y-%m")
bars = ax2.bar(cohort_bar.index, cohort_bar.values,
               color=ACCENT, alpha=0.85, edgecolor="#0f1117", linewidth=0.5)
ax2.bar_label(bars, fmt="%d", color=TEXT_COL, fontsize=7, padding=3)
style_ax(ax2, "📦 Rozmiar Kohort – nowi klienci per miesiąc")
ax2.set_xlabel("Kohorta", color=TEXT_COL, fontsize=9)
ax2.set_ylabel("Liczba klientów", color=TEXT_COL, fontsize=9)
ax2.tick_params(axis="x", rotation=45)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))


# --- Wykres 3: Nowi vs powracający (stacked area) ---
ax3 = axes[1, 0]
ax3.fill_between(df_trend["OrderMonth"], df_trend["NewCustomers"],
                 alpha=0.7, color=ACCENT, label="Nowi klienci")
ax3.fill_between(df_trend["OrderMonth"], df_trend["ReturningCustomers"],
                 alpha=0.6, color="#ff6b6b", label="Powracający klienci")
ax3.plot(df_trend["OrderMonth"], df_trend["NewCustomers"],
         color=ACCENT, linewidth=1.5)
ax3.plot(df_trend["OrderMonth"], df_trend["ReturningCustomers"],
         color="#ff6b6b", linewidth=1.5)
style_ax(ax3, "📈 Nowi vs Powracający Klienci (miesięcznie)")
ax3.set_xlabel("Miesiąc", color=TEXT_COL, fontsize=9)
ax3.set_ylabel("Liczba klientów", color=TEXT_COL, fontsize=9)
legend = ax3.legend(facecolor="#1a1d27", edgecolor="#333",
                    labelcolor=TEXT_COL, fontsize=9)
ax3.tick_params(axis="x", rotation=30)


# --- Wykres 4: Segmentacja RFM (donut) ---
ax4 = axes[1, 1]
colors_rfm = ["#00d4aa", "#4ecdc4", "#f7b731", "#ff6b6b", "#a29bfe"]
wedges, texts, autotexts = ax4.pie(
    df_rfm["CustomerCount"],
    labels=df_rfm["Segment"],
    colors=colors_rfm[:len(df_rfm)],
    autopct="%1.1f%%",
    pctdistance=0.75,
    startangle=90,
    wedgeprops={"edgecolor": "#0f1117", "linewidth": 2}
)
for t in texts:
    t.set_color(TEXT_COL)
    t.set_fontsize(9)
for at in autotexts:
    at.set_color("#0f1117")
    at.set_fontsize(8)
    at.set_fontweight("bold")
# Dziura donut
circle = plt.Circle((0, 0), 0.5, color=BG_COLOR)
ax4.add_patch(circle)
ax4.set_facecolor(BG_COLOR)
ax4.set_title("🎯 Segmentacja Klientów (RFM)", color=TEXT_COL,
              fontsize=13, fontweight="bold", pad=10)


plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("cohort_analysis/cohort_dashboard.png",
            dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.show()
print("✅ Dashboard zapisany: cohort_analysis/cohort_dashboard.png")

# 5. EKSPORT WYNIKÓW DO CSV (do portfolio / dokumentacji)

retention_matrix.to_csv("cohort_analysis/retention_matrix.csv")
df_trend.to_csv("cohort_analysis/trend_new_vs_returning.csv", index=False)
df_rfm.to_csv("cohort_analysis/rfm_segments.csv", index=False)
print("✅ Wyniki zapisane do plików CSV")

# 6. PODSUMOWANIE TEKSTOWE

best_cohort  = cohort_size.idxmax()
worst_cohort = cohort_size.idxmin()

print("\n" + "="*55)
print("  PODSUMOWANIE ANALIZY KOHORTOWEJ")
print("="*55)
print(f"  📅 Analizowane kohorty:    {len(retention_matrix)}")
print(f"  👥 Łączna liczba klientów: {int(cohort_size.sum()):,}")
print(f"  🏆 Największa kohorta:     {best_cohort} ({int(cohort_size.max()):,} klientów)")
print(f"  📉 Najmniejsza kohorta:    {worst_cohort} ({int(cohort_size.min()):,} klientów)")

if 1 in cohort_pivot.columns:
    avg_m1_retention = (cohort_pivot[1] / cohort_pivot[0]).mean()
    print(f"  🔄 Śr. retencja po 1 mies.: {avg_m1_retention:.1%}")
print("="*55)
