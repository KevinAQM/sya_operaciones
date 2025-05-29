import os
import subprocess
import sys
import requests
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk

# Configuración DPI para Windows
if sys.platform == "win32":
    try:
        import ctypes
        # For Windows 10 version 1607 and later: PROCESS_PER_MONITOR_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (ImportError, AttributeError):
        try:
            # For Windows 8.1 and earlier:
            ctypes.windll.user32.SetProcessDPIAware()
        except (ImportError, AttributeError):
            pass

# Configuración para el manejo de imágenes
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

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

def abrir_archivo(ruta_archivo):
    """Abre un archivo con la aplicación predeterminada del sistema."""
    try:
        if sys.platform == 'win32':
            os.startfile(ruta_archivo)
        else:
            # Para macOS y Linux usamos subprocess
            if sys.platform == 'darwin':  # macOS
                cmd = ['open', ruta_archivo]
            else:  # Linux
                cmd = ['xdg-open', ruta_archivo]
            subprocess.call(cmd)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir el archivo: {e}")
        return False

def descargar_excel(url, nombre_archivo, status_callback=None):
    """
    Función para descargar un archivo Excel desde una URL y guardarlo en la carpeta 'reportes'.
    """
    try:
        if status_callback:
            status_callback("Descargando archivo...")
            
        respuesta = requests.get(url, stream=True, timeout=30)
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

        if status_callback:
            status_callback(f"Archivo descargado: {nombre_archivo}")
        messagebox.showinfo("Descarga completada", f"Archivo '{nombre_archivo}' descargado exitosamente en:\n{nombre_archivo_completo}")
        return True
    except requests.exceptions.RequestException as e:
        if status_callback:
            status_callback("Error al descargar el archivo")
        messagebox.showerror("Error de descarga", f"Error al descargar el archivo:\n{e}")
        return False

def abrir_excel(nombre_archivo, status_callback=None):
    """
    Función para abrir el archivo Excel descargado desde la carpeta 'reportes'.
    """
    ruta_app = obtener_ruta_aplicacion()
    ruta_reportes = os.path.join(ruta_app, "reportes")
    nombre_archivo_completo = os.path.join(ruta_reportes, nombre_archivo)

    if os.path.exists(nombre_archivo_completo):
        if abrir_archivo(nombre_archivo_completo):
            if status_callback:
                status_callback(f"Archivo abierto: {nombre_archivo}")
    else:
        if status_callback:
            status_callback("Archivo no encontrado")
        messagebox.showerror("Error", "El archivo no existe. Por favor, descárguelo primero.")

class SyaOperacionesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("S&A - Area Operaciones")
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        
        # Configuración del icono
        try:
            self.root.iconbitmap(resource_path("images/smontyaragon.ico"))
        except Exception:
            pass
        
        # Configurar estilos
        self.configurar_estilos()
        
        # Crear carpeta de reportes
        crear_carpeta_reportes()
        
        # Inicializar la interfaz
        self.inicializar_interfaz()
        
        # Ajustar el tamaño mínimo de la ventana
        root.update_idletasks()
        root.minsize(int(root.winfo_reqwidth()*1.30), root.winfo_reqheight())
    
    def configurar_estilos(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style(self.root)
        style.theme_use('clam')

        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), foreground="#333", background='#f0f0f0')

        style.configure("Base.TButton", font=("Helvetica", 14), padding=(15, 12), relief="flat", background="#e0e0e0", foreground="#333")
        style.map("Base.TButton",
                background=[("active", "#f0f0f0")],
                relief=[("active", "raised")]
                )

        style.configure("Descargar.TButton", parent="Base.TButton", background="#cce0ff", foreground="#003366")
        style.map("Descargar.TButton",
                background=[("active", "#b3d1ff")],
                foreground=[("active", "#003366")]
                )

        style.configure("Abrir.TButton", parent="Base.TButton", background="#90EE90", foreground="#006400") # Verde claro
        style.map("Abrir.TButton",
                background=[("active", "#7FFFD4")], # Acuamarine
                foreground=[("active", "#006400")]
                )

        style.configure("General.TButton", parent="Base.TButton", background="#FFE4B5", foreground="#8B4513") # Beige
        style.map("General.TButton",
                background=[("active", "#FFDAB9")], # Peach Puff
                foreground=[("active", "#8B4513")]
                )
    
    def inicializar_interfaz(self):
        """Inicializa todos los componentes de la interfaz."""
        # Título
        titulo = ttk.Label(self.root, text="S&A - Area Operaciones", style="Title.TLabel")
        titulo.pack(pady=20)
        
        # Cargar logo
        self.cargar_logo()
        
        # Frame principal para botones
        frame_botones_principal = ttk.Frame(self.root)
        frame_botones_principal.pack(pady=20, fill='x', expand=True)
        
        # Sección Reportes Diarios
        frame_reportes = ttk.LabelFrame(frame_botones_principal, text="Reportes Diarios", padding=(10, 5))
        frame_reportes.pack(pady=10, padx=10, fill='x')

        btn_descargar_reporte = ttk.Button(
            frame_reportes, 
            text="Descargar Reporte Diario", 
            command=self.on_descargar, 
            style="Descargar.TButton"
        )
        btn_descargar_reporte.pack(side='left', padx=5, expand=True, fill='x')

        btn_abrir_reporte = ttk.Button(
            frame_reportes, 
            text="Abrir Reporte Diario", 
            command=self.on_abrir, 
            style="Abrir.TButton"
        )
        btn_abrir_reporte.pack(side='left', padx=5, expand=True, fill='x')
        
        # Sección Requerimientos
        frame_requerimientos = ttk.LabelFrame(frame_botones_principal, text="Requerimientos de Obra", padding=(10, 5))
        frame_requerimientos.pack(pady=10, padx=10, fill='x')

        btn_descargar_req = ttk.Button(
            frame_requerimientos, 
            text="Descargar Requerimientos", 
            command=self.on_descargar_requerimientos, 
            style="Descargar.TButton"
        )
        btn_descargar_req.pack(side='left', padx=5, pady=5, expand=True, fill='x')

        btn_abrir_req = ttk.Button(
            frame_requerimientos, 
            text="Abrir Requerimientos", 
            command=self.on_abrir_requerimientos, 
            style="Abrir.TButton"
        )
        btn_abrir_req.pack(side='left', padx=5, pady=5, expand=True, fill='x')
        
        # Sección General
        frame_general = ttk.LabelFrame(frame_botones_principal, text="General", padding=(10, 5))
        frame_general.pack(pady=10, padx=10, fill='x')

        btn_abrir_carpeta = ttk.Button(
            frame_general, 
            text="Abrir Carpeta Reportes", 
            command=self.abrir_carpeta_reportes, 
            style="General.TButton"
        )
        btn_abrir_carpeta.pack(padx=5, expand=True, fill='x')
        
        # Etiqueta de estado
        self.status_label = ttk.Label(self.root, text="Listo", font=("Helvetica", 10), background="#f0f0f0")
        self.status_label.pack(side=tk.BOTTOM, pady=10)
    
    def cargar_logo(self):
        """Carga e inserta el logo de la empresa."""
        if PIL_AVAILABLE:
            try:
                image = Image.open(resource_path("images/smontyaragon.png"))
                photo = ImageTk.PhotoImage(image)
                label_imagen = ttk.Label(self.root, image=photo)
                label_imagen.image = photo
                label_imagen.pack(pady=15)
            except Exception:
                # Si no se puede cargar la imagen, mostrar un texto alternativo
                label_texto = ttk.Label(self.root, text="S&A Operaciones", font=("Helvetica", 20, "bold"), foreground="#0066cc")
                label_texto.pack(pady=15)
        else:
            # Si PIL no está disponible, mostrar un texto alternativo
            label_texto = ttk.Label(self.root, text="S&A Operaciones", font=("Helvetica", 20, "bold"), foreground="#0066cc")
            label_texto.pack(pady=15)
    
    def actualizar_estado(self, texto):
        """Actualiza el texto del label de estado."""
        self.status_label.config(text=texto)
        self.root.update()
    
    def on_descargar(self):
        """
        Evento del botón 'Descargar Reporte Diario'.
        """
        self.actualizar_estado("Descargando reporte diario...")
        url_servidor = "http://34.67.103.132:5000/descargar-excel"  # URL del servidor
        # Se especifica solo el nombre del archivo para colocarlo dentro de la carpeta 'reportes'
        nombre_archivo_local = "reportes_parte_diario.xlsx"
        descargar_excel(url_servidor, nombre_archivo_local, self.actualizar_estado)

    def on_abrir(self):
        """
        Evento del botón 'Abrir Reporte Diario'.
        """
        nombre_archivo_local = "reportes_parte_diario.xlsx"
        abrir_excel(nombre_archivo_local, self.actualizar_estado)

    def on_descargar_requerimientos(self):
        """
        Evento del botón 'Descargar Requerimientos'.
        """
        self.actualizar_estado("Descargando requerimientos...")
        url_servidor = "http://34.67.103.132:5000/descargar-requerimientos-excel"  # URL del servidor para requerimientos
        nombre_archivo_local = "requerimientos_obra.xlsx"
        descargar_excel(url_servidor, nombre_archivo_local, self.actualizar_estado)

    def on_abrir_requerimientos(self):
        """
        Evento del botón 'Abrir Requerimientos'.
        """
        nombre_archivo_local = "requerimientos_obra.xlsx"
        abrir_excel(nombre_archivo_local, self.actualizar_estado)
    
    def abrir_carpeta_reportes(self):
        """Abre la carpeta de reportes."""
        ruta_reportes = crear_carpeta_reportes()
        try:
            if abrir_archivo(ruta_reportes):
                self.actualizar_estado("Carpeta de reportes abierta")
        except Exception as e:
            self.actualizar_estado("Error al abrir la carpeta")
            messagebox.showerror("Error", f"Ocurrió un error al abrir la carpeta de reportes:\n{e}")


# Punto de entrada principal
def main():
    """Inicializa y ejecuta la aplicación principal."""
    root = tk.Tk()
    app = SyaOperacionesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()