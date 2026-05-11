SELECT
    p.id_intern,
    CONCAT(p.nom, ' ', p.cognom, ' ', p.cognom2) AS nom_complet,
    p.tipus_feina,
    p.telefon,
    p.email,
    p.data_alta
FROM personal p
ORDER BY p.cognom, p.cognom2, p.nom;