SELECT
    v.data_visita,
    COUNT(*) AS total_visites
FROM visita v
WHERE v.data_visita BETWEEN %s AND %s
GROUP BY v.data_visita
ORDER BY v.data_visita;