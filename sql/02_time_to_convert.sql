-- Q2. For free downloaders who converted, how long did it take?
-- Returns the share in each time band, rounded to whole percentages.

WITH converted AS (
    SELECT julianday(b.first_paid_time) - julianday(s.optin_time_utc) AS days
    FROM subscribers AS s
    JOIN buyers AS b USING (customer_id)
    WHERE s.source = 'auto_signup'
      AND s.tag_free_download = 1
      AND julianday(b.first_paid_time) - julianday(s.optin_time_utc) > 1.0 / 24
)
SELECT
    CASE
        WHEN days <= 7   THEN '1. Within a week'
        WHEN days <= 30  THEN '2. 1 to 4 weeks'
        WHEN days <= 90  THEN '3. 1 to 3 months'
        ELSE                  '4. 3 to 12 months'
    END                                                   AS time_to_convert,
    100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()              AS pct
FROM converted
GROUP BY 1
ORDER BY 1;
