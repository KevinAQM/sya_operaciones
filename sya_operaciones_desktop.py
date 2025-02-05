import os
import sys
import requests
import webbrowser
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

def resource_path(relative_path):
    """
    Obtiene la ruta absoluta a los recursos, tanto para desarrollo como para ejecutables generados con PyInstaller.
    """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def obtener_ruta_aplicacion():
    """
    Obtiene la ruta del directorio en el que se encuentra el ejecutable o el script.
    """
    if getattr(sys, 'frozen', False):
        # En modo ejecutable (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # En modo desarrollo
        return os.path.dirname(os.path.abspath(__file__))

def crear_carpeta_reportes():
    """
    Crea la carpeta 'reportes' en la misma ruta que el ejecutable, si no existe.
    """
    ruta_app = obtener_ruta_aplicacion()
    ruta_reportes = os.path.join(ruta_app, "reportes")
    if not os.path.exists(ruta_reportes):
        try:
            os.makedirs(ruta_reportes)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta 'reportes':\n{e}")
    return ruta_reportes

def descargar_excel(url, nombre_archivo):
    """
    Función para descargar un archivo Excel desde una URL y guardarlo en la carpeta 'reportes'.
    """
    try:
        respuesta = requests.get(url, stream=True)
        respuesta.raise_for_status()  # Lanza una excepción si la solicitud falla

        ruta_app = obtener_ruta_aplicacion()
        # Se construye la ruta completa: [ruta_app]/reportes/[nombre_archivo]
        ruta_reportes = os.path.join(ruta_app, "reportes")
        if not os.path.exists(ruta_reportes):
            os.makedirs(ruta_reportes)
        nombre_archivo_completo = os.path.join(ruta_reportes, nombre_archivo)
        
        with open(nombre_archivo_completo, 'wb') as archivo:
            for chunk in respuesta.iter_content(chunk_size=8192):
                archivo.write(chunk)

        messagebox.showinfo("Descarga completada", f"Archivo '{nombre_archivo}' descargado exitosamente en:\n{nombre_archivo_completo}")
        return True
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error de descarga", f"Error al descargar el archivo:\n{e}")
        return False

def abrir_excel(nombre_archivo):
    """
    Función para abrir el archivo Excel descargado desde la carpeta 'reportes'.
    """
    ruta_app = obtener_ruta_aplicacion()
    ruta_reportes = os.path.join(ruta_app, "reportes")
    nombre_archivo_completo = os.path.join(ruta_reportes, nombre_archivo)
    
    if os.path.exists(nombre_archivo_completo):
        webbrowser.open(f"file://{os.path.abspath(nombre_archivo_completo)}")
    else:
        messagebox.showerror("Error", "El archivo no existe. Por favor, descárguelo primero.")

def on_descargar():
    """
    Evento del botón 'Descargar archivo Excel'.
    """
    url_servidor = "http://34.67.103.132:5000/descargar-excel"  # URL del servidor
    # Se especifica solo el nombre del archivo para colocarlo dentro de la carpeta 'reportes'
    nombre_archivo_local = "reportes_parte_diario.xlsx"
    descargar_excel(url_servidor, nombre_archivo_local)

def on_abrir():
    """
    Evento del botón 'Abrir Excel'.
    """
    nombre_archivo_local = "reportes_parte_diario.xlsx"
    abrir_excel(nombre_archivo_local)

# Crear la ventana principal
root = tk.Tk()
root.title("S&A - Reportes de Parte Diario")
root.geometry("450x420")
root.resizable(True, True)

# Establecer el ícono de la ventana
try:
    root.iconbitmap(resource_path("images/smontyaragon.ico"))
except Exception:
    pass  # Ignorar si el ícono no se encuentra (en desarrollo)

# Estilo moderno
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=10)

# Etiqueta de título
titulo = ttk.Label(root, text="S&A - Reportes de Parte Diario", font=("Helvetica", 16, "bold"))
titulo.pack(pady=10)

# Cargar la imagen
try:
    image = Image.open(resource_path("images/smontyaragon.png"))
    photo = ImageTk.PhotoImage(image)
    label_imagen = ttk.Label(root, image=photo)
    label_imagen.image = photo  # Mantener referencia para evitar que el recolector de basura la elimine
    label_imagen.pack(pady=10)
except Exception:
    pass  # Ignorar si la imagen no se encuentra

# Crear la carpeta 'reportes' al inicio de la aplicación
crear_carpeta_reportes()

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
