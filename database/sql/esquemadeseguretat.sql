-- Matriu de seguretat
-- - Es mantenen dos usuaris tècnics de PostgreSQL.
-- - Es creen rols de login per a cada tipus de persona i rols de grup per agrupar permisos.
-- - Els rols de login es creen amb el prefix rol_ per no xocar amb els rols de grup.
-- - Els usuaris reals de l'aplicació es guarden a la taula usuaris.
-- - El backend en Python continua usant un usuari tècnic propi.

-- Rols de PostgreSQL que es creen:
-- 1) hosp_admin: administra tota la base de dades.
-- 2) hosp_app: usuari tècnic que farà servir l'aplicació web.
-- 3) administrador, personal, sanitari, gestio, serveis i pacient: rols de grup.
-- 4) rol_administrador, rol_metge, rol_infermer, rol_administratiu, rol_tecnic,
--    rol_personal_neteja, rol_personal_seguretat, rol_personal_cuina i rol_pacient:
--    rols de login amb contrasenya d'exemple P@ssw0rd.

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

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'administrador') THEN
		CREATE ROLE administrador NOLOGIN;
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'personal') THEN
		CREATE ROLE personal NOLOGIN;
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sanitari') THEN
		CREATE ROLE sanitari NOLOGIN;
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gestio') THEN
		CREATE ROLE gestio NOLOGIN;
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'serveis') THEN
		CREATE ROLE serveis NOLOGIN;
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pacient') THEN
		CREATE ROLE pacient NOLOGIN;
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_administrador') THEN
		CREATE ROLE rol_administrador LOGIN PASSWORD 'P@ssw0rd';
	ELSE
		ALTER ROLE rol_administrador LOGIN PASSWORD 'P@ssw0rd';
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_metge') THEN
		CREATE ROLE rol_metge LOGIN PASSWORD 'P@ssw0rd';
	ELSE
		ALTER ROLE rol_metge LOGIN PASSWORD 'P@ssw0rd';
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_infermer') THEN
		CREATE ROLE rol_infermer LOGIN PASSWORD 'P@ssw0rd';
	ELSE
		ALTER ROLE rol_infermer LOGIN PASSWORD 'P@ssw0rd';
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_administratiu') THEN
		CREATE ROLE rol_administratiu LOGIN PASSWORD 'P@ssw0rd';
	ELSE
		ALTER ROLE rol_administratiu LOGIN PASSWORD 'P@ssw0rd';
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_tecnic') THEN
		CREATE ROLE rol_tecnic LOGIN PASSWORD 'P@ssw0rd';
	ELSE
		ALTER ROLE rol_tecnic LOGIN PASSWORD 'P@ssw0rd';
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_personal_neteja') THEN
		CREATE ROLE rol_personal_neteja LOGIN PASSWORD 'P@ssw0rd';
	ELSE
		ALTER ROLE rol_personal_neteja LOGIN PASSWORD 'P@ssw0rd';
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_personal_seguretat') THEN
		CREATE ROLE rol_personal_seguretat LOGIN PASSWORD 'P@ssw0rd';
	ELSE
		ALTER ROLE rol_personal_seguretat LOGIN PASSWORD 'P@ssw0rd';
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_personal_cuina') THEN
		CREATE ROLE rol_personal_cuina LOGIN PASSWORD 'P@ssw0rd';
	ELSE
		ALTER ROLE rol_personal_cuina LOGIN PASSWORD 'P@ssw0rd';
	END IF;

	IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_pacient') THEN
		CREATE ROLE rol_pacient LOGIN PASSWORD 'P@ssw0rd';
	ELSE
		ALTER ROLE rol_pacient LOGIN PASSWORD 'P@ssw0rd';
	END IF;
END
$$;

GRANT CONNECT ON DATABASE hosp_blanes TO hosp_admin, hosp_app,
	rol_administrador, rol_metge, rol_infermer, rol_administratiu, rol_tecnic,
	rol_personal_neteja, rol_personal_seguretat, rol_personal_cuina, rol_pacient;
GRANT USAGE, CREATE ON SCHEMA public TO hosp_admin;
GRANT USAGE ON SCHEMA public TO hosp_app,
	rol_administrador, rol_metge, rol_infermer, rol_administratiu, rol_tecnic,
	rol_personal_neteja, rol_personal_seguretat, rol_personal_cuina, rol_pacient;

-- Administració tècnica total.
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hosp_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hosp_admin;

-- Perfil funcional d'administrador.
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO administrador;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO administrador;

-- Perfil funcional de personal.
GRANT SELECT ON TABLE
	personal,
	planta,
	habitacio,
	medicament,
	quirofan,
	maquina
TO personal;

-- Perfil funcional sanitari.
GRANT SELECT, INSERT, UPDATE ON TABLE
	personal,
	metge,
	enfermer,
	pacient,
	visita,
	recepta,
	operacio,
	assisteix,
	supervisio
TO sanitari;

GRANT SELECT ON TABLE
	planta,
	habitacio,
	medicament,
	quirofan,
	maquina,
	inventari,
	reserva_habitacio
TO sanitari;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sanitari;

-- Perfil funcional de gestió.
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
	inventari,
	reserva_habitacio
TO gestio;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gestio;

-- Perfil funcional de serveis.
GRANT SELECT ON TABLE
	planta,
	habitacio,
	quirofan,
	maquina,
	inventari
TO serveis;

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

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT ALL PRIVILEGES ON TABLES TO administrador;

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT ALL PRIVILEGES ON SEQUENCES TO administrador;

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT SELECT ON TABLES TO personal;

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT SELECT, INSERT, UPDATE ON TABLES TO sanitari;

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT USAGE, SELECT ON SEQUENCES TO sanitari;

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT SELECT, INSERT, UPDATE ON TABLES TO gestio;

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT USAGE, SELECT ON SEQUENCES TO gestio;

ALTER DEFAULT PRIVILEGES FOR ROLE hosp_admin IN SCHEMA public
	GRANT SELECT ON TABLES TO serveis;

-- Matriu funcional de l'aplicació:
-- administrador: accés total dins de l'aplicació.
-- personal: accés base de lectura a dades comunes.
-- sanitari: metges i infermers.
-- gestio: administratius i tècnics.
-- serveis: personal de neteja, seguretat i cuina.
-- pacient: rol preparat per a un accés restringit amb vistes o RLS.
-- Els rols funcionals existeixen a PostgreSQL i els rols de login s'assignen als grups corresponents.

GRANT administrador TO rol_administrador;
GRANT personal TO rol_metge, rol_infermer, rol_administratiu, rol_tecnic,
	rol_personal_neteja, rol_personal_seguretat, rol_personal_cuina;
GRANT sanitari TO rol_metge, rol_infermer;
GRANT gestio TO rol_administratiu, rol_tecnic;
GRANT serveis TO rol_personal_neteja, rol_personal_seguretat, rol_personal_cuina;
GRANT pacient TO rol_pacient;

COMMIT;
