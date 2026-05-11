SELECT
    m.id_intern,
    CONCAT(m.nom, ' ', m.cognom, ' ', m.cognom2) AS metge,
    COUNT(DISTINCT v.id_pacient) AS pacients_atesos,
    COUNT(*) AS total_visites
FROM visita v
JOIN personal m ON m.id_intern = v.id_metge
GROUP BY m.id_intern, m.nom, m.cognom, m.cognom2
ORDER BY pacients_atesos DESC, total_visites DESC, metge;