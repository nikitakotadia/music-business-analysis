-- Q1. What share of free downloaders go on to buy a paid licence?
-- Free downloaders: subscribers the sales platform added after a free download.
-- Converted: their first paid purchase came more than an hour after they joined.
-- (Within the hour means they joined by buying, not by downloading.)
-- Returns a rate only, so no audience or sales volumes are exposed.

WITH free_downloaders AS (
    SELECT
        f.customer_id,
        b.first_paid_time IS NOT NULL
            AND julianday(b.first_paid_time) - julianday(f.optin_time_utc) > 1.0 / 24 AS converted
    FROM subscribers AS f
    LEFT JOIN buyers AS b USING (customer_id)
    WHERE f.source = 'auto_signup'
      AND f.tag_free_download = 1
)
SELECT
    ROUND(100.0 * AVG(converted), 1)  AS conversion_pct,
    ROUND(1.0 / AVG(converted), 0)    AS one_in
FROM free_downloaders;
