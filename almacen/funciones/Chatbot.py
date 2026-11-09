import random
from difflib import get_close_matches
from almacen.funciones import FuncionesRefacciones
from almacen.basedatos import basedatos

# Palabras que no sirven para buscar
PalabrasIgnoradas = ['quiero','busco','buscando','busca','buscar','necesito','ocupo','quisiera','estoy','ando',
                     'una','un','unos','unas','de','del','la','el','los','las','que','con','y','para','me','por',
                     'favor','hay','tienen','tiene','tienes','tengan','alguna','alguno','algun','algunas',
                     'pieza','piezas','refaccion','refacciones','precio','pesos','peso','menos','mas','maximo',
                     'minimo','hasta','desde','mayor','menor','debajo','abajo','arriba','encima','bajo','en',
                     'existencia','disponible','disponibles','solo','muestrame','muestra','mostrar','ver','dame',
                     'a','o','si','no','quitar','marca','categoria','cual','cuales','cuanto','cuantos','cuantas',
                     'cuesta','cuestan','costo','valen','barata','baratas','barato','baratos','cara','caras',
                     'caro','caros','economica','economicas','economico','economicos','otra','otro','otras',
                     'hola','buenas','buenos','dias','tardes','noches','ok','gracias','tambien','ahora','pero',
                     'sea','sean','se','es','al','tengo','mi','su','ya','le','lo','como','esta','nueva','nuevo','consulta',
                     'consultas','entonces','tambien','pasame','pasa','damelo','ensename','mandame','necesitaria','ocupamos',
                     'ordena','ordenar','ordenalas','ordenalos','ordenado','ordenadas','ordenados','orden','acomoda',
                     'acomodalas','acomodalos','ascendente','descendente','primero','precios','lista','listame',
                     'nombre','alfabetico','alfabeticamente','alfabetica','existencias','cantidad','inventario',
                     'stock','z','checa','revisa','oye','disculpa','perdon','quisiera','podrias','puedes','puede','cuentas']
PalabrasSeguimiento = ['y','pero','ahora','tambien','entonces','solo']
PalabrasMaximo = ['menos','maximo','max','hasta','menor','debajo','abajo','bajo','barato','baratos']
PalabrasMinimo = ['mas','minimo','min','desde','mayor','arriba','encima']

Saludos = ['hola','buenas','buenos','hey','saludos']
Despedidas = ['salir','exit','adios','bye','chao','hasta luego','nos vemos']
Afirmaciones = ['si','claro','dale','ok','va','sale','por favor','porfa','simon','yes']


def QuitarAcentos(Texto):
    Texto = Texto.lower()
    for Con,Sin in zip('áéíóúü','aeiouu'):
        Texto = Texto.replace(Con,Sin)
    return Texto

def Singular(Palabra):
    # baterias -> bateria, para que coincida aunque escriban en plural o singular
    if len(Palabra) > 3 and Palabra.endswith('s'):
        return Palabra[:-1]
    return Palabra

def BuscarParecido(Palabra,Valores):
    # Para errores de dedo: "bosh" se parece a "Bosch". Regresa el valor original o None
    Normalizados = {Singular(QuitarAcentos(Valor)): Valor for Valor in Valores}
    Coincidencias = get_close_matches(Singular(Palabra),list(Normalizados),n=1,cutoff=0.75)
    if Coincidencias:
        return Normalizados[Coincidencias[0]]
    return None

def EsNumero(Palabra):
    try:
        float(Palabra)
        return True
    except ValueError:
        return False

def Bot(Texto,Respuestas):
    Respuestas.append(Texto)

def MostrarAyuda(Respuestas):
    Respuestas.append('''
    Cada mensaje es una búsqueda nueva. Si solo me das marca, precio o 'en existencia',
    afino la búsqueda anterior. Ejemplos:
      busco baterías con precio menos a 200
      bujías de la marca NGK
      ¿cuál es la batería más barata?
      ordena las baterías de menor a mayor precio
      ordénalas por nombre / por existencia / por marca
      y de Bosch?
      eléctrico en existencia
    Comandos:
      quitar marca / quitar categoria / quitar precio / quitar texto
      filtros   -> ver los filtros activos
      reiniciar -> empezar de nuevo
      salir     -> regresar al menú
    ''')

