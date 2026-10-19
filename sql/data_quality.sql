-- Day 1: SQL data quality exercises.
-- Assumed table: customers
-- Columns: customer_id, age, city, purchase_amount, signup_date

-- 1. Count records.
SELECT COUNT(*) AS total_rows
FROM customers;

-- 2. Check missing values.
SELECT
    SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) AS missing_age,
    SUM(CASE WHEN city IS NULL THEN 1 ELSE 0 END) AS missing_city,
    SUM(
        CASE WHEN purchase_amount IS NULL THEN 1 ELSE 0 END
    ) AS missing_purchase_amount
FROM customers;

-- 3. Identify duplicate customer identifiers.
SELECT
    customer_id,
    COUNT(*) AS occurrences
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- 4. Inspect invalid numeric values.
SELECT *
FROM customers
WHERE age < 0
   OR purchase_amount < 0;

-- 5. Check city distribution.
SELECT
    city,
    COUNT(*) AS customer_count
FROM customers
GROUP BY city
ORDER BY customer_count DESC;
