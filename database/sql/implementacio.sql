
--PERSONAL
CREATE TABLE personal (
    id_intern SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    cognom VARCHAR(50) NOT NULL,
    cognom2 VARCHAR(50) NOT NULL,
    data_naixement DATE NOT NULL,
    telefon VARCHAR(15) NOT NULL,
    telefon2 VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL CHECK (email LIKE '%@%'),
    email_intern VARCHAR(100) NOT NULL CHECK (email_intern LIKE '%@%'),
    dni VARCHAR(20) NOT NULL UNIQUE,
    tipus_feina VARCHAR(50) NOT NULL,
    data_alta DATE NOT NULL
);

--METGE
CREATE TABLE metge (
    id_intern INT NOT NULL PRIMARY KEY,
    especialitat VARCHAR(50) NOT NULL,
    cv VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_intern) REFERENCES personal(id_intern)
);

--ENFERMER
CREATE TABLE enfermer (
    id_intern INT NOT NULL PRIMARY KEY,
    FOREIGN KEY (id_intern) REFERENCES personal(id_intern)
);

--PACIENT
CREATE TABLE pacient (
    id_pacient SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    cognom VARCHAR(50) NOT NULL,
    cognom2 VARCHAR(50) NOT NULL,
    data_naixement DATE NOT NULL,
    identificador VARCHAR(20) NOT NULL UNIQUE
);

--PLANTA
CREATE TABLE planta (
    id_planta SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL
);

--HABITACIO
CREATE TABLE habitacio (
    id_planta INT NOT NULL,
    num_habitacio VARCHAR(10) NOT NULL PRIMARY KEY,
    FOREIGN KEY (id_planta) REFERENCES planta(id_planta)
);

--MEDICAMENT
CREATE TABLE medicament (
    id_medicament SERIAL PRIMARY KEY,
    descripcio TEXT NOT NULL
);

--MALALTIA
CREATE TABLE malaltia (
    id_malaltia SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);

--QUIROFAN
CREATE TABLE quirofan (
    id_quirofan SERIAL PRIMARY KEY,
    id_planta INT NOT NULL,
    FOREIGN KEY (id_planta) REFERENCES planta(id_planta)
);

--MAQUINES
CREATE TABLE maquina (
    id_maquina SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    descripcio TEXT NOT NULL
);

--VISITA
CREATE TABLE visita (
    id_visita SERIAL PRIMARY KEY,
    id_pacient INT NOT NULL,
    id_metge INT NOT NULL,
    id_malaltia INT,
    data_visita DATE NOT NULL,
    hora_visita TIME NOT NULL,
    diagnostic TEXT NOT NULL,
    FOREIGN KEY (id_pacient) REFERENCES pacient(id_pacient),
    FOREIGN KEY (id_metge) REFERENCES metge(id_intern),
    FOREIGN KEY (id_malaltia) REFERENCES malaltia(id_malaltia)
);

--RECEPTA
CREATE TABLE recepta (
    id_visita INT NOT NULL,
    id_medicament INT NOT NULL,
    FOREIGN KEY (id_visita) REFERENCES visita(id_visita),
    FOREIGN KEY (id_medicament) REFERENCES medicament(id_medicament),
    PRIMARY KEY (id_visita, id_medicament)
);

--OPERACIO
CREATE TABLE operacio (
    id_operacio SERIAL PRIMARY KEY,
    id_quirofan INT NOT NULL,
    id_pacient INT NOT NULL,
    data_operacio DATE NOT NULL,
    hora_operacio TIME NOT NULL,
    procediment TEXT NOT NULL,
    metge_responsable INT NOT NULL,
    FOREIGN KEY (id_quirofan) REFERENCES quirofan(id_quirofan),
    FOREIGN KEY (id_pacient) REFERENCES pacient(id_pacient),
    FOREIGN KEY (metge_responsable) REFERENCES metge(id_intern)
);

--ASSISTEIX
CREATE TABLE assisteix (
    id_operacio INT NOT NULL,
    id_intern INT NOT NULL,
    FOREIGN KEY (id_operacio) REFERENCES operacio(id_operacio),
    FOREIGN KEY (id_intern) REFERENCES personal(id_intern),
    PRIMARY KEY (id_operacio, id_intern)
);

