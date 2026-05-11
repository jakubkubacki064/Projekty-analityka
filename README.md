# 📊 Analiza Kohortowa Klientów – AdventureWorks

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

---

## 💼 Co pokazuje ten projekt rekruterowi

- Umiejętność łączenia **Pythona z SQL Serverem** (pyodbc + SQLAlchemy)
- Znajomość **zaawansowanych zapytań T-SQL** (CTE, funkcje okienkowe)
- Praca z **realną bazą danych** (AdventureWorks)
- Tworzenie **business insights** z surowych danych transakcyjnych
- Budowanie **dashboardów** (matplotlib + seaborn)
- Znajomość metod analitycznych: **cohort analysis + RFM**

---

## 🔧 Możliwe rozszerzenia

- [ ] Eksport raportu do PDF (biblioteka `reportlab` lub `fpdf`)
- [ ] Interaktywny dashboard w **Plotly Dash**
- [ ] Automatyczne odświeżanie danych (scheduled task)
- [ ] Predykcja churnu (scikit-learn – Logistic Regression / Random Forest)
