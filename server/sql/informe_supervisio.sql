SELECT 
    CONCAT(m.nom, ' ', m.cognom, ' ', m.cognom2) AS metge,
    STRING_AGG(
        CONCAT(e.nom, ' ', e.cognom, ' ', e.cognom2),
        ', '
        ORDER BY e.cognom, e.nom
    ) AS infermeres
FROM supervisio s
JOIN personal m 
    ON m.id_intern = s.id_metge
JOIN personal e 
    ON e.id_intern = s.id_intern
GROUP BY m.id_intern, m.nom, m.cognom, m.cognom2

UNION ALL

SELECT
    NULL AS metge,
    STRING_AGG(
        CONCAT(e.nom, ' ', e.cognom, ' ', e.cognom2),
        ', '
        ORDER BY e.cognom, e.nom
    ) AS infermeres
FROM personal e
LEFT JOIN supervisio s 
    ON s.id_intern = e.id_intern
WHERE e.tipus_feina = 'infermer' AND s.id_metge IS NULL;


--HE CREAT UN INDEX PER MILLORAR LA EFICIENCIA --> CREATE INDEX personal_tipus_feina ON personal(tipus_feina);