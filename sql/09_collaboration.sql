-- Q9. How much of the catalogue is co-produced?

WITH item_parties AS (
    SELECT order_id, item_no, SUM(party <> 'me') AS collaborators
    FROM payment_splits
    GROUP BY order_id, item_no
)
SELECT ROUND(100.0 * AVG(collaborators > 0), 0) AS co_produced_pct
FROM item_parties;
