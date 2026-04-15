-- =========================
-- PERSONAL (base de todo el sistema)
-- =========================
INSERT INTO personal (
    nom, cognom, cognom2, data_naixement,
    telefon, telefon2,
    email, email_intern,
    dni, tipus_feina, data_alta
) VALUES
-- Médicos
('Albert', 'Puig', 'Serra', '1975-03-12', '600111222', '600111223',
 'albert.puig@gmail.com', 'apuig@hosp.local',
 '12345678A', 'metge', '2015-01-10'),

('Núria', 'Ribas', 'Casas', '1980-06-22', '600222333', '600222334',
 'nuria.ribas@gmail.com', 'nribas@hosp.local',
 '23456789B', 'metge', '2016-05-20'),

('David', 'López', 'Martí', '1988-11-01', '600333444', '600333445',
 'david.lopez@gmail.com', 'dlopez@hosp.local',
 '34567890C', 'metge', '2018-09-15'),

('Laia', 'Vila', 'Ferrer', '1990-02-14', '600444555', '600444556',
 'laia.vila@gmail.com', 'lvila@hosp.local',
 '45678901D', 'metge', '2020-03-01');


-- =========================
-- PACIENTS
-- =========================
INSERT INTO pacient (nom, cognom, cognom2, data_naixement, identificador) VALUES
('Joan', 'Martí', 'Pujol', '1985-04-12', 'ID123456A'),
('Maria', 'Serra', 'Vidal', '1992-09-23', 'ID234567B'),
('Pere', 'Soler', 'Garcia', '1978-01-05', 'ID345678C'),
('Anna', 'Ferrer', 'Closa', '2000-07-18', 'ID456789D'),
('Marc', 'Roca', 'Tarrés', '1995-11-30', 'ID567890E');


-- =========================
-- METGES
-- (ahora referencian personal.id_intern)
-- =========================
INSERT INTO metge (id_intern, especialitat, cv) VALUES
(46, 'Cardiologia', 'Experiència en unitat coronària i intervencionisme'),
(47, 'Pediatria', 'Atenció neonatal i pediàtrica general'),
(48, 'Traumatologia', 'Cirurgia ortopèdica i lesions esportives'),
(49, 'Dermatologia', 'Tractaments dermatològics avançats');


-- =========================
-- VISITES
-- =========================
INSERT INTO visita (id_pacient, id_metge, data_visita, hora_visita) VALUES
(1, 39, '2026-04-10', '09:00'),
(2, 45, '2026-04-10', '09:30'),
(3, 49, '2026-04-11', '10:00'),
(4, 39, '2026-04-11', '10:30'),
(5, 46, '2026-04-12', '11:00'),
(1, 46, '2026-04-12', '11:30'),
(2, 49, '2026-04-13', '12:00');