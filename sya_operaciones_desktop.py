import requests

def descargar_excel(url, nombre_archivo):
    try:
        respuesta = requests.get(url, stream=True)
        respuesta.raise_for_status()  # Lanza una excepción si la solicitud falla

        with open(nombre_archivo, 'wb') as archivo:
            for chunk in respuesta.iter_content(chunk_size=8192):
                archivo.write(chunk)

        print(f"Archivo '{nombre_archivo}' descargado exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo: {e}")

if __name__ == "__main__":
    url_servidor = "http://34.82.57.55:5000/descargar-excel"  # Reemplazar con IP del servidor de la nube
    nombre_archivo_local = "registros_trabajo_descargado.xlsx"
    descargar_excel(url_servidor, nombre_archivo_local)