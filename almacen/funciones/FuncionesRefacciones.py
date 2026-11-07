def RegistrarRefaccion(ConexionDB,CodigoBarras,Articulo,NumParte,Marca,Categoria,Precio,Minimo,Ubicacion):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        INSERT INTO refaccion (codigobarras,articulo,num_parte,marca,categoria,precio,minimo,ubicacion)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING codigo;
        ''',(CodigoBarras,Articulo,NumParte,Marca,Categoria,Precio,Minimo,Ubicacion))

        CodigoRefaccion = Cursor.fetchone()[0]

        return CodigoRefaccion

def BuscarRefaccion(ConexionDB,Buscador):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        SELECT * FROM refaccion WHERE (codigo = %s) OR (codigobarras = %s);
        ''',(Buscador,Buscador))

        Refaccion = Cursor.fetchone()

    return Refaccion

def GetCantidad(ConexionDB,Buscador):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        SELECT existencia FROM refaccion WHERE (codigo = %s) OR (codigobarras = %s);
        ''',(Buscador,Buscador))

        CantidadActual = Cursor.fetchone()

    return CantidadActual

def GetMinimo(ConexionDB,Buscador):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        SELECT minimo FROM refaccion WHERE codigo = %s;
        ''',(Buscador,))

        Minimo = Cursor.fetchone()

    return Minimo[0]

def AltaRefacción(ConexionDB,CodigoBarras,Cantidad):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        UPDATE refaccion SET existencia = existencia + %s WHERE codigobarras = %s RETURNING codigo, existencia
        ''',(Cantidad,CodigoBarras))

        Refaccion = Cursor.fetchone()
        CodigoRefaccion = Refaccion[0]
        CantidadActual = Refaccion[1]

    return CodigoRefaccion,CantidadActual

def BajaRefacción(ConexionDB,CodigoBarras,Cantidad):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        UPDATE refaccion SET existencia = existencia - %s WHERE codigobarras = %s RETURNING codigo, existencia
        ''',(Cantidad,CodigoBarras))

        Refaccion = Cursor.fetchone()
        CodigoRefaccion = Refaccion[0]
        CantidadActual = Refaccion[1]

    return CodigoRefaccion,CantidadActual

def ActualizarEstado(ConexionDB,Codigo,EstadoNuevo):
    with ConexionDB.cursor() as Cursor:
        Cursor.execute('''
        UPDATE refaccion SET estado = %s WHERE codigo = %s RETURNING codigo;
        ''',(EstadoNuevo,Codigo))

        CodigoRefaccion = Cursor.fetchone()[0]

    return CodigoRefaccion