-- Matriu de seguretat
-- - Només es creen usuaris tècnics de PostgreSQL.
-- - Els usuaris reals de l'aplicació es guarden a la taula usuaris.
-- - L'administració general es fa amb un usuari tècnic des de pgAdmin o psql.
-- - El backend en Python usa un usuari tècnic propi.

-- Usuaris de PostgreSQL que es creen:
-- 1) hosp_admin: administra tota la base de dades.
-- 2) hosp_app: usuari tècnic que farà servir l'aplicació web.

BEGIN;

REVOKE CONNECT ON DATABASE hosp_blanes FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;

DO $$
BEGIN
	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hosp_admin') THEN
		CREATE ROLE hosp_admin LOGIN CREATEDB CREATEROLE PASSWORD 'P@ssw0rd!';
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hosp_app') THEN
		CREATE ROLE hosp_app LOGIN PASSWORD 'P@ssw0rd!app';
	END IF;
END
$$;

GRANT CONNECT ON DATABASE hosp_blanes TO hosp_admin, hosp_app;
GRANT USAGE, CREATE ON SCHEMA public TO hosp_admin;
GRANT USAGE ON SCHEMA public TO hosp_app;

-- Administració tècnica total.
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hosp_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hosp_admin;

-- Permisos del backend.
-- El backend necessita llegir i modificar dades, però no fer DDL.
GRANT SELECT, INSERT, UPDATE ON TABLE
	personal,
	metge,
	enfermer,
	pacient,
	planta,
	habitacio,
	medicament,
	quirofan,
	maquina,
	visita,
	recepta,
	operacio,
	assisteix,
	inventari,
	reserva_habitacio,
	supervisio,
	usuaris
TO hosp_app;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO hosp_app;

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT SELECT, INSERT, UPDATE ON TABLES TO hosp_app;

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT USAGE, SELECT ON SEQUENCES TO hosp_app;

-- Matriu funcional de l'aplicació:
-- administrador: accés total dins de l'aplicació.
-- personal: accés a pacients, visites, receptes, operacions i reserves.
-- pacient: accés només a la seva pròpia informació.
-- Aquests rols es controlen en Python fent servir la taula usuaris, no com a rols de PostgreSQL.

COMMIT;
