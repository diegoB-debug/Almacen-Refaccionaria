import tkinter as tk
from tkinter import scrolledtext
from almacen.basedatos import basedatos
from almacen.funciones import Chatbot

def AbrirVentanaChatbot():
    Ventana = tk.Tk()
    Ventana.title("Asistente para búsqueda")
    Ventana.geometry("350x500")

    Convo = scrolledtext.ScrolledText(Ventana,wrap=tk.WORD,state='disabled',font=("Arial",11))
    Convo.pack(fill=tk.BOTH,expand=True,padx=10,pady=10)

    FrameEntrada = tk.Frame(Ventana)
    FrameEntrada.pack(fill=tk.X,padx=10,pady=(0,10))

    Entrada = tk.Entry(FrameEntrada,font=("Arial",11))
    Entrada.pack(side=tk.LEFT,fill=tk.X,expand=True,padx=(0,5))

    def MostrarMensaje(Sender,Msg):
        Convo.config(state='normal')
        Convo.insert(tk.END,f"{Sender}: {Msg}\n\n")
        Convo.config(state='disabled')
        Convo.see(tk.END)

    def EnviarMensaje(Evento=None):
        Msg = Entrada.get().strip()
        Entrada.delete(0,tk.END)
        MostrarMensaje("Tú",Msg)

        try:
            with basedatos.ObtenerConexion() as Conexion:
                Respuesta = Chatbot.ProcesarMensaje(Msg,Conexion,EstadoChat)
                for Text in Respuesta:
                    MostrarMensaje("Bot",Text)
        except Exception as Error:
            MostrarMensaje("Bot",f"Ocurrió un error {Error}")

    EstadoChat = Chatbot.CrearEstadoChat()

    SendBoton = tk.Button(FrameEntrada,text="Enviar",command=EnviarMensaje)
    SendBoton.pack(side=tk.RIGHT)

    Entrada.bind("<Return>",EnviarMensaje)
    Entrada.focus()

    MostrarMensaje("Bot","¡Hola! Soy el asistente del almacén. Cuéntame qué pieza buscas. Escribe 'ayuda' para ver ejemplos.")