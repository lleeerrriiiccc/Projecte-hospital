import psycopg2 
from dotenv import load_dotenv
import os



############
# CONNECTION TO DB
############
def connect(type="default"):
    load_dotenv()
    db_host = os.getenv("DB_HOST")
    db_database = os.getenv("DB_DATABASE")
    match type:
        case "default":
            db_user = os.getenv("DEFAULT_USER")
            db_password = os.getenv("DEFAULT_PASSWORD")
            con = psycopg2.connect(
                host=db_host,
                database=db_database,
                user=db_user,
                password=db_password
            )
            cursor = con.cursor()
            return con, cursor
        case "metge":
            db_user = os.getenv("METGE_USER")
            db_password = os.getenv("METGE_PASSWORD")
            con = psycopg2.connect(
                host=db_host,
                database=db_database,
                user=db_user,
                password=db_password
            )
            cursor = con.cursor()
            return con, cursor
        case _:
            raise ValueError("Invalid connection type. Use 'default' or 'test'.")



############
# INIT DB
############
def init_db():
    con, cur = main_connect()
    with open("base_de_dades/implementacio.sql", "r") as f:
        sql = f.read()
        cur.execute(sql)
    con.commit()
    cur.close()
    con.close()


