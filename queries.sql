
-- PROJEKT: Analiza Kohortowa Klientów – AdventureWorks
-- Baza:    AdventureWorks2019 (lub 2017/2016)
-- Autor:   Jakub Kubacki

-- KROK 1: Pierwsza data zakupu każdego klienta (definicja kohorty)
-- Kohorta = miesiąc, w którym klient złożył PIERWSZE zamówienie.
-- Każdy klient należy do dokładnie jednej kohorty przez cały czas.

CREATE OR ALTER VIEW Sales.vw_CustomerCohort AS
SELECT
    CustomerID,
    DATEFROMPARTS(YEAR(MIN(OrderDate)), MONTH(MIN(OrderDate)), 1) AS CohortMonth
FROM Sales.SalesOrderHeader
WHERE OnlineOrderFlag = 1        
GROUP BY CustomerID;
GO


-- KROK 2: Wszystkie zamówienia z numerem miesiąca od kohorty
-- CohortIndex = 0  → miesiąc pierwszego zakupu
-- CohortIndex = 1  → miesiąc po pierwszym zakupie itd.

CREATE OR ALTER VIEW Sales.vw_CohortData AS
SELECT
    soh.CustomerID,
    cc.CohortMonth,
    DATEDIFF(MONTH, cc.CohortMonth, soh.OrderDate)   AS CohortIndex,
    soh.TotalDue                                      AS OrderValue
FROM Sales.SalesOrderHeader        soh
JOIN Sales.vw_CustomerCohort       cc  ON soh.CustomerID = cc.CustomerID
WHERE soh.OnlineOrderFlag = 1
AND soh.Status = 5;
GO

-- KROK 3: Tabela retencji – ilu klientów wraca w każdym miesiącu
SELECT
    CohortMonth,
    CohortIndex,
    COUNT(DISTINCT CustomerID)                            AS ActiveCustomers,
    CAST(
        COUNT(DISTINCT CustomerID) * 100.0 /
        FIRST_VALUE(COUNT(DISTINCT CustomerID))
            OVER (PARTITION BY CohortMonth ORDER BY CohortIndex
                  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
    AS DECIMAL(5,2))                                      AS RetentionRate
FROM Sales.vw_CohortData
GROUP BY CohortMonth, CohortIndex
ORDER BY CohortMonth, CohortIndex;

-- KROK 4: Przychód per kohorta i miesiąc (Revenue Cohort)

SELECT
    CohortMonth,
    CohortIndex,
    COUNT(DISTINCT CustomerID)    AS ActiveCustomers,
    ROUND(SUM(OrderValue), 2)     AS TotalRevenue,
    ROUND(AVG(OrderValue), 2)     AS AvgOrderValue
FROM Sales.vw_CohortData
GROUP BY CohortMonth, CohortIndex
ORDER BY CohortMonth, CohortIndex;


-- KROK 5: Segmentacja klientów (RFM uproszczone)
-- R = Recency   – kiedy ostatnio kupił
-- F = Frequency – ile razy kupił
-- M = Monetary  – ile wydał łącznie

WITH RFM AS (
    SELECT
        CustomerID,
        DATEDIFF(DAY, MAX(OrderDate), '2014-06-30')  AS Recency,
        COUNT(SalesOrderID)                           AS Frequency,
        ROUND(SUM(TotalDue), 2)                       AS Monetary
    FROM Sales.SalesOrderHeader
    WHERE OnlineOrderFlag = 1
      AND Status = 5
    GROUP BY CustomerID
),
RFM_Scored AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY Recency ASC)    AS R_Score,
        NTILE(4) OVER (ORDER BY Frequency DESC) AS F_Score,
        NTILE(4) OVER (ORDER BY Monetary DESC)  AS M_Score
    FROM RFM
)
SELECT
    CustomerID,
    Recency,
    Frequency,
    Monetary,
    R_Score,
    F_Score,
    M_Score,
    R_Score + F_Score + M_Score                          AS RFM_Total,
    CASE
        WHEN R_Score + F_Score + M_Score >= 10 THEN 'Champions'
        WHEN R_Score + F_Score + M_Score >= 7  THEN 'Loyal Customers'
        WHEN R_Score >= 3 AND F_Score <= 2      THEN 'At Risk'
        WHEN R_Score <= 2                       THEN 'Lost'
        ELSE                                         'Potential Loyalists'
    END AS CustomerSegment
FROM RFM_Scored
ORDER BY RFM_Total DESC;

-- KROK 6: Miesięczny trend – nowi vs powracający klienci

WITH OrderDates AS (
    SELECT
        CustomerID,
        OrderDate,
        DATEFROMPARTS(YEAR(OrderDate), MONTH(OrderDate), 1) AS OrderMonth,
        ROW_NUMBER() OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS OrderRank
    FROM Sales.SalesOrderHeader
    WHERE OnlineOrderFlag = 1 AND Status = 5
)
SELECT
    OrderMonth,
    COUNT(CASE WHEN OrderRank = 1 THEN 1 END)  AS NewCustomers,
    COUNT(CASE WHEN OrderRank > 1 THEN 1 END)  AS ReturningCustomers,
    COUNT(*)                                    AS TotalOrders
FROM OrderDates
GROUP BY OrderMonth
ORDER BY OrderMonth;
