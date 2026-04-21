SELECT
    op.id_operacio,
    op.data_operacio,
    op.hora_operacio,
    op.procediment,
    CONCAT(p.nom, ' ', p.cognom, ' ', p.cognom2) AS nom_complet_pacient,
    CONCAT(pm.nom, ' ', pm.cognom, ' ', pm.cognom2) AS nom_complet_metge,
    STRING_AGG(
        CONCAT(pi.nom, ' ', pi.cognom, ' ', pi.cognom2),
        ', ' ORDER BY pi.cognom, pi.nom
    ) AS infermers_assistents
FROM operacio op
JOIN pacient p
    ON op.id_pacient = p.id_pacient
JOIN personal pm
    ON op.metge_responsable = pm.id_intern
LEFT JOIN assisteix a
    ON a.id_operacio = op.id_operacio
LEFT JOIN enfermer i
    ON i.id_intern = a.id_intern
LEFT JOIN personal pi
    ON pi.id_intern = i.id_intern
--WHERE op.data_operacio = %s
GROUP BY
    op.id_operacio,
    op.data_operacio,
    op.hora_operacio,
    op.procediment,
    p.nom, p.cognom, p.cognom2,
    pm.nom, pm.cognom, pm.cognom2
ORDER BY
    op.data_operacio,
    op.hora_operacio,
    op.id_operacio;