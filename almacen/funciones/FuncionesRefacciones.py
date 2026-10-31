def RegistrarRefaccion(ConexionDB,CodigoBarras,Nombre,NumParte,Modelo,Yr,Desc,LinkImg):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        INSERT INTO refaccion (codigobarras,nombre,num_parte,modelo,yr,descr,url_imagen)
        VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING sku;
        ''',(CodigoBarras,Nombre,NumParte,Modelo,Yr,Desc,LinkImg))

        SkuRefaccion = Cursor.fetchone()[0]

        return SkuRefaccion

def BuscarRefaccion(ConexionDB,Buscador):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        SELECT * FROM refaccion WHERE sku = %s
        ''',(Buscador,))

        Refaccion = Cursor.fetchone()

    return Refaccion