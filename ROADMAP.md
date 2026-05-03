Добавить для конверсии продаж
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN paid_credits > 0 THEN 1 END) as paid_users,
    ROUND(100.0 * COUNT(CASE WHEN paid_credits > 0 THEN 1 END) / COUNT(*), 1) as conversion_pct
FROM user_quota;