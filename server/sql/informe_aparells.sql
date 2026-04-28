SELECT
    q.id_quirofan,
    pl.nom AS planta,
    COALESCE(
        STRING_AGG(
            m.nom || ' · ' || m.descripcio,
            ', ' ORDER BY m.nom
        ),
        'Sense aparells'
    ) AS maquinari
FROM quirofan q
JOIN planta pl ON pl.id_planta = q.id_planta
LEFT JOIN inventari i ON i.id_quirofan = q.id_quirofan
LEFT JOIN maquina m ON m.id_maquina = i.id_maquina
GROUP BY q.id_quirofan, pl.nom
ORDER BY q.id_quirofan;


