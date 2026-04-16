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
        WHEN 'Administrador' THEN
            EXECUTE format('CREATE ROLE %I WITH PASSWORD %L', NEW.username, NEW.password);
            EXECUTE format('GRANT Administrador TO %I', NEW.username);

        WHEN 'Gestor' THEN
            INSERT INTO con_rol (id_intern, rol) 
            VALUES (NEW.id_intern, 'Gestor');

        WHEN 'Usuari' THEN
            INSERT INTO con_rol (id_intern, rol) 
            VALUES (NEW.id_intern, 'Usuari');
    END CASE;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trigger_create_con_rol
AFTER INSERT ON usuaris
FOR EACH ROW
EXECUTE FUNCTION create_con_rol();