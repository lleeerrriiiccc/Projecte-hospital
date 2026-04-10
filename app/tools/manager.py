import tools.db_driver as db
import tools.crypt as c



############
# LOGIN FUNCTION
############
def login(username, password):
    con, cur = db.connect()
    cur.execute("SELECT password FROM usuaris WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    con.close()
    if result is None:
        return False
    stored_password = result[0]
    return c.check_password(password, stored_password)


############
# REGISTER FUNCTION
############
def register(username, password, id_intern):
    con, cur = db.connect()
    try:
        cur.execute("SELECT 1 FROM personal WHERE id_intern = %s", (id_intern,))
        if cur.fetchone() is None:
            return False, "El id_intern no existe en personal."

        cur.execute("SELECT 1 FROM usuaris WHERE username = %s", (username,))
        if cur.fetchone() is not None:
            return False, "El nombre de usuario ya existe."

        hashed_password = c.encrypt_password(password)
        cur.execute(
            "INSERT INTO usuaris (username, password, id_intern) VALUES (%s, %s, %s)",
            (username, hashed_password, id_intern)
        )
        con.commit()
        return True, None
    except Exception:
        con.rollback()
        return False, "No se pudo registrar el usuario."
    finally:
        cur.close()
        con.close()