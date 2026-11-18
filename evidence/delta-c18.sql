-- Delta query, TD 2 Step 2 (wrong consensus C18): rows the reference counts but the two faulty queries (north-mini, dots) miss.
-- Both require (order_year - birth_year) = 25 AND birthday already reached. They drop customers whose year gap is 26
-- but whose birthday has not yet occurred in the order year: their completed age is still 25.
SELECT c.customer_id, c.birth_date,
       SUM(o.quantity_product * p.price) AS delta_cents   -- revenue excluding VAT, in euro cents
FROM orders o
JOIN product p   ON p.product_id   = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.date >= '2026-05-01 00:00:00' AND o.date < '2026-06-01 00:00:00'
  AND CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 26
  AND strftime('%m-%d', o.date) < strftime('%m-%d', c.birth_date)   -- birthday not yet reached => completed age is 25
GROUP BY c.customer_id;
-- Expected: C004 (2000-09-25) 11940 + C022 (2000-08-14) 10960 = 22900 = 62480 (reference) - 39580 (faulty value).

-- Same root cause for C16 (120b + dots, 211260 vs reference 376740, gap 165480): the faulty queries force year gap = 25.
-- Delta for C16 (age on 2026-09-25, products a,b,c, all orders): customers born in 2000 after 09-25.
SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS delta_cents
FROM orders o
JOIN product p   ON p.product_id   = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.product_id IN ('a','b','c')
  AND 2026 - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 26
  AND strftime('%m-%d', '2026-09-25') < strftime('%m-%d', c.birth_date)
GROUP BY c.customer_id;
