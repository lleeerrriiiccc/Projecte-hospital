import tools.crypt as c
import tools.db_driver as db
import requests


############
# LOGIN FUNCTION
############
def login(username, password):
    con, cur = db.connect()
    cur.execute("SELECT password FROM usuaris WHERE username = %s", (username,))
    result = cur.fetchone()

    if result is None:
        error = "El nom d'usuari no existeix. Revisa les dades e intenta-ho de nou."
        return False, error

    cur.close()
    con.close()

    stored_password = result[0]

    if c.check_password(password, stored_password) == True:
        return True, None

    error = "Contrasenya incorrecte. Revisa les dades e intenta-ho de nou."
    return False, error


############
# REGISTER FUNCTION
############
def register(username, password, id_intern):
    con, cur = db.connect()

    try:
        cur.execute("SELECT 1 FROM personal WHERE id_intern = %s", (id_intern,))
        if cur.fetchone() is None:
            return False, "El id intern no existeix"

        cur.execute("SELECT 1 FROM usuaris WHERE username = %s", (username,))
        if cur.fetchone() is not None:
            return False, "El nom d'usuari ja existeix. Tria un altre."

        hashed_password = c.encrypt_password(password)
        cur.execute(
            "INSERT INTO usuaris (username, password, id_intern) VALUES (%s, %s, %s)",
            (username, hashed_password, id_intern),
        )
        con.commit()

        return True, None

    except Exception:
        con.rollback()
        return False, "No s'ha pogut registrar l'usuari. Revisa les dades i torna-ho a intentar."

    finally:
        cur.close()
        con.close()



############
# NEW PACIENT FUNCTION
############
def new_pacient(name, surename, surename2, birth_date, ident):
    con, cur = db.connect()

    try:
        query = """
            INSERT INTO pacient (nom, cognom, cognom2, data_naixement, identificador)
            VALUES (%s, %s, %s, %s, %s)
        """

        cur.execute(query, (name, surename, surename2, birth_date, ident))
        con.commit()

        return True, None

    except Exception:
        con.rollback()
        return False, "No s'ha pogut donar d'alta el pacient. Revisa si l'identificador ja existeix."

    finally:
        cur.close()
        con.close()



############
# NEW EMPLOYEE FUNCTION
############
def new_employee(
    name,
    surename,
    surename2,
    birthdate,
    phone,
    phone2,
    email,
    email_intern,
    dni,
    tfeina,
    data_alta_str,
    especialitat=None,
    cv=None,
    mresp=None
):
    con, cur = db.connect()

    try:
        match tfeina:
            case 'metge':
                if not especialitat or not cv:
                    return False, "Per donar d'alta un metge, has de proporcionar una especialitat i un CV."

                query = """
                    SELECT afegir_metge(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    name,
                    surename,
                    surename2,
                    birthdate,
                    phone,
                    phone2,
                    email,
                    email_intern,
                    dni,
                    tfeina,
                    data_alta_str,
                    especialitat,
                    cv,
                )

            case 'infermer':
                if not mresp:
                    query = """
                        INSERT INTO personal (
                            nom, cognom, cognom2, data_naixement,
                            telefon, telefon2, email, email_intern,
                            dni, tipus_feina, data_alta
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        name,
                        surename,
                        surename2,
                        birthdate,
                        phone,
                        phone2,
                        email,
                        email_intern,
                        dni,
                        tfeina,
                        data_alta_str
                    )
                else:
                    query = """
                        SELECT afegir_infermer(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        name,
                        surename,
                        surename2,
                        birthdate,
                        phone,
                        phone2,
                        email,
                        email_intern,
                        dni,
                        tfeina,
                        data_alta_str,
                        mresp,
                    )

            case _:
                if especialitat or cv:
                    return False, "Només els metges poden tenir una especialitat i un CV."

                query = """
                    INSERT INTO personal (
                        nom, cognom, cognom2, data_naixement,
                        telefon, telefon2, email, email_intern,
                        dni, tipus_feina, data_alta
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    name,
                    surename,
                    surename2,
                    birthdate,
                    phone,
                    phone2,
                    email,
                    email_intern,
                    dni,
                    tfeina,
                    data_alta_str,
                )

        cur.execute(query, params)

        con.commit()
        return True, None

    except Exception as e:
        con.rollback()
        return False, f"Error: {str(e)}"

    finally:
        cur.close()
        con.close()


def get_metges():
    con, cur = db.connect()

    try:
        query = "SELECT id_intern, CONCAT(nom, ' ', cognom) AS nom_complet FROM personal WHERE tipus_feina = 'metge'"
        cur.execute(query)
        metges = cur.fetchall()
        return metges

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        cur.close()
        con.close()



def get_informes_supervisio():
    con, cur = db.connect()

    try:
        with open("app/sql/informe_supervisio.sql", "r") as f:
            sql = f.read()
        cur.execute(sql)
        informes = cur.fetchall()
        return informes

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        cur.close()
        con.close()