--Inventari
CREATE TABLE inventari (
    id_quirofan INT NOT NULL,
    id_maquina INT NOT NULL,
    FOREIGN KEY (id_maquina) REFERENCES maquina(id_maquina),
    FOREIGN KEY (id_quirofan) REFERENCES quirofan(id_quirofan),
    PRIMARY KEY (id_quirofan, id_maquina)
);

--RESERVA_HABITACIO
CREATE TABLE reserva_habitacio (
    id_pacient INT NOT NULL,
    num_habitacio VARCHAR(10) NOT NULL,
    data_inici DATE NOT NULL,
    data_fi DATE NOT NULL,
    FOREIGN KEY (id_pacient) REFERENCES pacient(id_pacient),
    FOREIGN KEY (num_habitacio) REFERENCES habitacio(num_habitacio),
    PRIMARY KEY (id_pacient, num_habitacio, data_inici)
);

--SUPERVISIO
CREATE TABLE supervisio (
    id_intern INT NOT NULL,
    id_metge INT NOT NULL,
    FOREIGN KEY (id_intern) REFERENCES personal(id_intern),
    FOREIGN KEY (id_metge) REFERENCES metge(id_intern),
    PRIMARY KEY (id_intern, id_metge)
);

--ASSIGNACIO_INFERMER_PLANTA
CREATE TABLE assignacio_infermer_planta (
    id_intern INT NOT NULL,
    id_planta INT NOT NULL,
    FOREIGN KEY (id_intern) REFERENCES enfermer(id_intern),
    FOREIGN KEY (id_planta) REFERENCES planta(id_planta),
    PRIMARY KEY (id_intern, id_planta)
);

--USUARIS
CREATE TABLE usuaris (
    id_user SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    id_intern INT NOT NULL,
    FOREIGN KEY (id_intern) REFERENCES personal(id_intern)
);

CREATE INDEX personal_tipus_feina ON personal(tipus_feina);

CREATE INDEX visita_data_visita ON visita(data_visita);
CREATE INDEX visita_id_malaltia ON visita(id_malaltia);

-- MIGRACIO DES DE LA VERSIO ACTUAL
-- Executa aquest bloc si ja tens la base de dades creada amb l'esquema anterior
-- i vols afegir la relacio entre infermers i plantes sense reconstruir-ho tot.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'assignacio_infermer_planta'
    ) THEN
        CREATE TABLE assignacio_infermer_planta (
            id_intern INT NOT NULL,
            id_planta INT NOT NULL,
            FOREIGN KEY (id_intern) REFERENCES enfermer(id_intern),
            FOREIGN KEY (id_planta) REFERENCES planta(id_planta),
            PRIMARY KEY (id_intern, id_planta)
        );
    END IF;
END $$;

-- MIGRACIO PER A LES MALALTIES
-- Executa aquest bloc si ja tens l'esquema anterior i vols convertir els
-- diagnòstics de les visites en una taula normalitzada de malalties.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'malaltia'
    ) THEN
        CREATE TABLE malaltia (
            id_malaltia SERIAL PRIMARY KEY,
            nom VARCHAR(100) NOT NULL UNIQUE
        );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'visita'
          AND column_name = 'id_malaltia'
    ) THEN
        ALTER TABLE visita ADD COLUMN id_malaltia INT;
    END IF;
END $$;

INSERT INTO malaltia (nom)
VALUES
    ('Grip'),
    ('Bronquitis'),
    ('Migranya')
ON CONFLICT (nom) DO NOTHING;

INSERT INTO malaltia (nom)
SELECT DISTINCT INITCAP(TRIM(diagnostic))
FROM visita
WHERE diagnostic IS NOT NULL AND TRIM(diagnostic) <> ''
ON CONFLICT (nom) DO NOTHING;

UPDATE visita v
SET id_malaltia = m.id_malaltia
FROM malaltia m
WHERE LOWER(TRIM(v.diagnostic)) = LOWER(TRIM(m.nom));

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_schema = 'public'
          AND table_name = 'visita'
          AND constraint_name = 'visita_id_malaltia_fkey'
    ) THEN
        ALTER TABLE visita
            ADD CONSTRAINT visita_id_malaltia_fkey
            FOREIGN KEY (id_malaltia) REFERENCES malaltia(id_malaltia);
    END IF;
END $$;
