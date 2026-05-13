SELECT
    v.id_visita,
    v.data_visita,
    CONCAT(m.nom, ' ', m.cognom, ' ', m.cognom2) AS metge,
    p.id_pacient,
    p.nom,
    p.cognom,
    p.cognom2
FROM visita v
JOIN pacient p ON p.id_pacient = v.id_pacient
JOIN personal m ON m.id_intern = v.id_metge
WHERE v.data_visita BETWEEN %s AND %s
ORDER BY v.data_visita, v.hora_visita, v.id_visita;