import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
def ObtenerConexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST","localhost"),
        port=os.getenv("DB_PORT","5432"),
        dbname=os.getenv("DB_NAME","almacen_dev"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )