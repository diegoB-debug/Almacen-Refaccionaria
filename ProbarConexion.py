from almacen.basedatos.basedatos import ObtenerConexion

try:
    with ObtenerConexion() as Conexion:
        with Conexion.cursor() as Cursor:
            Cursor.execute("SELECT version();")
            print("Conectado a PostgreSQL")
            print(Cursor.fetchone()[0])
except Exception as Error:
    print("Conexión fallida:")
    print(Error)