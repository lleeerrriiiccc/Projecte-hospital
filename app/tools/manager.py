import tools.crypt as c
import tools.db_driver as db
import psycopg2
from psycopg2 import errors


#############################
# HELPER DE ERRORES
#############################
def _close_db(con, cur):
    if cur is not None:
        cur.close()
    if con is not None:
        con.close()


def _db_error_message(e):
    if isinstance(e, psycopg2.Error):
        message = None
        if getattr(e, "diag", None) is not None:
            message = getattr(e.diag, "message_primary", None)
        if not message:
            message = e.pgerror
        return (message or str(e)).strip()
    return str(e).strip()


def handle_db_error(e, con):
    if con is not None:
        con.rollback()

    if isinstance(e, ValueError):
        return False, str(e)

    if isinstance(e, errors.InsufficientPrivilege):
        return False, f"No tens permís per realitzar aquesta acció."

    if isinstance(e, errors.UniqueViolation):
        return False, "Ja existeix un registre amb aquestes dades."

    if isinstance(e, errors.ForeignKeyViolation):
        return False, "Error de relació amb altres dades."

    if isinstance(e, psycopg2.Error):
        return False, f"Error de base de dades: {_db_error_message(e)}"

    return False, f"Error intern: {str(e)}"


############
# LOGIN FUNCTION
############
def login(username, password):
    con = None
    cur = None

    try:
        con, cur = db.connect()
        username = username.lower()
        cur.execute(
            "SELECT id_intern, password FROM usuaris WHERE username = %s",
            (username,)
        )
        result = cur.fetchone()

        if not result:
            return False, "El nom d'usuari no existeix.", None

        id_intern, stored_password = result

        if not stored_password:
            return False, "El nom d'usuari no existeix.", None

        if c.check_password(password, stored_password):
            cur.execute(
                "SELECT tipus_feina FROM personal WHERE id_intern = %s",
                (id_intern,)
            )
            tipus = cur.fetchone()[0]
            return True, None, tipus

        return False, "Contrasenya incorrecta.", None

    except Exception as e:
        ok, msg = handle_db_error(e, con)
        return ok, msg, None

    finally:
        _close_db(con, cur)


############
# REGISTER FUNCTION
############
def register(username, password, id_intern):
    con = None
    cur = None

    try:
        username = username.lower()
        con, cur = db.connect()
        cur.execute("SELECT 1 FROM personal WHERE id_intern = %s", (id_intern,))
        if cur.fetchone() is None:
            return False, "El id intern no existeix"

        cur.execute("SELECT 1 FROM usuaris WHERE username = %s", (username,))
        if cur.fetchone():
            return False, "El nom d'usuari ja existeix."

        hashed_password = c.encrypt_password(password)

        cur.execute(
            "INSERT INTO usuaris (username, password, id_intern) VALUES (%s, %s, %s)",
            (username, hashed_password, id_intern),
        )

        con.commit()
        return True, None

    except Exception as e:
        return handle_db_error(e, con)

    finally:
        _close_db(con, cur)


