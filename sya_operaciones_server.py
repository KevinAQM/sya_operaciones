from flask import Flask, request, jsonify, send_file
import openpyxl
from datetime import datetime
import os
import logging
import pandas as pd

app = Flask(__name__)

# Usar una ruta absoluta para el archivo Excel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "registros_trabajo.xlsx")
MATERIALES_CSV_PATH = os.path.join(BASE_DIR, "operaciones_materiales.csv")

# Configuración de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def inicializar_excel():
    if not os.path.exists(EXCEL_FILE):
        logging.info(f"Creando archivo Excel en: {EXCEL_FILE}")
        wb = openpyxl.Workbook()
        # Hoja "Reporte Principal"
        ws1 = wb.active
        ws1.title = "Reporte Principal"
        headers_reporte = [
            "Fecha", "Código Obra", "Nombre Ingeniero",
            "Nombre Supervisor", "Actividad Principal",
            "Supervisor Presente", "Equipos Seguridad Completos",
            "Incidentes", "Plan Siguiente Día", "Observaciones"
        ]
        ws1.append(headers_reporte)

        # Hoja "Materiales Usados"
        ws2 = wb.create_sheet(title="Materiales Usados")
        headers_materiales = [
            "Fecha", "Código Obra", "Nombre Ingeniero"
        ]
        ws2.append(headers_materiales)

        wb.save(EXCEL_FILE)
    else:
        logging.info(f"El archivo Excel ya existe en: {EXCEL_FILE}")

def actualizar_cabeceras_materiales(ws, num_materiales):
    headers = ws[1]  # Obtener la primera fila (cabeceras)
    num_headers_actuales = len(headers)

    # Encontrar el último número de material existente
    ultimo_material = 0
    for header in headers:
        header_value = header.value
        if header_value and header_value.startswith("Material"):
            try:
                numero = int(header_value.split(" ")[1])
                ultimo_material = max(ultimo_material, numero)
            except ValueError:
                pass

    # Si ya hay suficientes cabeceras, no hacer nada
    # Se verifica que el ultimo material ya sea mayor o igual a num_materiales
    if ultimo_material >= num_materiales:
        return

    # Agregar las cabeceras faltantes
    # Se itera solo hasta num_materiales
    for i in range(ultimo_material + 1, num_materiales + 1):
        ws.cell(row=1, column=num_headers_actuales + 1, value=f"Material {i}")
        ws.cell(row=1, column=num_headers_actuales + 2, value=f"Unidad {i}")
        ws.cell(row=1, column=num_headers_actuales + 3, value=f"Cantidad {i}")
        num_headers_actuales += 3

def procesar_datos(datos):
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws_reporte = wb["Reporte Principal"]
        ws_materiales = wb["Materiales Usados"]

        # Preparar fila de datos para "Reporte Principal"
        fila_reporte = [
            # Formatear la fecha como DATE en "Reporte Principal"
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(),  # Fecha como date
            datos.get('codigo_obra', ''),
            datos.get('nombre_ingeniero', ''),
            datos.get('nombre_supervisor', ''),
            datos.get('actividad_principal', ''),
            'Sí' if datos.get('supervisor_presente', False) else 'No',
            'Sí' if datos.get('equipos_seguridad', False) else 'No',
            datos.get('incidentes', ''),
            datos.get('siguiente_dia', ''),
            datos.get('observaciones', '')
        ]
        ws_reporte.append(fila_reporte)

        # Procesar materiales usados para "Materiales Usados"
        materiales = datos.get('materiales_usados', [])

        # Actualizar cabeceras de materiales si es necesario
        actualizar_cabeceras_materiales(ws_materiales, len(materiales))

        fila_materiales = [
            # Convertir la fecha al formato correcto para "Materiales Usados"
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(),
            datos.get('codigo_obra', ''),
            datos.get('nombre_ingeniero', '')
        ]
        for material in materiales:
            fila_materiales.extend([material['nombre'], material['unidad'], material['cantidad']])
        ws_materiales.append(fila_materiales)

        wb.save(EXCEL_FILE)

        logging.info(f"Datos recibidos de {datos.get('nombre_ingeniero', 'Unknown')} procesados exitosamente")

    except Exception as e:
        logging.error(f"Error al procesar datos: {str(e)}")

def descargar_excel_flask():
    try:
        logging.info(f"Intentando enviar archivo: {EXCEL_FILE}")
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
        return jsonify({"error": f"No se encontró el archivo de materiales en {MATERIALES_CSV_PATH}"}), 404
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