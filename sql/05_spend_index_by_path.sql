-- Q5. Average spend per buyer, as an index (buyers not on the list = 100).
-- Shown as an index so no revenue figures are exposed.

WITH spend AS (
    SELECT path, AVG(total_spend) AS avg_spend
    FROM buyer_paths
    WHERE first_paid_time >= '2021-05-05'
      AND path <> 'file_import'
    GROUP BY path
)
SELECT
    path,
    ROUND(100.0 * avg_spend / (SELECT avg_spend FROM spend WHERE path = 'not_on_list'), 0) AS spend_index
FROM spend
ORDER BY spend_index DESC;
