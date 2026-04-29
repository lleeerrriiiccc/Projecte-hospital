import tools.crypt as c
import tools.db_driver as db
import psycopg2
from psycopg2 import errors
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


############
# GESTIÓ D'ERRORS DE BASE DE DADES
############
def handle_db_error(e, con):
    if con is not None:
        con.rollback()

    if isinstance(e, ValueError):
        return False, str(e)

    if isinstance(e, errors.InsufficientPrivilege):
        return False, "No tens permís per realitzar aquesta acció."

    if isinstance(e, errors.UniqueViolation):
        return False, "Ja existeix un registre amb aquestes dades."

    if isinstance(e, errors.ForeignKeyViolation):
        return False, "Error de relació amb altres dades."

    if isinstance(e, psycopg2.Error):
        msg = None
        if getattr(e, "diag", None) is not None:
            msg = getattr(e.diag, "message_primary", None)
        if not msg:
            msg = e.pgerror
        return False, f"Error de base de dades: {(msg or str(e)).strip()}"

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
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


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
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


############
# NEW PACIENT FUNCTION
############
def new_pacient(name, surename, surename2, birth_date, ident, username):
    con = None
    cur = None

    try:
        con, cur = db.connect(username=username)
        cur.execute(
            """
            INSERT INTO pacient (nom, cognom, cognom2, data_naixement, identificador)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, surename, surename2, birth_date, ident)
        )
        con.commit()
        return True, None

    except Exception as e:
        return handle_db_error(e, con)

    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


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

        if tfeina == 'metge':
            if not especialitat or not cv:
                return False, "Falten especialitat o CV."
            query = "SELECT afegir_metge(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = (
                name, surename, surename2, birthdate,
                phone, phone2, email, email_intern,
                dni, tfeina, data_alta_str, especialitat, cv
            )

        elif tfeina == 'infermer':
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

        else:
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
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


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
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


############
# GET INFORMES
############
def get_informes(informe, params=None, username=None):
    con = None
    cur = None

    try:
        con, cur = db.connect(username=username)

        sql_file = BASE_DIR / ".." / "sql" / f"informe_{informe}.sql"
        with open(sql_file, encoding="utf-8") as f:
            sql = f.read()

        if params:
            if not isinstance(params, (tuple, list)):
                params = (params,)
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        rows = cur.fetchall()

        if informe == 'supervisio':
            return True, rows

        if informe == 'visites':
            result = []
            for row in rows:
                result.append({
                    "pacient": row[0],
                    "metge": row[1],
                    "hora_visita": str(row[2]),
                })
            return True, result

        if informe == 'quirofans':
            result = []
            for row in rows:
                result.append({
                    "id_operacio": row[0],
                    "data_operacio": str(row[1]),
                    "hora_operacio": str(row[2]),
                    "procediment": row[3],
                    "pacient": row[4],
                    "metge": row[5],
                    "infermers_assistents": row[6],
                })
            return True, result

        if informe == 'habitacions':
            result = []
            for row in rows:
                result.append({
                    "num_habitacio": row[0],
                    "data_inici": str(row[1]),
                    "data_fi": str(row[2]),
                    "pacient": row[3],
                })
            return True, result

        if informe == 'metge':
            result = []
            for row in rows:
                result.append({
                    "tipus": row[0],
                    "data": str(row[1]),
                    "hora": str(row[2]),
                    "pacient": row[3],
                    "metge": row[4],
                    "detall": row[5],
                })
            return True, result

        if informe == 'pacient':
            result = []
            for row in rows:
                result.append({
                    "tipus": row[0],
                    "data_event": str(row[1]),
                    "hora_event": str(row[2]) if row[2] is not None else None,
                    "descripcio": row[3],
                    "info_extra": row[4],
                })
            return True, result

        if informe == 'aparells':
            result = []
            for row in rows:
                result.append({
                    "id_quirofan": row[0],
                    "planta": row[1],
                    "maquinari": row[2],
                })
            return True, result

        return True, rows

    except Exception as e:
        return handle_db_error(e, con)

    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


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
        result = []
        for row in rows:
            result.append({"num_habitacio": row[0]})
        return True, result

    except Exception as e:
        ok, msg = handle_db_error(e, con)
        return ok, msg

    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


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
        result = []
        for row in rows:
            result.append({"id_pacient": row[0], "nom_complet": row[1]})
        return True, result

    except Exception as e:
        ok, msg = handle_db_error(e, con)
        return ok, msg

    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


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


def _execute_write(query, params, username=None):
    con = None
    cur = None

    try:
        con, cur = _connect_for_user(username)
        cur.execute(query, params)
        con.commit()
        return True, None
    except Exception as e:
        return handle_db_error(e, con)
    finally:
        _close_db(con, cur)


def _fetch_rows(query, params=None, username=None):
    con = None
    cur = None

    try:
        con, cur = _connect_for_user(username)
        cur.execute(query, params or ())
        return True, cur.fetchall()
    except Exception as e:
        ok, msg = handle_db_error(e, con)
        return ok, msg
    finally:
        _close_db(con, cur)


def _read_report_sql(report_name):
    report_file = BASE_DIR / ".." / "sql" / f"informe_{report_name}.sql"
    with open(report_file, encoding="utf-8") as sql_file:
        return sql_file.read()


############
# LOGIN FUNCTION
############
def login(username, password):
    con = None
    cur = None

    try:
        con, cur = _connect_for_user()
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
        con, cur = _connect_for_user()
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
    query = """
        INSERT INTO pacient (nom, cognom, cognom2, data_naixement, identificador)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (name, surename, surename2, birth_date, ident)
    return _execute_write(query, params, username=username)


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
        con, cur = _connect_for_user(username)
        if tfeina == 'metge':
            if not especialitat or not cv:
                return False, "Falten especialitat o CV."

            query = "SELECT afegir_metge(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = (
                name, surename, surename2, birthdate,
                phone, phone2, email, email_intern,
                dni, tfeina, data_alta_str,
                especialitat, cv
            )
        elif tfeina == 'infermer':
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
        else:
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
    query = """
        SELECT id_intern, CONCAT(nom, ' ', cognom)
        FROM personal WHERE tipus_feina = 'metge'
    """
    return _fetch_rows(query, username=username)


