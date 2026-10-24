-- Q6. Share of paid orders through my own storefront versus the platform's public marketplace.

SELECT
    CASE WHEN order_time_utc < '2024-01-01' THEN strftime('%Y', order_time_utc) ELSE '2024 to 2026' END AS period,
    ROUND(100.0 * AVG(channel = 'own_store'), 0)     AS own_storefront_pct,
    ROUND(100.0 * AVG(channel = 'marketplace'), 0)  AS marketplace_pct
FROM paid_orders
GROUP BY 1
ORDER BY 1;
