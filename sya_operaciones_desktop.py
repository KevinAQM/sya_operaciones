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
    Evento del botón 'Descargar Reporte Diario'.
    """
    url_servidor = "http://34.67.103.132:5000/descargar-excel"  # URL del servidor
    # Se especifica solo el nombre del archivo para colocarlo dentro de la carpeta 'reportes'
    nombre_archivo_local = "reportes_parte_diario.xlsx"
    descargar_excel(url_servidor, nombre_archivo_local)

def on_abrir():
    """
    Evento del botón 'Abrir Reporte Diario'.
    """
    nombre_archivo_local = "reportes_parte_diario.xlsx"
    abrir_excel(nombre_archivo_local)

def on_descargar_requerimientos():
    """
    Evento del botón 'Descargar Requerimientos'.
    """
    url_servidor = "http://34.67.103.132:5000/descargar-requerimientos-excel"  # URL del servidor para requerimientos
    nombre_archivo_local = "requerimientos_obra.xlsx"
    descargar_excel(url_servidor, nombre_archivo_local)

def on_abrir_requerimientos():
    """
    Evento del botón 'Abrir Requerimientos'.
    """
    nombre_archivo_local = "requerimientos_obra.xlsx"
    abrir_excel(nombre_archivo_local)

# Crear la ventana principal
root = tk.Tk()
root.title("S&A - Area Operaciones")
root.geometry("450x520")
root.resizable(True, True)
root.configure(bg='#f0f0f0') # Fondo general de la ventana

# Establecer el ícono de la ventana
try:
    root.iconbitmap(resource_path("images/smontyaragon.ico"))
except Exception:
    pass  # Ignorar si el ícono no se encuentra (en desarrollo)

# Estilo moderno
style = ttk.Style(root)
style.theme_use('clam')  # Tema 'clam' para un look moderno

# Estilo para el título
style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), foreground="#333", background='#f0f0f0')

# Estilo base para los botones (Aumentando el tamaño de la fuente y el padding)
style.configure("Base.TButton", font=("Helvetica", 14), padding=(15, 12), relief="flat", background="#e0e0e0", foreground="#333") # Aumentado font y padding
style.map("Base.TButton",
    background=[("active", "#d0d0d0")],
    relief=[("active", "raised")]
)

# Estilo específico para botones de descarga (azul claro)
style.configure("Descargar.TButton", parent="Base.TButton", background="#cce0ff", foreground="#003366")
style.map("Descargar.TButton",
    background=[("active", "#b3d1ff")],
    foreground=[("active", "#003366")]
)

# Estilo específico para botones de abrir (verde claro)
style.configure("Abrir.TButton", parent="Base.TButton", background="#ccffcc", foreground="#006600")
style.map("Abrir.TButton",
    background=[("active", "#b3ffb3")],
    foreground=[("active", "#006600")]
)

# Estilo para la imagen de fondo del Label (para que se vea bien con el fondo de la ventana)
style.configure("ImageLabel.TLabel", background='#f0f0f0')


# Etiqueta de título
titulo = ttk.Label(root, text="S&A - Reportes y Requerimientos", style="Title.TLabel")
titulo.pack(pady=20)

# Cargar la imagen
try:
    image = Image.open(resource_path("images/smontyaragon.png"))
    photo = ImageTk.PhotoImage(image)
    label_imagen = ttk.Label(root, image=photo, style="ImageLabel.TLabel")
    label_imagen.image = photo  # Mantener referencia para evitar que el recolector de basura la elimine
    label_imagen.pack(pady=15)
except Exception:
    pass  # Ignorar si la imagen no se encuentra

# Crear la carpeta 'reportes' al inicio de la aplicación
crear_carpeta_reportes()

# Contenedor de botones
frame_botones = ttk.Frame(root)
frame_botones.pack(pady=20)

# Botón para descargar el archivo Excel de Reporte Diario
btn_descargar = ttk.Button(frame_botones, text="Descargar Reporte Diario", command=on_descargar, style="Descargar.TButton")
btn_descargar.grid(row=0, column=0, padx=10, pady=5)

# Botón para abrir el archivo Excel de Reporte Diario
btn_abrir = ttk.Button(frame_botones, text="Abrir Reporte Diario", command=on_abrir, style="Abrir.TButton")
btn_abrir.grid(row=0, column=1, padx=10, pady=5)

# Botón para descargar el archivo Excel de Requerimientos
btn_descargar_requerimientos = ttk.Button(frame_botones, text="Descargar Requerimientos", command=on_descargar_requerimientos, style="Descargar.TButton")
btn_descargar_requerimientos.grid(row=1, column=0, padx=10, pady=5)

# Botón para abrir el archivo Excel de Requerimientos
btn_abrir_requerimientos = ttk.Button(frame_botones, text="Abrir Requerimientos", command=on_abrir_requerimientos, style="Abrir.TButton")
btn_abrir_requerimientos.grid(row=1, column=1, padx=10, pady=5)

# Mostrar la ventana
root.mainloop()