CREATE OR REPLACE FUNCTION create_con_rol()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE 
    tipus_feina_t VARCHAR;
BEGIN

    SELECT tipus_feina 
    INTO tipus_feina_t 
    FROM personal 
    WHERE id_intern = NEW.id_intern;

    CASE tipus_feina_t
        WHEN 'administrador' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT rol_administrador TO %I', NEW.username);

        WHEN 'metge' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT rol_metge TO %I', NEW.username);

        WHEN 'infermer' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT rol_infermer TO %I', NEW.username);

        WHEN 'administratiu' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT rol_administratiu TO %I', NEW.username);

        WHEN 'tecnic' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT rol_tecnic TO %I', NEW.username);

        WHEN 'personal neteja' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT rol_personal_neteja TO %I', NEW.username);

        WHEN 'personal seguretat' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT rol_personal_seguretat TO %I', NEW.username);

        WHEN 'personal cuina' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT rol_personal_cuina TO %I', NEW.username);

        WHEN 'pacient' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT rol_pacient TO %I', NEW.username);
        ELSE
            RAISE EXCEPTION 'Tipus de feina desconegut: %', tipus_feina_t;
    END CASE;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trigger_create_con_rol
AFTER INSERT ON usuaris
FOR EACH ROW
EXECUTE FUNCTION create_con_rol();





CREATE OR REPLACE FUNCTION public.create_con_rol()
RETURNS trigger AS
$$
DECLARE
    v_role TEXT;
    role_exists BOOLEAN;
BEGIN
    SELECT tipus_feina INTO v_role FROM personal WHERE id_intern = NEW.id_intern;
    -- 🔴 Validaciones
    IF NEW.username IS NULL OR NEW.password IS NULL THEN
        RAISE EXCEPTION 'Username o password no pueden ser NULL';
    END IF;

    IF v_role IS NULL THEN
        RAISE EXCEPTION 'tipus_feina no puede ser NULL para usuario %', NEW.username;
    END IF;

    -- 🔵 comprobar si el role existe
    SELECT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = NEW.username
    ) INTO role_exists;

    -- 🔵 crear role si no existe
    IF NOT role_exists THEN
        EXECUTE format(
            'CREATE ROLE %I LOGIN PASSWORD %L',
            NEW.username,
            NEW.password
        );
    END IF;

    -- 🔵 mapear tipo de trabajo
    v_role := CASE v_role
        WHEN 'metge' THEN 'rol_metge'
        WHEN 'infermer' THEN 'rol_infermer'
        WHEN 'administratiu' THEN 'rol_administratiu'
        WHEN 'tecnic' THEN 'rol_tecnic'
        WHEN 'personal neteja' THEN 'rol_personal_neteja'
        WHEN 'personal seguretat' THEN 'rol_personal_seguretat'
        WHEN 'personal cuina' THEN 'rol_personal_cuina'
        WHEN 'pacient' THEN 'rol_pacient'
        WHEN 'administrador' THEN 'rol_administrador'
        ELSE NULL
    END;

    IF v_role IS NULL THEN
        RAISE EXCEPTION 'Tipus de feina desconegut: %', v_role;
    END IF;

    -- 🔵 asignar rol
    EXECUTE format(
        'GRANT %I TO %I',
        v_role,
        NEW.username
    );

    RETURN NEW;

END;
$$ LANGUAGE plpgsql;