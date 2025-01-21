from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from datetime import datetime
import requests
import json

class ReporteObraApp(App):
    def build(self):
        # Contenedor principal
        self.root_widget = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Crear ScrollView para el formulario
        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Diccionario para almacenar las respuestas
        self.respuestas = {}
        
        # Lista de campos del formulario
        self.campos = [
            {"nombre": "codigo_ingeniero", "tipo": "text", "etiqueta": "Código de Ingeniero"},
            {"nombre": "nombre_ingeniero", "tipo": "text", "etiqueta": "Nombre del Ingeniero"},
            {"nombre": "codigo_obra", "tipo": "text", "etiqueta": "Código de Obra"},
            {"nombre": "fecha", "tipo": "date", "etiqueta": "Fecha"},
            {"nombre": "cantidad_material1", "tipo": "float", "etiqueta": "Cantidad Material 1 (kg)"},
            {"nombre": "cantidad_material2", "tipo": "float", "etiqueta": "Cantidad Material 2 (L)"},
            {"nombre": "equipo1_usado", "tipo": "bool", "etiqueta": "¿Se usó Equipo 1?"},
            {"nombre": "equipo2_usado", "tipo": "bool", "etiqueta": "¿Se usó Equipo 2?"},
            {"nombre": "num_trabajadores", "tipo": "float", "etiqueta": "Número de Trabajadores"},
            {"nombre": "horas_trabajo", "tipo": "float", "etiqueta": "Horas de Trabajo"},
            {"nombre": "area_trabajada", "tipo": "float", "etiqueta": "Área Trabajada (m²)"},
            {"nombre": "calidad_trabajo", "tipo": "text", "etiqueta": "Calidad del Trabajo"},
            {"nombre": "incidentes", "tipo": "bool", "etiqueta": "¿Hubo Incidentes?"},
            {"nombre": "clima", "tipo": "text", "etiqueta": "Condiciones Climáticas"},
            {"nombre": "equipos_seguridad", "tipo": "bool", "etiqueta": "¿Equipos de Seguridad Completos?"},
            {"nombre": "supervisor_presente", "tipo": "bool", "etiqueta": "¿Supervisor Presente?"},
            {"nombre": "material_restante", "tipo": "float", "etiqueta": "Material Restante (kg)"},
            {"nombre": "tiempo_descanso", "tipo": "float", "etiqueta": "Tiempo de Descanso (min)"},
            {"nombre": "observaciones", "tipo": "text", "etiqueta": "Observaciones"},
            {"nombre": "siguiente_dia", "tipo": "text", "etiqueta": "Plan para Siguiente Día"}
        ]
        
        # Crear campos del formulario
        for campo in self.campos:
            # Crear etiqueta
            label = Label(text=campo["etiqueta"], size_hint_y=None, height=30)
            form_layout.add_widget(label)
            
            # Crear input según el tipo
            if campo["tipo"] == "bool":
                input_widget = Spinner(
                    text='No',
                    values=('Sí', 'No'),
                    size_hint_y=None,
                    height=40
                )
            else:
                input_widget = TextInput(
                    multiline=False,
                    size_hint_y=None,
                    height=40
                )
            
            self.respuestas[campo["nombre"]] = input_widget
            form_layout.add_widget(input_widget)
        
        # Botón de envío
        btn_enviar = Button(
            text='Enviar Datos',
            size_hint_y=None,
            height=50
        )
        btn_enviar.bind(on_press=self.confirmar_envio)
        
        # Agregar todo al layout principal
        scroll.add_widget(form_layout)
        self.root_widget.add_widget(scroll)
        self.root_widget.add_widget(btn_enviar)
        
        return self.root_widget
    
    def confirmar_envio(self, instance):
        # Validar datos
        datos_validos = self.validar_datos()
        if datos_validos:
            # Crear diccionario con los datos
            datos = {}
            for campo in self.campos:
                valor = self.respuestas[campo["nombre"]].text
                if campo["tipo"] == "float":
                    try:
                        valor = float(valor)
                    except ValueError:
                        valor = 0.0
                elif campo["tipo"] == "bool":
                    valor = valor == "Sí"
                datos[campo["nombre"]] = valor
            
            # Agregar fecha y hora actual
            datos["timestamp"] = datetime.now().isoformat()
            
            # Enviar datos al servidor
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/recibir-datos",
                    json=datos
                )
                if response.status_code == 200:
                    print("Datos enviados exitosamente")
                else:
                    print("Error al enviar datos")
            except Exception as e:
                print(f"Error de conexión: {e}")
    
    def validar_datos(self):
        for campo in self.campos:
            valor = self.respuestas[campo["nombre"]].text
            if not valor:
                return False
            if campo["tipo"] == "float":
                try:
                    float(valor)
                except ValueError:
                    return False
        return True


if __name__ == '__main__':
    ReporteObraApp().run()