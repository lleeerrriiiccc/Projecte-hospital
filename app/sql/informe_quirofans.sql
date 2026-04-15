SELECT
    q.id_quirofan,
    o.id_operacio,
    o.data_operacio,
    o.hora_operacio,
    o.procediment,

    CONCAT(p.nom, ' ', p.cognom) AS pacient_nom,

    CONCAT(per_m.nom, ' ', per_m.cognom) AS metge_complet,

    CONCAT(per_i.nom, ' ', per_i.cognom) AS infermer_complet

FROM operacio o
JOIN quirofan q ON o.id_quirofan = q.id_quirofan
JOIN pacient p ON o.id_pacient = p.id_pacient

LEFT JOIN assisteix a ON a.id_operacio = o.id_operacio
LEFT JOIN personal per_i ON per_i.id_intern = a.id_intern

JOIN assisteix am ON am.id_operacio = o.id_operacio
JOIN metge m ON m.id_intern = am.id_intern
JOIN personal per_m ON per_m.id_intern = m.id_intern

ORDER BY q.id_quirofan, o.hora_operacio;