############
# GET INFORMES
############
def get_informes(informe, params=None, username=None):
    con = None
    cur = None

    try:
        con, cur = _connect_for_user(username)
        sql = _read_report_sql(informe)

        if params:
            if not isinstance(params, (tuple, list)):
                params = (params,)
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        rows = cur.fetchall()

        if informe == 'supervisio':
            return True, rows

        if informe == 'visites':
            result = []
            for row in rows:
                result.append({
                    "pacient": row[0],
                    "metge": row[1],
                    "hora_visita": str(row[2]),
                })
            return True, result

        if informe == 'quirofans':
            result = []
            for row in rows:
                result.append({
                    "id_operacio": row[0],
                    "data_operacio": str(row[1]),
                    "hora_operacio": str(row[2]),
                    "procediment": row[3],
                    "pacient": row[4],
                    "metge": row[5],
                    "infermers_assistents": row[6],
                })
            return True, result

        if informe == 'habitacions':
            result = []
            for row in rows:
                result.append({
                    "num_habitacio": row[0],
                    "data_inici": str(row[1]),
                    "data_fi": str(row[2]),
                    "pacient": row[3],
                })
            return True, result

        if informe == 'metge':
            result = []
            for row in rows:
                result.append({
                    "tipus": row[0],
                    "data": str(row[1]),
                    "hora": str(row[2]),
                    "pacient": row[3],
                    "metge": row[4],
                    "detall": row[5],
                })
            return True, result

        if informe == 'pacient':
            result = []
            for row in rows:
                hora_event = None
                if row[2] is not None:
                    hora_event = str(row[2])

                result.append({
                    "tipus": row[0],
                    "data_event": str(row[1]),
                    "hora_event": hora_event,
                    "descripcio": row[3],
                    "info_extra": row[4],
                })
            return True, result

        if informe == 'aparells':
            result = []
            for row in rows:
                result.append({
                    "id_quirofan": row[0],
                    "planta": row[1],
                    "maquinari": row[2],
                })
            return True, result

        return True, rows

    except Exception as e:
        return handle_db_error(e, con)

    finally:
        _close_db(con, cur)



############
# GET HABITACIONS
############
def get_habitacions(username=None):
    query = """
        SELECT num_habitacio
        FROM habitacio
        ORDER BY num_habitacio
    """
    ok, rows = _fetch_rows(query, username=username)
    if not ok:
        return ok, rows

    result = []
    for row in rows:
        result.append({"num_habitacio": row[0]})

    return True, result


############
# GET PACIENTS
############
def get_pacients(username=None):
    query = """
        SELECT id_pacient, CONCAT(nom, ' ', cognom, ' ', cognom2)
        FROM pacient
        ORDER BY cognom, cognom2, nom
    """
    ok, rows = _fetch_rows(query, username=username)
    if not ok:
        return ok, rows

    result = []
    for row in rows:
        result.append({"id_pacient": row[0], "nom_complet": row[1]})

    return True, result