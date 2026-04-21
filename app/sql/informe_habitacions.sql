SELECT
    rh.num_habitacio,
    rh.data_inici,
    rh.data_fi,
    CONCAT(p.nom, ' ', p.cognom, ' ', p.cognom2) AS nom_complet_pacient
FROM reserva_habitacio rh
JOIN pacient p ON rh.id_pacient = p.id_pacient
WHERE rh.num_habitacio = %s
ORDER BY rh.data_inici, rh.data_fi;