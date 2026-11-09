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

def ActualizarInfo(ConexionDB,Codigo,DatosACambiar):
    with ConexionDB.cursor() as Cursor:
        Columnas= ', '.join(f"{Columna} = %s" for Columna in DatosACambiar)
        Valores = tuple(DatosACambiar.values())

        Cambio = f'''
        UPDATE refaccion SET {Columnas} WHERE codigo = %s RETURNING codigo;
        '''

        Cursor.execute(Cambio,Valores+(Codigo,))
        CodigoRefaccion = Cursor.fetchone()[0]

    return CodigoRefaccion


def ObtenerValores(ConexionDB,Columna):
    # Regresa una lista con las marcas o categorías que existen en la tabla
    if Columna not in ['marca','categoria']:
        return []

    with ConexionDB.cursor() as Cursor:
        Cursor.execute(f"SELECT DISTINCT {Columna} FROM refaccion ORDER BY {Columna};")
        Valores = [Fila[0] for Fila in Cursor.fetchall()]

    return Valores

def FiltrarRefacciones(ConexionDB,Filtros):
    # Filtros es un diccionario, por ejemplo: {'marca': 'Bosch', 'precio_max': 500, 'disponibles': True}
    Condiciones = []
    Valores = []

    if 'marca' in Filtros:
        Condiciones.append("marca = %s")
        Valores.append(Filtros['marca'])

    if 'categoria' in Filtros:
        Condiciones.append("categoria = %s")
        Valores.append(Filtros['categoria'])

    if 'precio_min' in Filtros:
        Condiciones.append("precio >= %s")
        Valores.append(Filtros['precio_min'])

    if 'precio_max' in Filtros:
        Condiciones.append("precio <= %s")
        Valores.append(Filtros['precio_max'])

    if Filtros.get('disponibles'):
        Condiciones.append("existencia > 0")

    Consulta = "SELECT codigo, articulo, num_parte, marca, categoria, precio, existencia, estado FROM refaccion"
    if Condiciones:
        Consulta += " WHERE " + " AND ".join(Condiciones)
    Consulta += " ORDER BY precio;"

    with ConexionDB.cursor() as Cursor:
        Cursor.execute(Consulta,tuple(Valores))
        Refacciones = Cursor.fetchall()

    return Refacciones
