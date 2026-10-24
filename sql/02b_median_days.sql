-- Q2b. Median days from free download to first purchase.

WITH converted AS (
    SELECT julianday(b.first_paid_time) - julianday(s.optin_time_utc) AS days
    FROM subscribers AS s
    JOIN buyers AS b USING (customer_id)
    WHERE s.source = 'auto_signup'
      AND s.tag_free_download = 1
      AND julianday(b.first_paid_time) - julianday(s.optin_time_utc) > 1.0 / 24
),
ranked AS (
    SELECT days,
           ROW_NUMBER() OVER (ORDER BY days) AS rn,
           COUNT(*) OVER ()                  AS n
    FROM converted
)
SELECT ROUND(AVG(days), 0) AS median_days
FROM ranked
WHERE rn IN ((n + 1) / 2, (n + 2) / 2);
