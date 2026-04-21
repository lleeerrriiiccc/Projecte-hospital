-- PLANTA
INSERT INTO planta (nom) VALUES
('Urgències'),
('Cirurgia'),
('UCI');

-- PERSONAL
INSERT INTO personal 
(nom, cognom, cognom2, data_naixement, telefon, telefon2, email, email_intern, dni, tipus_feina, data_alta)
VALUES
('Marc', 'Serra', 'Pujol', '1985-04-12', '600111222', '600333444', 'marc.serra@gmail.com', 'm.serra@hospital.local', '11111111A', 'metge', '2020-01-10'),
('Laura', 'Vila', 'Roca', '1990-09-22', '600222333', '600444555', 'laura.vila@gmail.com', 'l.vila@hospital.local', '22222222B', 'enfermer', '2021-03-15'),
('Jordi', 'Ferrer', 'Solé', '1978-11-05', '600555666', '600777888', 'jordi.ferrer@gmail.com', 'j.ferrer@hospital.local', '33333333C', 'metge', '2018-07-01');

-- METGE / ENFERMER
INSERT INTO metge VALUES
(1, 'Cardiologia', 'CV_Marc.pdf'),
(3, 'Traumatologia', 'CV_Jordi.pdf');

INSERT INTO enfermer VALUES
(2);

-- PACIENT
INSERT INTO pacient (nom, cognom, cognom2, data_naixement, identificador)
VALUES
('Anna', 'Martí', 'Clara', '2001-02-10', 'PAC001'),
('Pere', 'Navarro', 'Gomez', '1975-06-18', 'PAC002');

-- HABITACIO
INSERT INTO habitacio VALUES
(1, 'U01'),
(1, 'U02'),
(2, 'C01');

-- MEDICAMENT
INSERT INTO medicament (descripcio) VALUES
('Paracetamol 1g'),
('Ibuprofèn 600mg'),
('Amoxicil·lina 500mg');

-- QUIROFAN
INSERT INTO quirofan (id_planta) VALUES
(2),
(3);

-- MAQUINA
INSERT INTO maquina (nom, descripcio) VALUES
('Monitor cardíac', 'Control de constants vitals'),
('Ventilador', 'Suport respiratori'),
('Desfibril·lador', 'Emergències cardíaques');

-- VISITA
INSERT INTO visita (id_pacient, id_metge, data_visita, hora_visita) VALUES
(1, 1, '2026-04-10', '10:30'),
(2, 3, '2026-04-11', '12:00');

-- RECEPTA
INSERT INTO recepta VALUES
(1, 1),
(1, 2),
(2, 3);

-- OPERACIO
INSERT INTO operacio (id_quirofan, id_pacient, data_operacio, hora_operacio, procediment, metge_responsable) VALUES
(1, 1, '2026-04-12', '09:00', 'Apendicectomia', 1),
(2, 2, '2026-04-13', '11:00', 'Artroscòpia', 3);

-- ASSISTEIX
INSERT INTO assisteix VALUES
(1, 1),
(1, 2),
(2, 3);

-- INVENTARI
INSERT INTO inventari VALUES
(1, 1),
(1, 2),
(2, 3);

-- RESERVA HABITACIO
INSERT INTO reserva_habitacio VALUES
(1, 'U01', '2026-04-10', '2026-04-15'),
(2, 'C01', '2026-04-11', '2026-04-20');

-- SUPERVISIO
INSERT INTO supervisio VALUES
(2, 1),
(2, 3);

-- USUARIS
INSERT INTO usuaris (username, password, id_intern, rol) VALUES
('mserra', 'hashed_password_1', 1, 'metge'),
('lvila', 'hashed_password_2', 2, 'enfermer'),
('jferrer', 'hashed_password_3', 3, 'metge');

