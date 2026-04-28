import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql


BASE_DIR = Path(__file__).resolve().parent



############
# CONNECTION TO DB
############
def connect(username="default"):
    load_dotenv()
    db_host = os.getenv("DB_HOST")
    db_database = os.getenv("DB_DATABASE")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_sslmode = os.getenv("DB_SSLMODE", "prefer")
    con = None
    try:
        con = psycopg2.connect(
            host=db_host,
            database=db_database,
            user=db_user,
            password=db_password,
            sslmode=db_sslmode,
        )
        cursor = con.cursor()

        if username == "default":
            return con, cursor

        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (username,))
        if cursor.fetchone() is None:
            raise ValueError(f"User '{username}' does not exist in the database.")

        cursor.execute(sql.SQL("SET ROLE {}").format(sql.Identifier(username)))
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


