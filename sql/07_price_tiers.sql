-- Q7. Which licence price points sell? Grouped by list price (USD).

SELECT
    CASE
        WHEN list_price < 35   THEN '1. Under 35'
        WHEN list_price < 60   THEN '2. 35 to 59'
        WHEN list_price < 100  THEN '3. 60 to 99'
        ELSE                        '4. 100 and over'
    END                                                   AS price_band,
    100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()              AS pct_of_items
FROM paid_items
GROUP BY 1
ORDER BY 1;
