import os
from almacen.basedatos import basedatos
from almacen.funciones import FuncionesRefacciones



basedatos.InicializarBD()
while True:
    os.system('cls')
    print("""
    ========= SISTEMA DE ALMACÉN =========
    1. Registrar refacción (REG)
    2. Buscar Refacción (SEARCH)
    0. Salir (EXIT)
    ======================================
    """)
    Oprc = input("\n* ¿Qué operación desea realizar?\n")

    match Oprc.upper():
        case "1" | "REG":
            CodigoBarras = input("* Ingrese el código de barras: ")
            Nombre = input("* Ingrese el nombre de la refacción: ")
            NumParte = input("* Ingrese el número de parte: ")
            Modelo = input("* Ingrese el modelo: ")
            Yr = input("* Ingrese el año: ")
            Desc = input("* Ingrese la descripción: ")
            LinkImg = input("* Ingrese el link de la imagen: ")

            try:
                with basedatos.ObtenerConexion() as Conexion:
                    SkuRegistrado = FuncionesRefacciones.RegistrarRefaccion(Conexion,CodigoBarras,Nombre,NumParte,Modelo,Yr,Desc,LinkImg)
                    print(f"* Se registró {Nombre} con el SKU {SkuRegistrado}.")
            except Exception as Error:
                print(f"* Error al registrar {Nombre}.")


        case "2" | "SEARCH":
            Buscador = input("* Ingrese el código de barras o SKU de la refacción a buscar: ")

            try:
                with basedatos.ObtenerConexion() as Conexion:
                    Refaccion = FuncionesRefacciones.BuscarRefaccion(Conexion,Buscador)

                    if Refaccion is None:
                        print("* No se encontró la parte.")
                    else:
                        print(f'''
                        ========= {Refaccion[2]} =========
                        SKU: {Refaccion[0]}
                        Número de parte: {Refaccion[3]}
                        Código de barras: {Refaccion[1]}
                        Modelo: {Refaccion[4]}
                        Año: {Refaccion[5]}
                        Descripción:
                        {Refaccion[6]}
                        ''')
            except Exception as Error:
                print("* No se encontró la pieza.")

        case "0" | "EXIT":
            print("Saliendo del programa.")
            break

        case _:
            print("* Operación inválida.")

    os.system("pause")