def MostrarFiltros(Filtros,Respuestas):
    if not Filtros:
        Respuestas.append("No hay filtros de búsqueda activos.")
        return
    
    Respuestas.append("Estos son los filtros actuales:")
    for Nombre,Valor in Filtros.items():
        Respuestas.append(f"- {Nombre}: {Valor}")

def Describir(Filtros):
    # Convierte los filtros en una frase, ej: "baterías de la marca Bosch con precio menor a $3,000"
    Frase = Filtros.get('categoria','refacciones').lower()
    if 'texto' in Filtros:
        Frase += " de " + " ".join(Filtros['texto'])
    if 'marca' in Filtros:
        Frase += f" de la marca {Filtros['marca']}"
    if 'precio_min' in Filtros and 'precio_max' in Filtros:
        Frase += f" con precio entre ${Filtros['precio_min']:,.0f} y ${Filtros['precio_max']:,.0f}"
    elif 'precio_max' in Filtros:
        Frase += f" con precio menor a ${Filtros['precio_max']:,.0f}"
    elif 'precio_min' in Filtros:
        Frase += f" con precio mayor a ${Filtros['precio_min']:,.0f}"
    if Filtros.get('disponibles'):
        Frase += " en existencia"
    if 'orden' in Filtros:
        Campo = Filtros.get('campo','precio')
        if Campo in ['nombre','marca']:
            Frase += ", en orden alfabético (A-Z)" if Filtros['orden'] == 'asc' else ", en orden alfabético inverso (Z-A)"
        elif Filtros['orden'] == 'asc':
            Frase += f", de menor a mayor {Campo}"
        else:
            Frase += f", de mayor a menor {Campo}"
    return Frase

def CrearEstadoChat():
    with basedatos.ObtenerConexion() as Conexion:
        Marcas = FuncionesRefacciones.ObtenerValores(Conexion,'marca')
        Categorias = FuncionesRefacciones.ObtenerValores(Conexion,'categoria')

    return{
        'Marcas': Marcas,
        'Categorias': Categorias,
        'Filtros': {},
        'EsperandoRespuesta': False
    }

