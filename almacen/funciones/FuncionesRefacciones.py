def RegistrarRefaccion(ConexionDB,CodigoBarras,Articulo,NumParte,Marca,Categoria,Precio,Minimo,Ubicacion):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        INSERT INTO refaccion (codigobarras,articulo,num_parte,marca,categoria,precio,minimo,ubicacion)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING codigo;
        ''',(CodigoBarras,Articulo,NumParte,Marca,Categoria,Precio,Minimo,Ubicacion))

        SkuRefaccion = Cursor.fetchone()[0]

        return SkuRefaccion

def BuscarRefaccion(ConexionDB,Buscador):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        SELECT * FROM refaccion WHERE (codigo = %s) OR (codigobarras = %s)
        ''',(Buscador,Buscador))

        Refaccion = Cursor.fetchone()

    return Refaccion