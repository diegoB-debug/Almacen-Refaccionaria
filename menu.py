import os
from almacen.basedatos import basedatos
from almacen.funciones import FuncionesRefacciones

basedatos.InicializarBD()
# basedatos.CargarDatosPrueba() # Comentar esta línea después de correr el programa para que no se dupliquen los datos de prueba



while True:
    os.system('cls')
    print("""
    ========= SISTEMA DE ALMACÉN =========
    1. Registrar refacción (REG)
    2. Buscar refacción (SEARCH)
    3. Alta de refacción (ALTA)
    4. Baja de refacción (BAJA)
    0. Salir (EXIT)
    ======================================
    """)
    Oprc = input("\n* ¿Qué operación desea realizar?\n")


    match Oprc.upper():
        case "1" | "REG":
            CodigoBarras = input("* Ingrese el código de barras: ")

            # checar si ya hay alguna refaccion con el mismo código de barras para evitar duplicados
            with basedatos.ObtenerConexion() as Conexion:
                Coincide = FuncionesRefacciones.BuscarRefaccion(Conexion,CodigoBarras)
                if Coincide is None: #No hay refacci´n que coincida entonces se llena manualmente
                    Articulo = input("* Ingrese el nombre de la refacción: ")
                    NumParte = input("* Ingrese el número de parte: ")
                    Marca = input("* Ingrese la marca: ")
                    Categoria = input("* Ingrese la categoría: ")
                    Precio = input("* Ingrese el precio de la refacción: ")
                    Minimo = input("* Ingrese el mínimo aceptable: ")
                    Ubicacion = input("* Ingrese la ubicación del producto en almacén: ")

                    try:
                        with basedatos.ObtenerConexion() as Conexion:
                            CodigoRegistrado = FuncionesRefacciones.RegistrarRefaccion(Conexion,CodigoBarras,Articulo,NumParte,Marca,Categoria,Precio,Minimo,Ubicacion)
                            print(f"* Se registró {Articulo} con el código {CodigoRegistrado}.")
                    except Exception as Error:
                        print(f"* Error al registrar {Articulo}.\nError {Error}")

                else: # Sí hay refacción que coincida
                    print(f"* Ya se registró la refacción {Coincide[2]}. Su código es: {Coincide[0]}")



        case "2" | "SEARCH":
            Buscador = input("* Ingrese el código de barras o SKU de la refacción a buscar: ")

            with basedatos.ObtenerConexion() as Conexion:
                Refaccion = FuncionesRefacciones.BuscarRefaccion(Conexion,Buscador)

                if Refaccion is None:
                     print("* No se encontró la parte.")
                else:
                    print(f'''
                    ========= {Refaccion[2]} =========
                    Código: {Refaccion[0]}
                    Código de barras: {Refaccion[1]}
                    Precio: ${Refaccion[6]}
                    Número de parte: {Refaccion[3]}
                    Marca: {Refaccion[4]}
                    Categoria: {Refaccion[5]}
                    {Refaccion[7]} en existencia, estado: {Refaccion[11]}
                    ''')


        case "3" | "ALTA":
            Cantidad = int(input("* Ingrese la cantidad de productos: "))
            CodigoBarras = input("* Ingrese el código de barras del producto: ")

            with basedatos.ObtenerConexion() as Conexion:
                CodigoRefaccion,CantidadActual = FuncionesRefacciones.AltaRefacción(Conexion,CodigoBarras,Cantidad)

                if CodigoRefaccion is None:
                    print("* No se encontró la refacción.")
                else:
                    print(f"* Se añadieron {Cantidad} productos al producto con el código {CodigoRefaccion}")

                    Minimo = FuncionesRefacciones.GetMinimo(Conexion,CodigoRefaccion)
                    if CantidadActual <= Minimo:
                        RefaccionActualizada = FuncionesRefacciones.ActualizarEstado(Conexion,CodigoRefaccion,'Bajo')
                    elif CantidadActual > Minimo:
                        RefaccionActualizada = FuncionesRefacciones.ActualizarEstado(Conexion,CodigoRefaccion,'En Stock')


        case "4" | "BAJA":
            Cantidad = int(input("* Ingrese la cantidad de productos: "))
            CodigoBarras = input("* Ingrese el código de barras del producto: ")

            with basedatos.ObtenerConexion() as Conexion:
                CantidadActual = FuncionesRefacciones.GetCantidad(Conexion,CodigoBarras)

                if CantidadActual[0] == '0' or CantidadActual[0]-Cantidad < 0:
                    print("* La refacción no está en existencia o no hay suficientes disponibles.")
                else:
                    CodigoRefaccion,CantidadActual = FuncionesRefacciones.BajaRefacción(Conexion,CodigoBarras,Cantidad)
                    print(f"* Se vendieron {Cantidad} productos con el código {CodigoRefaccion}")

                    Minimo = FuncionesRefacciones.GetMinimo(Conexion,CodigoRefaccion)
                    if CantidadActual <= Minimo:
                        RefaccionActualizada = FuncionesRefacciones.ActualizarEstado(Conexion,CodigoRefaccion,'Bajo')
                    elif CantidadActual > Minimo:
                        RefaccionActualizada = FuncionesRefacciones.ActualizarEstado(Conexion,CodigoRefaccion,'En Stock')
                    

        case "0" | "EXIT":
            print("Saliendo del programa.")
            break

        case _:
            print("* Operación inválida.")

    os.system("pause")