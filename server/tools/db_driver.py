import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql


BASE_DIR = Path(__file__).resolve().parent

ROLE_BY_JOB_TYPE = {
    "administrador": "rol_administrador",
    "metge": "rol_metge",
    "infermer": "rol_infermer",
    "administratiu": "rol_administratiu",
    "tecnic": "rol_tecnic",
    "personal neteja": "rol_personal_neteja",
    "personal seguretat": "rol_personal_seguretat",
    "personal cuina": "rol_personal_cuina",
    "pacient": "rol_pacient",
}


def _role_exists(cursor, role_name):
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (role_name,))
    return cursor.fetchone() is not None


def _resolve_db_role(cursor, username):
    if _role_exists(cursor, username):
        return username

    cursor.execute(
        """
        SELECT p.tipus_feina
        FROM usuaris u
        JOIN personal p ON p.id_intern = u.id_intern
        WHERE LOWER(u.username) = LOWER(%s)
        """,
        (username,),
    )
    row = cursor.fetchone()

    if row is None:
        raise ValueError(f"User '{username}' does not exist in the database.")

    job_type = str(row[0] or "").strip().lower()
    role_name = ROLE_BY_JOB_TYPE.get(job_type)

    if not role_name:
        raise ValueError(f"No database role mapping found for job type '{row[0]}'.")

    if not _role_exists(cursor, role_name):
        raise ValueError(f"Database role '{role_name}' does not exist.")

    return role_name



############
# CONNECTION TO DB
############
def connect(username="default"):
    load_dotenv()
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_database = os.getenv("DB_DATABASE")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_sslmode = os.getenv("DB_SSLMODE", "prefer")
    con = None
    try:
        con = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_database,
            user=db_user,
            password=db_password,
            sslmode=db_sslmode,
        )
        cursor = con.cursor()

        if username is None or username == "default":
            return con, cursor

        role_name = _resolve_db_role(cursor, username)
        cursor.execute(sql.SQL("SET ROLE {}").format(sql.Identifier(role_name)))
        return con, cursor
    except Exception:
        if con is not None:
            con.close()
        raise



############
# INIT DB
############
def init_db():
    con, cur = connect()
    with open(BASE_DIR / ".." / ".." / "database" / "sql" / "implementacio.sql", "r") as f:
        sql = f.read()
        cur.execute(sql)
    con.commit()
    cur.close()
    con.close()


