SELECT
    pl.id_planta,
    pl.nom AS planta,
    COUNT(DISTINCT h.num_habitacio) AS habitacions,
    COUNT(DISTINCT q.id_quirofan) AS quirofans,
    COUNT(DISTINCT aip.id_intern) AS infermeres
FROM planta pl
LEFT JOIN habitacio h ON h.id_planta = pl.id_planta
LEFT JOIN quirofan q ON q.id_planta = pl.id_planta
LEFT JOIN assignacio_infermer_planta aip ON aip.id_planta = pl.id_planta
GROUP BY pl.id_planta, pl.nom
ORDER BY pl.id_planta;