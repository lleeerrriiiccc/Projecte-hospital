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
    EXECUTE format('GRANT %I TO hosp_app', NEW.username);
    RETURN NEW;
END;
$$;


CREATE OR REPLACE TRIGGER trigger_create_con_rol
AFTER INSERT ON usuaris
FOR EACH ROW
EXECUTE FUNCTION create_con_rol();





