import tkinter as tk
from tkinter import ttk, messagebox
from flask import Flask, request, jsonify, send_file
import threading
import openpyxl
from datetime import datetime
import os

app = Flask(__name__)
EXCEL_FILE = "registros_trabajo.xlsx"

class AplicacionDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Registro de Operaciones")

        # Crear frame principal
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Área de log
        self.log_text = tk.Text(self.frame, height=10, width=50)
        self.log_text.grid(row=0, column=0, pady=10)

        # Botón para abrir Excel
        self.btn_excel = ttk.Button(
            self.frame,
            text="Abrir Excel",
            command=self.abrir_excel
        )
        self.btn_excel.grid(row=1, column=0, pady=5)

        # Inicializar Excel si no existe
        self.inicializar_excel()

    def inicializar_excel(self):
        if not os.path.exists(EXCEL_FILE):
            wb = openpyxl.Workbook()
            ws = wb.active
            # Definir encabezados
            headers = [
                "Fecha Registro", "Código Ingeniero", "Nombre Ingeniero",
                "Código Obra", "Fecha Trabajo", "Cantidad Material 1",
                "Cantidad Material 2", "Equipo 1 Usado", "Equipo 2 Usado",
                "Número Trabajadores", "Horas Trabajo", "Área Trabajada",
                "Calidad Trabajo", "Incidentes", "Clima",
                "Equipos Seguridad", "Supervisor Presente", "Material Restante",
                "Tiempo Descanso", "Observaciones", "Plan Siguiente Día"
            ]
            ws.append(headers)
            wb.save(EXCEL_FILE)

    def agregar_log(self, mensaje):
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {mensaje}\n")
        self.log_text.see(tk.END)

    def abrir_excel(self):
        try:
            os.startfile(EXCEL_FILE)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir Excel: {str(e)}")

    def procesar_datos(self, datos):
        try:
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active

            # Preparar fila de datos
            fila = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datos.get('codigo_ingeniero', ''),
                datos.get('nombre_ingeniero', ''),
                datos.get('codigo_obra', ''),
                datos.get('fecha', ''),
                datos.get('cantidad_material1', 0),
                datos.get('cantidad_material2', 0),
                'Sí' if datos.get('equipo1_usado', False) else 'No',
                'Sí' if datos.get('equipo2_usado', False) else 'No',
                datos.get('num_trabajadores', 0),
                datos.get('horas_trabajo', 0),
                datos.get('area_trabajada', 0),
                datos.get('calidad_trabajo', ''),
                'Sí' if datos.get('incidentes', False) else 'No',
                datos.get('clima', ''),
                'Sí' if datos.get('equipos_seguridad', False) else 'No',
                'Sí' if datos.get('supervisor_presente', False) else 'No',
                datos.get('material_restante', 0),
                datos.get('tiempo_descanso', 0),
                datos.get('observaciones', ''),
                datos.get('siguiente_dia', '')
            ]

            ws.append(fila)
            wb.save(EXCEL_FILE)

            self.agregar_log(f"Datos recibidos de {datos.get('nombre_ingeniero', 'Unknown')} procesados exitosamente")

        except Exception as e:
            self.agregar_log(f"Error al procesar datos: {str(e)}")

    def descargar_excel_flask(self):
        try:
            return send_file(EXCEL_FILE, as_attachment=True)
        except Exception as e:
            self.agregar_log(f"Error al generar descarga de Excel: {str(e)}")
            return str(e), 500  # Devuelve un código de error 500

def iniciar_servidor(app_desktop):
    @app.route('/recibir-datos', methods=['POST'])
    def recibir_datos():
        datos = request.json
        app_desktop.procesar_datos(datos)
        return jsonify({"status": "success"})

    # La ruta se asocia a un método de la clase AplicacionDesktop
    @app.route('/descargar-excel')
    def descargar_excel_route():
        return app_desktop.descargar_excel_flask()

    app.run(host='0.0.0.0', port=5000) # Modificado para escuchar en todas las interfaces

def main():
    root = tk.Tk()
    app_desktop = AplicacionDesktop(root)

    # Iniciar servidor Flask en un hilo separado
    servidor_thread = threading.Thread(
        target=iniciar_servidor,
        args=(app_desktop,),
        daemon=True
    )
    servidor_thread.start()

    root.mainloop()

if __name__ == '__main__':
    main()