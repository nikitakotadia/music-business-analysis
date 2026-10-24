-- Q4. Where do new buyers come from: the peak years against recent years.
-- Share of first-time buyers who had joined the list before buying.
-- Years are grouped into two periods because single recent years are small.

SELECT
    CASE WHEN first_paid_time < '2024-01-01' THEN '1. 2021 to 2023' ELSE '2. 2024 to 2026' END AS period,
    ROUND(100.0 * AVG(path = 'joined_list_first'), 0)                                     AS joined_list_first_pct
FROM buyer_paths
WHERE first_paid_time >= '2021-05-05'
GROUP BY 1
ORDER BY 1;
