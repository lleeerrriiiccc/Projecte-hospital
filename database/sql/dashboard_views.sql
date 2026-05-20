-- Vistes analitiques per al dashboard de Power BI.
-- Es mantenen dins de public per no obrir canvis d'esquema addicionals.

CREATE OR REPLACE VIEW vw_dashboard_visites_area_dia AS
SELECT
    v.data_visita,
    COALESCE(m.especialitat, 'Sense especialitat') AS area,
    COUNT(*) AS total_visites,
    COUNT(DISTINCT v.id_pacient) AS pacients_unics,
    COUNT(DISTINCT v.id_metge) AS metges_actius
FROM visita v
LEFT JOIN metge m
    ON m.id_intern = v.id_metge
GROUP BY
    v.data_visita,
    COALESCE(m.especialitat, 'Sense especialitat');


CREATE OR REPLACE VIEW vw_dashboard_visites_metge_dia AS
SELECT
    v.data_visita,
    v.id_metge,
    CONCAT(p.nom, ' ', p.cognom, ' ', p.cognom2) AS metge_nom,
    COALESCE(m.especialitat, 'Sense especialitat') AS area,
    COUNT(*) AS total_visites,
    COUNT(DISTINCT v.id_pacient) AS pacients_unics
FROM visita v
JOIN personal p
    ON p.id_intern = v.id_metge
LEFT JOIN metge m
    ON m.id_intern = v.id_metge
GROUP BY
    v.data_visita,
    v.id_metge,
    p.nom,
    p.cognom,
    p.cognom2,
    COALESCE(m.especialitat, 'Sense especialitat');


CREATE OR REPLACE VIEW vw_dashboard_visites_franja_dia AS
SELECT
    v.data_visita,
    CASE
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 0 AND 5 THEN 1
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 6 AND 11 THEN 2
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 12 AND 17 THEN 3
        ELSE 4
    END AS franja_ordre,
    CASE
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 0 AND 5 THEN '00-05'
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 6 AND 11 THEN '06-11'
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 12 AND 17 THEN '12-17'
        ELSE '18-23'
    END AS franja_horaria,
    COUNT(*) AS total_visites
FROM visita v
GROUP BY
    v.data_visita,
    CASE
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 0 AND 5 THEN 1
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 6 AND 11 THEN 2
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 12 AND 17 THEN 3
        ELSE 4
    END,
    CASE
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 0 AND 5 THEN '00-05'
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 6 AND 11 THEN '06-11'
        WHEN EXTRACT(HOUR FROM v.hora_visita) BETWEEN 12 AND 17 THEN '12-17'
        ELSE '18-23'
    END;


CREATE OR REPLACE VIEW vw_dashboard_ocupacio_habitacions_dia AS
SELECT DISTINCT
    gs.data_servei::date AS data_servei,
    h.id_planta,
    pl.nom AS planta,
    rh.num_habitacio,
    TRUE AS ocupada,
    rh.id_pacient
FROM reserva_habitacio rh
JOIN habitacio h
    ON h.num_habitacio = rh.num_habitacio
JOIN planta pl
    ON pl.id_planta = h.id_planta
CROSS JOIN LATERAL generate_series(rh.data_inici, rh.data_fi, interval '1 day') AS gs(data_servei);


CREATE OR REPLACE VIEW vw_dashboard_quirofans_dia AS
SELECT
    op.data_operacio,
    q.id_planta,
    pl.nom AS planta,
    op.id_quirofan,
    COUNT(*) AS total_operacions,
    COUNT(DISTINCT op.id_pacient) AS pacients_unics,
    COUNT(DISTINCT op.metge_responsable) AS metges_responsables
FROM operacio op
JOIN quirofan q
    ON q.id_quirofan = op.id_quirofan
JOIN planta pl
    ON pl.id_planta = q.id_planta
GROUP BY
    op.data_operacio,
    q.id_planta,
    pl.nom,
    op.id_quirofan;


CREATE OR REPLACE VIEW vw_dashboard_malalties_dia AS
SELECT
    v.data_visita,
    COALESCE(m.nom, 'Sense malaltia informada') AS malaltia,
    COUNT(*) AS total_visites,
    COUNT(DISTINCT v.id_pacient) AS pacients_afectats
FROM visita v
LEFT JOIN malaltia m
    ON m.id_malaltia = v.id_malaltia
GROUP BY
    v.data_visita,
    COALESCE(m.nom, 'Sense malaltia informada');


CREATE OR REPLACE VIEW vw_dashboard_planta_recursos AS
SELECT
    pl.id_planta,
    pl.nom AS planta,
    COUNT(DISTINCT h.num_habitacio) AS total_habitacions,
    COUNT(DISTINCT q.id_quirofan) AS total_quirofans,
    COUNT(DISTINCT aip.id_intern) AS total_infermers_assignats
FROM planta pl
LEFT JOIN habitacio h
    ON h.id_planta = pl.id_planta
LEFT JOIN quirofan q
    ON q.id_planta = pl.id_planta
LEFT JOIN assignacio_infermer_planta aip
    ON aip.id_planta = pl.id_planta
GROUP BY
    pl.id_planta,
    pl.nom;


CREATE OR REPLACE VIEW vw_dashboard_visites_detall AS
SELECT
    v.id_visita,
    v.data_visita,
    v.hora_visita,
    v.id_metge,
    CONCAT(p.nom, ' ', p.cognom, ' ', p.cognom2) AS metge_nom,
    COALESCE(m.especialitat, 'Sense especialitat') AS area,
    v.id_pacient,
    v.id_malaltia,
    v.diagnostic
FROM visita v
JOIN personal p
    ON p.id_intern = v.id_metge
LEFT JOIN metge m
    ON m.id_intern = v.id_metge;