def LeerMensaje(Mensaje,Filtros,Marcas,Categorias):
    # Revisa el mensaje y va guardando los filtros que encuentre en el diccionario Filtros
    Mensaje = QuitarAcentos(Mensaje)
    Palabras = [Palabra.strip('.,;:?!¿¡') for Palabra in Mensaje.replace('$','').replace(',','').split()]
    Palabras = [Palabra for Palabra in Palabras if Palabra != '']

    Usadas = []

    # marca y categoría (se compara contra lo que existe en la base de datos)
    for Marca in Marcas:
        if QuitarAcentos(Marca) in Mensaje:
            Filtros['marca'] = Marca
            Usadas += QuitarAcentos(Marca).split()

    for Categoria in Categorias:
        if Singular(QuitarAcentos(Categoria)) in Mensaje:
            if Filtros.get('categoria',Categoria) != Categoria:
                Filtros.pop('texto',None)   # cambió de tipo de pieza, se olvida el texto anterior
            Filtros['categoria'] = Categoria
            Usadas += [Singular(QuitarAcentos(Categoria)),QuitarAcentos(Categoria)]

    # precios: se fija en las palabras anteriores al número
    for i,Palabra in enumerate(Palabras):
        if EsNumero(Palabra):
            Anteriores = Palabras[max(0,i-3):i]
            if ('no' in Anteriores and 'mas' in Anteriores) or any(P in PalabrasMaximo for P in Anteriores[-2:]):
                Filtros['precio_max'] = float(Palabra)
            elif any(P in PalabrasMinimo for P in Anteriores[-2:]):
                Filtros['precio_min'] = float(Palabra)
            Usadas.append(Palabra)

    # orden de la lista: "ordena de menor a mayor", "por nombre", "por existencia", "las más baratas"...
    TextoOrden = ' '.join(Palabras)

    Campo = None
    if any(K in TextoOrden for K in ['por nombre','alfabet','a la z','z a la a','por articulo']):
        Campo = 'nombre'
    elif any(K in TextoOrden for K in ['por existencia','por stock','por cantidad','por inventario','mas existencia','menos existencia']):
        Campo = 'existencia'
    elif 'por marca' in TextoOrden:
        Campo = 'marca'
    elif 'por precio' in TextoOrden:
        Campo = 'precio'

    PidioOrden = Campo is not None or any(K in TextoOrden for K in ['orden','acomod','ascendente','descendente','menor a mayor','mayor a menor','menor precio a mayor','mayor precio a menor'])

    if PidioOrden:
        Filtros['campo'] = Campo or 'precio'
        PosMenor = TextoOrden.find('menor')
        PosMayor = TextoOrden.find('mayor')
        if 'descendente' in TextoOrden or 'z a la a' in TextoOrden or 'mas existencia' in TextoOrden:
            Filtros['orden'] = 'desc'
        elif 'ascendente' in TextoOrden or 'a la z' in TextoOrden or 'menos existencia' in TextoOrden:
            Filtros['orden'] = 'asc'
        elif PosMenor != -1 and PosMayor != -1:
            Filtros['orden'] = 'asc' if PosMenor < PosMayor else 'desc'
        elif Filtros['campo'] == 'existencia':
            Filtros['orden'] = 'desc'    # por existencia: primero las que más hay
        else:
            Filtros['orden'] = 'asc'
    elif any(P in Palabras for P in ['baratas','baratos','economicas','economicos']):
        Filtros['campo'] = 'precio'
        Filtros['orden'] = 'asc'
    elif any(P in Palabras for P in ['caras','caros']):
        Filtros['campo'] = 'precio'
        Filtros['orden'] = 'desc'

    if 'disponible' in Mensaje or 'en existencia' in Mensaje or 'con existencia' in Mensaje or 'en stock' in Mensaje or 'con stock' in Mensaje:
        Filtros['disponibles'] = True

    # lo que sobre se toma como texto para buscar en el nombre o número de parte
    for Palabra in Palabras:
        if Palabra in Usadas or Palabra in PalabrasIgnoradas or EsNumero(Palabra) or len(Palabra) < 2:
            continue
        if Singular(Palabra) in Usadas or any(Palabra in U or U in Palabra for U in Usadas if len(U) > 2):
            continue

        # si se parece a una marca o categoría se toma esa, si no, se busca como texto
        if len(Palabra) >= 4:
            MarcaParecida = BuscarParecido(Palabra,Marcas)
            if MarcaParecida is not None:
                Filtros['marca'] = MarcaParecida
                continue
            CategoriaParecida = BuscarParecido(Palabra,Categorias)
            if CategoriaParecida is not None:
                if Filtros.get('categoria',CategoriaParecida) != CategoriaParecida:
                    Filtros.pop('texto',None)
                Filtros['categoria'] = CategoriaParecida
                continue

        if Palabra not in Filtros.setdefault('texto',[]):
            Filtros['texto'].append(Palabra)

def QuitarFiltro(Mensaje,Filtros):
    if 'marca' in Mensaje:
        Filtros.pop('marca',None)
    if 'categoria' in Mensaje:
        Filtros.pop('categoria',None)
    if 'precio' in Mensaje:
        Filtros.pop('precio_min',None)
        Filtros.pop('precio_max',None)
    if 'texto' in Mensaje:
        Filtros.pop('texto',None)
    if 'disponible' in Mensaje:
        Filtros.pop('disponibles',None)
    if 'orden' in Mensaje:
        Filtros.pop('orden',None)
        Filtros.pop('campo',None)

def ObtenerRefacciones(Conexion,Filtros):
    # Primero se filtra en la base de datos y luego por las palabras del nombre
    Refacciones = FuncionesRefacciones.FiltrarRefacciones(Conexion,Filtros)
    for Palabra in Filtros.get('texto',[]):
        Refacciones = [R for R in Refacciones if Singular(Palabra) in QuitarAcentos(f"{R[1]} {R[2]}")]
    return Refacciones

