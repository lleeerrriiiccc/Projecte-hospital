SELECT 
    CONCAT(p.nom, ' ', p.cognom, ' ', p.cognom2) AS pacient,
    CONCAT(m.nom, ' ', m.cognom, ' ', m.cognom2) AS metge,
    v.hora_visita
FROM visita v
JOIN pacient p ON p.id_pacient = v.id_pacient
JOIN personal m ON m.id_intern = v.id_metge
WHERE v.data_visita = %s
ORDER BY v.hora_visita;