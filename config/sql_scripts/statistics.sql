-- Количество выполненных заявок
SELECT COUNT(*) as completed_count
FROM requests_request
WHERE requestStatus = 'Выполнена';

-- Среднее время ремонта в днях
SELECT AVG(julianday(completionDate) - julianday(startDate)) as avg_days
FROM requests_request
WHERE requestStatus = 'Выполнена' AND completionDate IS NOT NULL;

-- Статистика по типам неисправностей
SELECT homeTechType, COUNT(*) as count
FROM requests_request
GROUP BY homeTechType
ORDER BY count DESC;

-- Статистика по мастерам
SELECT 
    u.fio as master_name,
    COUNT(r.requestID) as total_requests,
    SUM(CASE WHEN r.requestStatus = 'Выполнена' THEN 1 ELSE 0 END) as completed
FROM users_user u
LEFT JOIN requests_request r ON u.id = r.master_id
WHERE u.user_type = 'Мастер'
GROUP BY u.id, u.fio;