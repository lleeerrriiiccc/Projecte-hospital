import tools.crypt as c
import tools.db_driver as db


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