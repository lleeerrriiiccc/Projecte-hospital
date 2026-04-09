-- Dades de prova per a hosp_blanes
-- Executar sobre la base de dades ja creada

USE hospital_proves;

-- PERSONAL
INSERT INTO personal (
	id_intern,
	nom,
	cognom,
	cognom2,
	data_naixement,
	telefon,
	telefon2,
	email,
	email_intern,
	dni,
	tipus_feina,
	data_alta
) VALUES
(1, 'Anna', 'Roca', 'Serra', '1982-03-14', '600111222', '972111222', 'anna.roca@hospital.cat', 'anna.roca@intern.hospital.cat', '12345678A', 'administracio', '2024-01-10'),
(2, 'Jordi', 'Vidal', 'Puig', '1976-08-02', '600111223', '972111223', 'jordi.vidal@hospital.cat', 'jordi.vidal@intern.hospital.cat', '23456789B', 'metge', '2022-05-12'),
(3, 'Marta', 'Soler', 'Vives', '1980-11-21', '600111224', '972111224', 'marta.soler@hospital.cat', 'marta.soler@intern.hospital.cat', '34567890C', 'metge', '2021-09-01'),
(4, 'Pere', 'Pons', 'Marti', '1988-06-30', '600111225', '972111225', 'pere.pons@hospital.cat', 'pere.pons@intern.hospital.cat', '45678901D', 'enfermeria', '2023-02-15'),
(5, 'Laura', 'Font', 'Riera', '1991-09-18', '600111226', '972111226', 'laura.font@hospital.cat', 'laura.font@intern.hospital.cat', '56789012E', 'resident', '2024-09-01');

-- METGE
INSERT INTO metge (id_intern, especialitat, cv) VALUES
(2, 'Cardiologia', '/cv/jordi_vidal.pdf'),
(3, 'Traumatologia', '/cv/marta_soler.pdf');

-- ENFERMER
INSERT INTO enfermer (id_intern) VALUES
(4);

-- PACIENT
INSERT INTO pacient (
	id_pacient,
	nom,
	cognom,
	cognom2,
	data_naixement,
	identificador
) VALUES
(1, 'Marc', 'Garcia', 'Lopez', '1995-04-10', 'P-2026-0001'),
(2, 'Nuria', 'Martinez', 'Sanz', '2001-12-22', 'P-2026-0002'),
(3, 'Albert', 'Casas', 'Torres', '1987-07-19', 'P-2026-0003');

-- USUARI
INSERT INTO usuari (
	id_usuari,
	nom_usuari,
	contrasenya_hash,
	rol,
	id_intern,
	id_pacient,
	actiu,
	data_creacio,
	ultim_acces
) VALUES
(1, 'admin.hospital', '$2b$12$adminhashdemo0000000000000000000000000000000000000000', 'administrador', 1, NULL, TRUE, '2026-04-01 08:00:00', '2026-04-09 08:00:00'),
(2, 'jvidal', '$2b$12$jvidalhashdemo000000000000000000000000000000000000000', 'personal', 2, NULL, TRUE, '2026-04-01 08:05:00', '2026-04-09 08:15:00'),
(3, 'msoler', '$2b$12$msolerhashdemo000000000000000000000000000000000000000', 'personal', 3, NULL, TRUE, '2026-04-01 08:10:00', NULL),
(4, 'ppons', '$2b$12$pponshashdemo0000000000000000000000000000000000000000', 'personal', 4, NULL, TRUE, '2026-04-01 08:20:00', '2026-04-09 07:40:00'),
(5, 'lfont', '$2b$12$lfonthashdemo0000000000000000000000000000000000000000', 'personal', 5, NULL, TRUE, '2026-04-01 08:25:00', NULL),
(6, 'marc.garcia', '$2b$12$marcgarciahashdemo00000000000000000000000000000000000', 'pacient', NULL, 1, TRUE, '2026-04-02 10:00:00', '2026-04-08 19:20:00'),
(7, 'nuria.martinez', '$2b$12$nuriamartinezhashdemo000000000000000000000000000000000', 'pacient', NULL, 2, TRUE, '2026-04-02 10:05:00', NULL),
(8, 'albert.casas', '$2b$12$albertcasashashdemo0000000000000000000000000000000000', 'pacient', NULL, 3, FALSE, '2026-04-02 10:10:00', NULL);

-- PLANTA
INSERT INTO planta (id_planta, nom) VALUES
(1, 'Urgencies'),
(2, 'Hospitalitzacio Nord'),
(3, 'Bloc Quirurgic');

-- HABITACIO
INSERT INTO habitacio (id_planta, num_habitacio) VALUES
(1, '101'),
(1, '102'),
(2, '201'),
(2, '202');

-- MEDICAMENT
INSERT INTO medicament (id_medicament, descripcio) VALUES
(1, 'Paracetamol 1g'),
(2, 'Amoxicilina 500mg'),
(3, 'Ibuprofeno 600mg'),
(4, 'Omeprazol 20mg'),
(5, 'Salbutamol inhalador');

-- QUIROFAN
INSERT INTO quirofan (id_quirofan, id_planta) VALUES
(1, 3),
(2, 3);

-- MAQUINES
INSERT INTO maquina (id_maquina, nom, descripcio) VALUES
(1, 'Monitor multiparametric', 'Monitoritza constants vitals'),
(2, 'Respirador', 'Assistencia respiratoria'),
(3, 'Bisturi electrico', 'Tall i cauteritzacio'),
(4, 'Bomba d''infusio', 'Administracio controlada de fluid'),
(5, 'Desfibrilador', 'Intervencio en emergencies cardiaques');

-- VISITA
INSERT INTO visita (id_visita, id_pacient, id_metge, data_visita, hora_visita) VALUES
(1, 1, 2, '2026-04-05', '09:00:00'),
(2, 2, 3, '2026-04-06', '11:30:00'),
(3, 3, 2, '2026-04-07', '16:15:00'),
(4, 1, 3, '2026-04-09', '08:45:00');

-- RECEPTA
INSERT INTO recepta (id_visita, id_medicament) VALUES
(1, 1),
(1, 3),
(2, 2),
(3, 4),
(4, 1),
(4, 5);

-- OPERACIO
INSERT INTO operacio (
	id_operacio,
	id_quirofan,
	id_pacient,
	data_operacio,
	hora_operacio,
	procediment
) VALUES
(1, 1, 1, '2026-04-08', '08:30:00', 'Apendicectomia'),
(2, 2, 3, '2026-04-09', '13:00:00', 'Artroscopia de genoll'),
(3, 1, 2, '2026-04-10', '10:15:00', 'Cirurgia menor');

-- ASSISTEIX
INSERT INTO assisteix (id_operacio, id_intern) VALUES
(1, 2),
(1, 4),
(2, 3),
(2, 4),
(3, 2),
(3, 5);

-- INVENTARI
INSERT INTO inventari (id_quirofan, id_maquina) VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 2),
(2, 4),
(2, 5);

-- RESERVA_HABITACIO
INSERT INTO reserva_habitacio (id_pacient, num_habitacio, data_inici, data_fi) VALUES
(1, '201', '2026-04-05', '2026-04-10'),
(1, '202', '2026-04-11', '2026-04-15'),
(2, '202', '2026-04-06', '2026-04-09'),
(3, '101', '2026-04-07', '2026-04-12');

-- SUPERVISIO
INSERT INTO supervisio (id_intern, id_metge) VALUES
(4, 2),
(5, 2);
