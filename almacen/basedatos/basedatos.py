import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
def ObtenerConexion():
    return psycopg.connect(
        host=os.getenv("DB_HOST","localhost"),
        port=os.getenv("DB_PORT","5432"),
        dbname=os.getenv("DB_NAME","almacen_dev"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def InicializarBD():
    with ObtenerConexion() as Conexion:
        with open("almacen/basedatos/schema.sql","r",encoding="utf-8") as Archivo:
            SQL = Archivo.read()

        with Conexion.cursor() as Cursor:
            Cursor.execute(SQL)

def CargarDatosPrueba():
    with ObtenerConexion() as Conexion:
        with open("almacen/basedatos/refaccionesprueba.sql","r",encoding="utf-8") as Archivo:
            SQL = Archivo.read()

        with Conexion.cursor() as Cursor:
            Cursor.execute(SQL)