def OrdenarRefacciones(Refacciones,Filtros):
    # Ordena la lista según lo que pidió el cliente. Posiciones: 1 nombre, 3 marca, 5 precio, 6 existencia
    Posiciones = {'precio': 5, 'nombre': 1, 'existencia': 6, 'marca': 3}
    Posicion = Posiciones[Filtros.get('campo','precio')]

    def Clave(Refaccion):
        Valor = Refaccion[Posicion]
        if isinstance(Valor,str):
            return QuitarAcentos(Valor)
        return Valor

    return sorted(Refacciones,key=Clave,reverse=(Filtros.get('orden') == 'desc'))

def MostrarLista(Refacciones,Respuestas):
    for Refaccion in Refacciones[:15]:
        Respuestas.append(
            f"[{Refaccion[0]}]: {Refaccion[1]}"
            f"\nParte: {Refaccion[2]} | {Refaccion[3]}"
            f"\n${Refaccion[5]:,.2f}"
            f"\n{Refaccion[6]} En existencia"
        )
    if len(Refacciones) > 15:
        Respuestas.append(f"... y {len(Refacciones)-15} más. Dime otra característica para acotar.")

def Responder(Conexion,Filtros,Extremo,Respuestas):
    # Regresa True si se quedó esperando una confirmación del cliente
    Refacciones = ObtenerRefacciones(Conexion,Filtros)
    Descripcion = Describir(Filtros)

    if len(Refacciones) > 0:
        DescripcionSinOrden = Describir({C: V for C,V in Filtros.items() if C not in ['orden','campo']})
        if Extremo == 'barata':
            Respuestas.append(f"La opción más económica de {DescripcionSinOrden} es:")
            Refacciones = [Refacciones[0]]
        elif Extremo == 'cara':
            Respuestas.append(f"La opción más cara de {DescripcionSinOrden} es:")
            Refacciones = [Refacciones[-1]]
        elif len(Refacciones) == 1:
            Respuestas.append(f"Solo encontré una opción de {Descripcion}:")
        else:
            Refacciones = OrdenarRefacciones(Refacciones,Filtros)
            Inicio = random.choice(["Encontré","Tengo","Mira, hay"])
            Respuestas.append(f"{Inicio} {len(Refacciones)} opciones de {Descripcion}:")

        MostrarLista(Refacciones,Respuestas)
        Respuestas.append("¿Quieres afinar más? Puedes decirme otra marca, un precio, etc.")
        return False

    # No hubo resultados: se intenta explicar por qué
    Sin = {Clave: Valor for Clave,Valor in Filtros.items() if Clave not in ['precio_min','precio_max']}
    if ('precio_min' in Filtros or 'precio_max' in Filtros) and Sin:
        SinPrecio = ObtenerRefacciones(Conexion,Sin)
        if len(SinPrecio) > 0:
            Barato = SinPrecio[0][5]
            Caro = SinPrecio[-1][5]
            if Barato == Caro:
                Rango = f"cuesta ${Barato:,.0f}"
            else:
                Rango = f"cuesta entre ${Barato:,.0f} y ${Caro:,.0f}"
            Respuestas.append(f"No tengo {Descripcion}. Lo que sí tengo de {Describir(Sin)} {Rango}.")
            Respuestas.append("¿Quieres que quite el filtro de precio y te las muestre? (sí/no)")
            return True

    Respuestas.append(f"Por ahora no tengo {Descripcion}.")
    Sugerencia = "'quitar marca', 'quitar precio' o 'reiniciar'"
    if 'texto' in Filtros:
        Sugerencia = "'quitar texto' (por si escribiste mal una palabra), " + Sugerencia
    Respuestas.append(f"Puedes probar con {Sugerencia}.")
    return False


