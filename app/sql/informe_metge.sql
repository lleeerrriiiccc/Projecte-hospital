SELECT
    'visita' AS tipus,
    v.data_visita AS data,
    v.hora_visita AS hora,
    CONCAT(p.nom, ' ', p.cognom, ' ', p.cognom2) AS pacient,
    CONCAT(m.nom, ' ', m.cognom, ' ', m.cognom2) AS metge,
    'Visita programada' AS detall
FROM visita v
JOIN pacient p ON p.id_pacient = v.id_pacient
JOIN personal m ON m.id_intern = v.id_metge
WHERE v.id_metge = %s AND v.data_visita = %s

UNION ALL

SELECT
    'operacio' AS tipus,
    op.data_operacio AS data,
    op.hora_operacio AS hora,
    CONCAT(p.nom, ' ', p.cognom, ' ', p.cognom2) AS pacient,
    CONCAT(m.nom, ' ', m.cognom, ' ', m.cognom2) AS metge,
    op.procediment AS detall
FROM operacio op
JOIN pacient p ON p.id_pacient = op.id_pacient
JOIN personal m ON m.id_intern = op.metge_responsable
WHERE op.metge_responsable = %s AND op.data_operacio = %s

ORDER BY hora, tipus;