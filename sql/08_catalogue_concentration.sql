-- Q8. How concentrated are sales across the catalogue?

WITH per_beat AS (
    SELECT beat_title, COUNT(*) AS sales
    FROM paid_items
    GROUP BY beat_title
),
ranked AS (
    SELECT sales, ROW_NUMBER() OVER (ORDER BY sales DESC) AS rnk
    FROM per_beat
)
SELECT
    ROUND(100.0 * SUM(CASE WHEN rnk = 1   THEN sales END) / SUM(sales), 0) AS top_beat_pct,
    ROUND(100.0 * SUM(CASE WHEN rnk <= 10 THEN sales END) / SUM(sales), 0) AS top_10_pct,
    ROUND(100.0 * SUM(sales = 1) / COUNT(*), 0)                            AS sold_once_pct
FROM ranked;
