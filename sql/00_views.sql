-- Shared building blocks for every analysis query.
-- A "paid purchase" is an item with a sale price above zero, in an order
-- that is completed or has no recorded status. The one pending order is excluded.

DROP VIEW IF EXISTS paid_items;
CREATE VIEW paid_items AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_time_utc,
    o.channel,
    i.item_no,
    i.beat_title,
    i.list_price,
    i.sale_price
FROM orders AS o
JOIN order_items AS i USING (order_id)
WHERE o.status <> 'pending'
  AND i.sale_price > 0;


DROP VIEW IF EXISTS paid_orders;
CREATE VIEW paid_orders AS
SELECT
    order_id,
    customer_id,
    MIN(order_time_utc) AS order_time_utc,
    MIN(channel)        AS channel,
    SUM(sale_price)     AS order_value,
    COUNT(*)            AS items
FROM paid_items
GROUP BY order_id, customer_id;


-- One row per paying customer.
DROP VIEW IF EXISTS buyers;
CREATE VIEW buyers AS
SELECT
    customer_id,
    MIN(order_time_utc) AS first_paid_time,
    COUNT(*)            AS paid_orders,
    SUM(order_value)    AS total_spend
FROM paid_orders
GROUP BY customer_id;


-- How each buyer relates to the email list.
--   joined_list_first   : added automatically by the sales platform (almost always a free download) more than an hour before first paying
--   joined_at_checkout  : added automatically at the moment of their first purchase
--   file_import         : added from a spreadsheet in 2021, so the join date is not meaningful
--   not_on_list         : not currently subscribed
DROP VIEW IF EXISTS buyer_paths;
CREATE VIEW buyer_paths AS
SELECT
    b.customer_id,
    b.first_paid_time,
    b.paid_orders,
    b.total_spend,
    s.optin_time_utc,
    julianday(b.first_paid_time) - julianday(s.optin_time_utc) AS days_to_first_purchase,
    CASE
        WHEN s.customer_id IS NULL THEN 'not_on_list'
        WHEN s.source = 'file_import' THEN 'file_import'
        WHEN julianday(b.first_paid_time) - julianday(s.optin_time_utc) > 1.0 / 24 THEN 'joined_list_first'
        ELSE 'joined_at_checkout'
    END AS path
FROM buyers AS b
LEFT JOIN subscribers AS s USING (customer_id);
