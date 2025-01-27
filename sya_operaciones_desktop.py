import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import os
import webbrowser
from PIL import Image, ImageTk
import sys

def resource_path(relative_path):
    """ Obtiene la ruta absoluta a los recursos, funciona para dev y para ejecutables creados con PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def descargar_excel(url, nombre_archivo):
    """
    Función para descargar un archivo Excel desde una URL.
    """
    try:
        respuesta = requests.get(url, stream=True)
        respuesta.raise_for_status()  # Lanza una excepción si la solicitud falla

        with open(nombre_archivo, 'wb') as archivo:
            for chunk in respuesta.iter_content(chunk_size=8192):
                archivo.write(chunk)

        # Mostrar un mensaje emergente al completar la descarga
        messagebox.showinfo("Descarga completada", f"Archivo '{nombre_archivo}' descargado exitosamente.")
        return True
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error de descarga", f"Error al descargar el archivo:\n{e}")
        return False

def abrir_excel(nombre_archivo):
    """
    Función para abrir el archivo Excel descargado.
    """
    if os.path.exists(nombre_archivo):
        # Intentar abrir el archivo con la aplicación predeterminada
        webbrowser.open(f"file://{os.path.abspath(nombre_archivo)}")
    else:
        messagebox.showerror("Error", "El archivo no existe. Por favor, descárguelo primero.")

def on_descargar():
    """
    Evento del botón 'Descargar archivo Excel'.
    """
    url_servidor = "http://34.67.103.132:5000/descargar-excel"  # URL del servidor
    nombre_archivo_local = resource_path("reportes/reportes_parte_diario.xlsx")
    descargar_excel(url_servidor, nombre_archivo_local)

def on_abrir():
    """
    Evento del botón 'Abrir Excel'.
    """
    nombre_archivo_local = resource_path("reportes/reportes_parte_diario.xlsx")
    abrir_excel(nombre_archivo_local)

# Crear la ventana principal
root = tk.Tk()
root.title("S&A - Reportes de Parte Diario ")
root.geometry("450x420")
root.resizable(True, True)

# Estilo moderno
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=10)

# Etiqueta de título
titulo = ttk.Label(root, text="S&A - Reportes de Parte Diario", font=("Helvetica", 16, "bold"))
titulo.pack(pady=10)

# Cargar la imagen
image = Image.open(resource_path("images/smontyaragon.png"))
photo = ImageTk.PhotoImage(image)

# Crear un label para la imagen y posicionarlo en el centro
label_imagen = ttk.Label(root, image=photo)
label_imagen.pack(pady=10)

# Contenedor de botones
frame_botones = ttk.Frame(root)
frame_botones.pack(pady=10)

# Botón para descargar el archivo Excel
btn_descargar = ttk.Button(frame_botones, text="Descargar archivo Excel", command=on_descargar)
btn_descargar.grid(row=0, column=0, padx=10)

# Botón para abrir el archivo Excel
btn_abrir = ttk.Button(frame_botones, text="Abrir Excel", command=on_abrir)
btn_abrir.grid(row=0, column=1, padx=10)

# Mostrar la ventana
root.mainloop()