def ProcesarMensaje(Mensaje, Conexion, EstadoChat):
    Respuestas = []

    Marcas = EstadoChat['Marcas']
    Categorias = EstadoChat['Categorias']
    Filtros = EstadoChat['Filtros']
    EsperandoRespuesta = EstadoChat['EsperandoRespuesta']

    Texto = QuitarAcentos(Mensaje).strip('.,;:?!¿¡ ')
    Palabras = Texto.split()

    # Guarda los cambios antes de devolver las respuestas
    def Finalizar():
        EstadoChat['Filtros'] = Filtros
        EstadoChat['EsperandoRespuesta'] = EsperandoRespuesta
        return Respuestas

    if Texto == '':
        return Finalizar()

    if Texto in Despedidas:
        Bot("¡Hasta luego, que tengas buen día!", Respuestas)
        return Finalizar()

    if Texto == 'ayuda':
        MostrarAyuda(Respuestas)
        return Finalizar()

    if Texto in ['reiniciar', 'nuevo', 'empezar de nuevo']:
        Filtros = {}
        EsperandoRespuesta = False
        Bot("Listo, empezamos de nuevo. ¿Qué pieza buscas?", Respuestas)
        return Finalizar()

    if Texto == 'filtros':
        MostrarFiltros(Filtros, Respuestas)
        return Finalizar()

    # Respuesta a la pregunta de "¿quito el filtro de precio?"
    if EsperandoRespuesta:
        EsperandoRespuesta = False

        if Texto in Afirmaciones:
            Filtros.pop('precio_min', None)
            Filtros.pop('precio_max', None)
            EsperandoRespuesta = Responder(
                Conexion, Filtros, None, Respuestas
            )
            return Finalizar()

        if Texto == 'no':
            Bot("Está bien. ¿Quieres cambiar el precio o buscar otra cosa?", Respuestas)
            return Finalizar()

    # Conversación básica
    if 'gracias' in Palabras:
        Bot("¡De nada! ¿Te ayudo con algo más?", Respuestas)
        return Finalizar()

    if Palabras and Palabras[0] in Saludos and len(Palabras) <= 3:
        Bot("¡Hola! ¿Qué refacción andas buscando?", Respuestas)
        return Finalizar()

    if 'como estas' in Texto or 'que tal' in Texto:
        Bot("¡Muy bien, listo para ayudarte a buscar piezas! ¿Qué necesitas?", Respuestas)
        return Finalizar()

    if Texto.startswith('quitar'):
        QuitarFiltro(Texto, Filtros)
        Bot("Listo, quité ese filtro.", Respuestas)

        if not Filtros:
            return Finalizar()

        EsperandoRespuesta = Responder(
            Conexion, Filtros, None, Respuestas
        )
        return Finalizar()

    # ¿Pide la más barata o la más cara?
    Extremo = None

    for i, Palabra in enumerate(Palabras[:-1]):
        if Palabra == 'mas' and Palabras[i+1] in ['barata', 'barato', 'economica', 'economico']:
            Extremo = 'barata'

        elif Palabra == 'mas' and Palabras[i+1] in ['cara', 'caro']:
            Extremo = 'cara'

    # Cada mensaje se lee por separado
    Nuevos = {}
    LeerMensaje(Mensaje, Nuevos, Marcas, Categorias)

    if not Nuevos:
        if Extremo is not None and Filtros:
            EsperandoRespuesta = Responder(
                Conexion, Filtros, Extremo, Respuestas
            )
        else:
            Bot(
                "Mmm, no te entendí bien. Dime qué pieza buscas, "
                "por ejemplo: 'baterías Bosch' o 'bujías menos de 200'.",
                Respuestas
            )

        return Finalizar()

    # ¿Es un seguimiento de la búsqueda anterior o una búsqueda nueva?
    EsSeguimiento = bool(Filtros) and (
        Palabras[0] in PalabrasSeguimiento or
        ('categoria' not in Nuevos and 'texto' not in Nuevos)
    )

    if EsSeguimiento:
        if 'categoria' in Nuevos and Filtros.get('categoria') != Nuevos['categoria']:
            Filtros.pop('texto', None)

        for Clave, Valor in Nuevos.items():
            if Clave == 'texto':
                Previo = Filtros.setdefault('texto', [])
                Previo += [P for P in Valor if P not in Previo]
            else:
                Filtros[Clave] = Valor

    else:
        Filtros = Nuevos

    EsperandoRespuesta = Responder(
        Conexion, Filtros, Extremo, Respuestas
    )

    return Finalizar()