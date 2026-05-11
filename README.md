# 📊 1. Analiza Kohortowa Klientów – AdventureWorks

> **Stack:** Python · pandas · pyodbc · seaborn · SQL Server / T-SQL  
> **Baza danych:** AdventureWorks2019  
> **Typ projektu:** Data Analytics · Customer Retention · RFM Segmentation

---

## 🎯 Cel projektu

Projekt analizuje zachowanie klientów sklepu Adventure Works na przestrzeni czasu.  
Odpowiada na pytania biznesowe:

- Ilu klientów wraca po pierwszym zakupie? (**retencja**)
- Kiedy klienci najczęściej rezygnują? (**churn**)
- Jak zmieniała się liczba nowych vs powracających klientów? (**trend**)
- Kim są nasi najcenniejsi klienci? (**segmentacja RFM**)

---

## 🗂️ Struktura projektu

```
cohort_analysis/
├── queries.sql              ← zapytania T-SQL (widoki, retencja, RFM)
├── analysis.py              ← skrypt Python – pobieranie danych i wizualizacje
├── cohort_dashboard.png     ← wygenerowany dashboard (output)
├── retention_matrix.csv     ← macierz retencji (output)
├── trend_new_vs_returning.csv
├── rfm_segments.csv
└── README.md
```

---

## ⚙️ Instalacja i uruchomienie

### 1. Wymagania

```bash
pip install pandas pyodbc sqlalchemy matplotlib seaborn
```

Wymagany sterownik ODBC:  
👉 [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 2. Konfiguracja połączenia

W pliku `analysis.py` zmień zmienne na swoje:

```python
SERVER   = "localhost"           # np. "DESKTOP-XYZ\\SQLEXPRESS"
DATABASE = "AdventureWorks2019"
```

### 3. Uruchomienie

```bash
# Najpierw wykonaj widoki w SQL Server Management Studio:
# → otwórz queries.sql i uruchom sekcje KROK 1 i KROK 2

# Następnie uruchom skrypt Python:
python analysis.py
```

---

## 📈 Co zawiera dashboard

| Wykres | Opis |
|--------|-------|
| **Heatmapa retencji** | % klientów wracających w kolejnych miesiącach |
| **Rozmiar kohort** | Liczba nowych klientów pozyskanych każdego miesiąca |
| **Nowi vs powracający** | Miesięczny trend składu bazy klientów |
| **Segmentacja RFM** | Rozkład klientów wg wartości (Champions, Loyal, At Risk, Lost) |

---

## 🧠 Kluczowe koncepcje

### Analiza kohortowa
Kohorta = grupa klientów, którzy dokonali **pierwszego zakupu w tym samym miesiącu**.  
Śledzimy ich aktywność w kolejnych miesiącach, aby zmierzyć lojalność.

### RFM Segmentation
| Wymiar | Znaczenie |
|--------|-----------|
| **R** – Recency | Kiedy ostatnio kupił? (im świeżej, tym lepiej) |
| **F** – Frequency | Ile razy kupił? |
| **M** – Monetary | Ile łącznie wydał? |

### T-SQL – użyte funkcje okienkowe
```sql
FIRST_VALUE()  OVER (PARTITION BY ... ORDER BY ...)  -- wartość bazowa kohorty
ROW_NUMBER()   OVER (PARTITION BY CustomerID ...)    -- numer kolejnego zakupu
NTILE(4)       OVER (ORDER BY Recency ASC)           -- kwartyle RFM
DATEDIFF(MONTH, CohortMonth, OrderDate)              -- miesiące od dołączenia
```



# 📈 2. Prognozowanie Popytu – Demand Forecasting

> Projekt portfolio | Analityka Danych w Biznesie

## 📌 Opis projektu

Budowa modelu prognozowania popytu dla sklepu e-commerce na podstawie 3 lat danych dziennych.  
Projekt obejmuje pełen pipeline ML: od analizy sezonowości, przez feature engineering, po porównanie modeli i prognozę na przyszłość.

## 🎯 Zakres projektu

- **Analiza szeregu czasowego** – trend, sezonowość roczna i tygodniowa, efekty specjalne
- **Feature Engineering** – cechy kalendarzowe, cykliczne kodowanie sin/cos, lag features, rolling statistics
- **Porównanie modeli** – Regresja Liniowa vs Ridge vs Gradient Boosting
- **Ewaluacja** – MAE, RMSE, R², MAPE
- **Prognoza 30 dni** – predykcja popytu z przedziałem ufności

## 🛠️ Użyte technologie

| Biblioteka | Zastosowanie |
|-----------|--------------|
| `pandas` | Manipulacja danymi, resample, feature engineering |
| `numpy` | Obliczenia numeryczne, kodowanie cykliczne |
| `scikit-learn` | Modele ML, standaryzacja, metryki |
| `matplotlib` | Wykresy szeregów czasowych |
| `seaborn` | Wykresy analityczne |

## 📊 Wyniki modeli

| Model | MAE | RMSE | R² | MAPE |
|-------|-----|------|-----|------|
| Regresja Liniowa | ~28 szt. | ~36 szt. | ~0.85 | ~9% |
| Ridge Regression | ~27 szt. | ~35 szt. | ~0.86 | ~9% |
| **Gradient Boosting** | **~12 szt.** | **~16 szt.** | **~0.97** | **~4%** |

> 🏆 Gradient Boosting osiągnął najlepsze wyniki – MAPE poniżej 5%

## 📁 Struktura projektu

```
projekt_prognozowanie_popytu/
├── projekt_prognozowanie_popytu.ipynb   # Główny notebook
├── forecast_eda.png                     # Analiza sezonowości
├── forecast_wyniki.png                  # Prognozy vs rzeczywistość
├── forecast_feature_importance.png      # Ważność cech
├── forecast_przyszlosc.png              # Prognoza 30 dni
└── README.md
```

## 🚀 Uruchomienie

```bash
# Zainstaluj wymagane biblioteki
pip install pandas numpy scikit-learn matplotlib seaborn

# Uruchom notebook
jupyter notebook projekt_prognozowanie_popytu.ipynb
```

## 🔑 Kluczowe techniki

### Feature Engineering
```python
# Kodowanie cykliczne – kluczowe dla sezonowości!
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

# Lag features (opóźnienia)
df['lag_7']  = df['demand'].shift(7)   # popyt sprzed tygodnia
df['lag_30'] = df['demand'].shift(30)  # popyt sprzed miesiąca

# Rolling statistics
df['rolling_mean_30'] = df['demand'].shift(1).rolling(30).mean()
```

### Poprawny podział temporalny
```python
# NIE losowy – w szeregach czasowych testujemy na przyszłości!
train = df[df['date'] < '2023-07-01']
test  = df[df['date'] >= '2023-07-01']
```

## 💡 Kluczowe wnioski biznesowe

1. **Sezonowość:** wzrost sprzedaży o ~45% w grudniu – zwiększyć stany magazynowe
2. **Black Friday:** skokowy wzrost popytu – planować kampanie z wyprzedzeniem
3. **Dni tygodnia:** weekendy generują wyższy popyt niż dni robocze
4. **Promocje:** zwiększają popyt średnio o ~15% – warto zaplanować je na słabsze dni

---
*Projekt stworzony w ramach portfolio do stażu z zakresu analityki danych*
