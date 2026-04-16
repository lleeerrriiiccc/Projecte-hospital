import psycopg2 
from dotenv import load_dotenv
import os



############
# CONNECTION TO DB
############
def connect(type="default"):
    load_dotenv()
    match type:
        case "default":
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
        case "test":
            return test_connect()
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


