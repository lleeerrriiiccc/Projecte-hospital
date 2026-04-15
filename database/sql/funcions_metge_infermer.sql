-- Active: 1776089592306@@172.25.128.226@5432@hosp_blanes
CREATE OR REPLACE FUNCTION afegir_metge(nom text, cognom text, cognom2 text, data_naixement date, telefon text, telefon2 text, email text, email_intern text, dni text, tipus_feina text, data_alta date, especialitat text, cv text)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    id_intern_query integer;
BEGIN
    INSERT INTO personal (nom, cognom, cognom2, data_naixement, telefon, telefon2, email, email_intern, dni, tipus_feina, data_alta)
    VALUES (nom, cognom, cognom2, data_naixement, telefon, telefon2, email, email_intern, dni, tipus_feina, data_alta)
    RETURNING id_intern INTO id_intern_query;

    INSERT INTO metge (id_intern, especialitat, cv) VALUES (id_intern_query, especialitat, cv);

END;
$$;


CREATE OR REPLACE FUNCTION afegir_infermer(nom text, cognom text, cognom2 text, data_naixement date, telefon text, telefon2 text, email text, email_intern text, dni text, tipus_feina text, data_alta date, mresp integer)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    id_intern_query integer;
BEGIN
    INSERT INTO personal (nom, cognom, cognom2, data_naixement, telefon, telefon2, email, email_intern, dni, tipus_feina, data_alta)
    VALUES (nom, cognom, cognom2, data_naixement, telefon, telefon2, email, email_intern, dni, tipus_feina, data_alta)
    RETURNING id_intern INTO id_intern_query;

    INSERT INTO supervisio (id_intern, id_metge) VALUES (id_intern_query, mresp);

END;
$$;
