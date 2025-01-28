from flask import Flask, request, jsonify, send_file
import threading
import openpyxl
from datetime import datetime
import os
import logging
import pandas as pd

app = Flask(__name__)
EXCEL_FILE = "registros_trabajo.xlsx"
MATERIALES_CSV_PATH = "operaciones_materiales.csv"  # Ruta al archivo de materiales

# Configuración de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def inicializar_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = openpyxl.Workbook()
        ws = wb.active
        # Definir encabezados
        headers = [
            "Fecha Registro", "Código Obra", "Nombre Obra",
            "Código Ingeniero", "Nombre Ingeniero",
            "Fecha Trabajo", "Cantidad Material 1",
            "Cantidad Material 2", "Equipo 1 Usado", "Equipo 2 Usado",
            "Número Trabajadores", "Horas Trabajo", "Área Trabajada",
            "Calidad Trabajo", "Incidentes", "Clima",
            "Equipos Seguridad", "Supervisor Presente", "Material Restante",
            "Tiempo Descanso", "Observaciones", "Plan Siguiente Día"
        ]
        ws.append(headers)
        wb.save(EXCEL_FILE)

def procesar_datos(datos):
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active

        # Preparar fila de datos
        fila = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datos.get('codigo_obra', ''),
            datos.get('nombre_obra', ''),
            datos.get('codigo_ingeniero', ''),
            datos.get('nombre_ingeniero', ''),
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

        logging.info(f"Datos recibidos de {datos.get('nombre_ingeniero', 'Unknown')} procesados exitosamente")

    except Exception as e:
        logging.error(f"Error al procesar datos: {str(e)}")

def descargar_excel_flask():
    try:
        return send_file(EXCEL_FILE, as_attachment=True)
    except Exception as e:
        logging.error(f"Error al generar descarga de Excel: {str(e)}")
        return str(e), 500

# Inicializar Excel al inicio
inicializar_excel()

@app.route('/api/materiales', methods=['GET'])
def get_materiales():
    try:
        df = pd.read_csv(MATERIALES_CSV_PATH)
        materiales = df.to_dict(orient='records')
        return jsonify(materiales)
    except FileNotFoundError:
        return jsonify({"error": "No se encontró el archivo de materiales"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recibir-datos', methods=['POST'])
def recibir_datos():
    datos = request.json
    procesar_datos(datos)
    return jsonify({"status": "success"})

@app.route('/descargar-excel', methods=['GET'])
def descargar_excel_route():
    return descargar_excel_flask()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 