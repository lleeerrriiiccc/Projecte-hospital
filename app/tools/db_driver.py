import psycopg2
from dotenv import load_dotenv
import os
import crypt as c



def connect():
    load_dotenv()
    db_host = os.getenv("DB_HOST")
    db_database = os.getenv("DB_DATABASE")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    con = psycopg2.connect(
        host=db_host,
        database=db_database,
        user=db_user,
        password=db_password
    )
    cursor = con.cursor()
    return con, cursor

def init_db():
    con, cur = connect()
    with open("base_de_dades/implementacio.sql", "r") as f:
        sql = f.read()
        cur.execute(sql)
    con.commit()
    cur.close()
    con.close()

def new_user(username, password, id_intern):
    con, cur = connect()
    password = c.encrypt_password(password)
    cur.execute("INSERT INTO usuaris (username, password, id_intern) VALUES (%s, %s, %s)", (username, password, id_intern))
    con.commit()
    cur.close()
    con.close()