############
# NEW PACIENT FUNCTION
############
def new_pacient(name, surename, surename2, birth_date, ident, username):
    con = None
    cur = None

    try:
        con, cur = db.connect(username=username)
        cur.execute("""
            INSERT INTO pacient (nom, cognom, cognom2, data_naixement, identificador)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, surename, surename2, birth_date, ident))

        con.commit()
        return True, None

    except Exception as e:
        return handle_db_error(e, con)

    finally:
        _close_db(con, cur)


############
# NEW EMPLOYEE FUNCTION
############
def new_employee(
    name, surename, surename2, birthdate, phone, phone2,
    email, email_intern, dni, tfeina, data_alta_str,
    especialitat=None, cv=None, mresp=None, username=None
):
    con = None
    cur = None

    try:
        con, cur = db.connect(username=username)
        match tfeina:
            case 'metge':
                if not especialitat or not cv:
                    return False, "Falten especialitat o CV."

                query = "SELECT afegir_metge(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                params = (
                    name, surename, surename2, birthdate,
                    phone, phone2, email, email_intern,
                    dni, tfeina, data_alta_str,
                    especialitat, cv
                )

            case 'infermer':
                if not mresp:
                    query = """
                        INSERT INTO personal (
                            nom, cognom, cognom2, data_naixement,
                            telefon, telefon2, email, email_intern,
                            dni, tipus_feina, data_alta
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        name, surename, surename2, birthdate,
                        phone, phone2, email, email_intern,
                        dni, tfeina, data_alta_str
                    )
                else:
                    query = "SELECT afegir_infermer(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    params = (
                        name, surename, surename2, birthdate,
                        phone, phone2, email, email_intern,
                        dni, tfeina, data_alta_str, mresp
                    )

            case _:
                query = """
                    INSERT INTO personal (
                        nom, cognom, cognom2, data_naixement,
                        telefon, telefon2, email, email_intern,
                        dni, tipus_feina, data_alta
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    name, surename, surename2, birthdate,
                    phone, phone2, email, email_intern,
                    dni, tfeina, data_alta_str
                )

        cur.execute(query, params)
        con.commit()
        return True, None

    except Exception as e:
        return handle_db_error(e, con)

    finally:
        _close_db(con, cur)


############
# GET METGES
############
def get_metges(username=None):
    con = None
    cur = None

    try:
        con, cur = db.connect(username=username)
        cur.execute("""
            SELECT id_intern, CONCAT(nom, ' ', cognom)
            FROM personal WHERE tipus_feina = 'metge'
        """)
        return True, cur.fetchall()

    except Exception as e:
        ok, msg = handle_db_error(e, con)
        return ok, msg

    finally:
        _close_db(con, cur)


############
# GET INFORMES
############
def get_informes(informe, params=None, username=None):
    con = None
    cur = None

    try:
        con, cur = db.connect(username=username)
        with open(f"app/sql/informe_{informe}.sql") as f:
            sql = f.read()

        if params:
            if not isinstance(params, (tuple, list)):
                params = (params,)
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        rows = cur.fetchall()

        match informe:
            case 'supervisio':
                return True, rows

            case 'visites':
                return True, [
                    {"pacient": r[0], "metge": r[1], "hora_visita": str(r[2])}
                    for r in rows
                ]

            case 'quirofans':
                return True, [
                    {
                        "id_operacio": r[0],
                        "data_operacio": str(r[1]),
                        "hora_operacio": str(r[2]),
                        "procediment": r[3],
                        "pacient": r[4],
                        "metge": r[5],
                        "infermers_assistents": r[6],
                    }
                    for r in rows
                ]

            case 'habitacions':
                return True, [
                    {
                        "num_habitacio": r[0],
                        "data_inici": str(r[1]),
                        "data_fi": str(r[2]),
                        "pacient": r[3],
                    }
                    for r in rows
                ]

            case 'metge':
                return True, [
                    {
                        "tipus": r[0],
                        "data": str(r[1]),
                        "hora": str(r[2]),
                        "pacient": r[3],
                        "metge": r[4],
                        "detall": r[5],
                    }
                    for r in rows
                ]

            case 'pacient':
                return True, [
                    {
                        "tipus": r[0],
                        "data_event": str(r[1]),
                        "hora_event": str(r[2]) if r[2] is not None else None,
                        "descripcio": r[3],
                        "info_extra": r[4],
                    }
                    for r in rows
                ]

        return True, rows

    except Exception as e:
        return handle_db_error(e, con)

    finally:
        _close_db(con, cur)



############
# GET HABITACIONS
############
def get_habitacions(username=None):
    con = None
    cur = None

    try:
        con, cur = db.connect(username=username)
        cur.execute("""
            SELECT num_habitacio
            FROM habitacio
            ORDER BY num_habitacio
        """)
        rows = cur.fetchall()
        return True, [{"num_habitacio": r[0]} for r in rows]

    except Exception as e:
        ok, msg = handle_db_error(e, con)
        return ok, msg

    finally:
        _close_db(con, cur)


############
# GET PACIENTS
############
def get_pacients(username=None):
    con = None
    cur = None

    try:
        con, cur = db.connect(username=username)
        cur.execute("""
            SELECT id_pacient, CONCAT(nom, ' ', cognom, ' ', cognom2)
            FROM pacient
            ORDER BY cognom, cognom2, nom
        """)
        rows = cur.fetchall()
        return True, [
            {"id_pacient": r[0], "nom_complet": r[1]}
            for r in rows
        ]

    except Exception as e:
        ok, msg = handle_db_error(e, con)
        return ok, msg

    finally:
        _close_db(con, cur)