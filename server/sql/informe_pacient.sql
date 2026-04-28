WITH informe AS (
    SELECT
        'visita' AS tipus,
        v.data_visita AS data_event,
        v.hora_visita AS hora_event,
        v.diagnostic AS descripcio,
        NULL::text AS info_extra
    FROM visita v
    WHERE v.id_pacient = %s

    UNION ALL

    SELECT
        'operacio' AS tipus,
        o.data_operacio AS data_event,
        o.hora_operacio AS hora_event,
        o.procediment AS descripcio,
        NULL::text AS info_extra
    FROM operacio o
    WHERE o.id_pacient = %s

    UNION ALL

    SELECT
        'medicament' AS tipus,
        v.data_visita AS data_event,
        v.hora_visita AS hora_event,
        m.descripcio AS descripcio,
        NULL::text AS info_extra
    FROM recepta r
    JOIN visita v ON v.id_visita = r.id_visita
    JOIN medicament m ON m.id_medicament = r.id_medicament
    WHERE v.id_pacient = %s

    UNION ALL

    SELECT
        'reserva_habitacio' AS tipus,
        rh.data_inici AS data_event,
        NULL::time AS hora_event,
        rh.num_habitacio AS descripcio,
        rh.data_fi::text AS info_extra
    FROM reserva_habitacio rh
    WHERE rh.id_pacient = %s
)
SELECT
    tipus,
    data_event,
    hora_event,
    descripcio,
    info_extra
FROM informe
ORDER BY data_event, hora_event NULLS LAST, tipus, descripcio;


