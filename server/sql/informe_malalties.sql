SELECT
    m.id_malaltia,
    m.nom AS malaltia,
    COUNT(*) AS total_visites,
    COUNT(DISTINCT v.id_pacient) AS pacients_afectats
FROM visita v
JOIN malaltia m ON m.id_malaltia = v.id_malaltia
GROUP BY m.id_malaltia, m.nom
ORDER BY total_visites DESC, malaltia;