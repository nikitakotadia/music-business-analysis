-- Q3. Do buyers on the list come back more often?
-- Limited to buyers whose first purchase came after the list started (May 2021),
-- so every buyer had the chance to be on it. File imports are excluded:
-- their join date is the day I uploaded them, not when they found me.

SELECT
    CASE WHEN path = 'not_on_list' THEN 'Not on the list' ELSE 'On the list' END AS list_status,
    ROUND(100.0 * AVG(paid_orders > 1), 1)            AS repeat_pct
FROM buyer_paths
WHERE first_paid_time >= '2021-05-05'
  AND path <> 'file_import'
GROUP BY 1
ORDER BY 1 DESC;
