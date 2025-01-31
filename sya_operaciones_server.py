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
EQUIPOS_CSV_PATH = os.path.join(BASE_DIR, "operaciones_equipos.csv")
VEHICULOS_CSV_PATH = os.path.join(BASE_DIR, "operaciones_vehiculos.csv")

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

        # Hoja "Equipos Usados"
        ws3 = wb.create_sheet(title="Equipos Usados")
        headers_equipos = [
            "Fecha", "Código Obra", "Nombre Ingeniero"
        ]
        ws3.append(headers_equipos)

        # Hoja "Vehículos Usados"
        ws4 = wb.create_sheet(title="Vehículos Usados")  # Nueva línea
        headers_vehiculos = [  # Nueva línea
            "Fecha", "Código Obra", "Nombre Ingeniero"  # Nueva línea
        ]  # Nueva línea
        ws4.append(headers_vehiculos)  # Nueva línea

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

def actualizar_cabeceras_equipos(ws, num_equipos):
    headers = ws[1]
    num_headers_actuales = len(headers)

    ultimo_equipo = 0
    for header in headers:
        header_value = header.value
        if header_value and header_value.startswith("Equipo"):
            try:
                numero = int(header_value.split(" ")[1])
                ultimo_equipo = max(ultimo_equipo, numero)
            except ValueError:
                pass

    if ultimo_equipo >= num_equipos:
        return

    for i in range(ultimo_equipo + 1, num_equipos + 1):
        ws.cell(row=1, column=num_headers_actuales + 1, value=f"Equipo {i}")
        ws.cell(row=1, column=num_headers_actuales + 2, value=f"Cantidad {i}")
        ws.cell(row=1, column=num_headers_actuales + 3, value=f"Propiedad {i}")
        num_headers_actuales += 3

def actualizar_cabeceras_vehiculos(ws, num_vehiculos):  # Nueva función
    headers = ws[1]
    num_headers_actuales = len(headers)

    ultimo_vehiculo = 0
    for header in headers:
        header_value = header.value
        if header_value and header_value.startswith("Vehículo"):
            try:
                numero = int(header_value.split(" ")[1])
                ultimo_vehiculo = max(ultimo_vehiculo, numero)
            except ValueError:
                pass

    if ultimo_vehiculo >= num_vehiculos:
        return

    for i in range(ultimo_vehiculo + 1, num_vehiculos + 1):
        ws.cell(row=1, column=num_headers_actuales + 1, value=f"Vehículo {i}")
        ws.cell(row=1, column=num_headers_actuales + 2, value=f"Placa {i}")
        ws.cell(row=1, column=num_headers_actuales + 3, value=f"Propiedad {i}")
        num_headers_actuales += 3

def procesar_datos(datos):
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws_reporte = wb["Reporte Principal"]
        ws_materiales = wb["Materiales Usados"]
        ws_equipos = wb["Equipos Usados"]
        ws_vehiculos = wb["Vehículos Usados"]  # Nueva línea


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

        # Procesar equipos usados
        equipos = datos.get('equipos_usados', [])
        actualizar_cabeceras_equipos(ws_equipos, len(equipos))
        fila_equipos = [
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(),
            datos.get('codigo_obra', ''),
            datos.get('nombre_ingeniero', '')
        ]
        for equipo in equipos:
            fila_equipos.extend([equipo['nombre'], equipo['cantidad'], equipo['propiedad']])
        ws_equipos.append(fila_equipos)

        # Procesar vehículos usados
        vehiculos = datos.get('vehiculos_usados', [])  # Nueva línea
        actualizar_cabeceras_vehiculos(ws_vehiculos, len(vehiculos))  # Nueva línea
        fila_vehiculos = [  # Nueva línea
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(),  # Nueva línea
            datos.get('codigo_obra', ''),  # Nueva línea
            datos.get('nombre_ingeniero', '')  # Nueva línea
        ]  # Nueva línea
        for vehiculo in vehiculos:  # Nueva línea
            fila_vehiculos.extend([vehiculo['nombre'], vehiculo['placa'], vehiculo['propiedad']])  # Nueva línea
        ws_vehiculos.append(fila_vehiculos)  # Nueva línea

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

@app.route('/api/equipos', methods=['GET']) # Nuevo endpoint
def get_equipos():
    try:
        df = pd.read_csv(EQUIPOS_CSV_PATH)
        equipos = df.to_dict(orient='records')
        return jsonify(equipos)
    except FileNotFoundError:
        return jsonify({"error": f"No se encontró el archivo de equipos en {EQUIPOS_CSV_PATH}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehiculos', methods=['GET'])  # Nuevo endpoint
def get_vehiculos():
    try:
        df = pd.read_csv(VEHICULOS_CSV_PATH)
        vehiculos = df.to_dict(orient='records')
        return jsonify(vehiculos)
    except FileNotFoundError:
        return jsonify({"error": f"No se encontró el archivo de vehículos en {VEHICULOS_CSV_PATH}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recibir-datos', methods=['POST'])z
def recibir_datos():
    datos = request.json
    procesar_datos(datos)
    return jsonify({"status": "success"})

@app.route('/descargar-excel', methods=['GET'])
def descargar_excel_route():
    return descargar_excel_flask()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)