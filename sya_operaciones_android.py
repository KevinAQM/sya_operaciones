from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from datetime import datetime
import requests
import json

# Establecer colores de fondo de la ventana
Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Fondo negro

class ReporteObraApp(App):
    title = "Parte Diario de Obra"

    def build(self):
        # Contenedor principal
        self.root_widget = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Crear ScrollView para el formulario
        scroll = ScrollView(size_hint=(1, 0.9))

        # Crear un layout para el formulario
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=10)
        form_layout.bind(minimum_height=form_layout.setter("height"))
        
        # Diccionario para almacenar las respuestas
        self.respuestas = {}
        
        # Lista de campos del formulario
        self.campos = [
            {"nombre": "codigo_obra", "tipo": "text", "etiqueta": "Código de Obra"},
            {"nombre": "nombre_obra", "tipo": "text", "etiqueta": "Nombre de Obra"},
            {"nombre": "codigo_ingeniero", "tipo": "text", "etiqueta": "Código de Ingeniero"},
            {"nombre": "nombre_ingeniero", "tipo": "text", "etiqueta": "Nombre del Ingeniero"},
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
            # Crear un espacio pequeño antes de cada etiqueta
            form_layout.add_widget(Widget(size_hint_y=None, height=5))  # Espacio pequeño
            
            # Crear etiqueta
            label = Label(
                text=campo["etiqueta"],
                size_hint=(None, None),
                size=(400, 20),
                pos_hint={'center_x': 0.5},
                color=(0.9, 0.9, 1, 1),  # Azul claro
                font_size=18
            )
            form_layout.add_widget(label)
            
            # Crear input según el tipo
            if campo["tipo"] == "bool":
                input_widget = Spinner(
                    text='Sí',
                    values=('Sí', 'No'),
                    size_hint=(None, None),
                    size=(400, 40),
                    pos_hint={'center_x': 0.5},
                    background_color=(0.75, 0.75, 0.75, 1),  # Gris claro
                    color=(1, 1, 1, 1)  # Blanco
                )
            else:
                input_widget = TextInput(
                    multiline=False,
                    size_hint=(None, None),
                    size=(400, 40),
                    pos_hint={'center_x': 0.5},
                    background_color=(1, 1, 1, 1),  # Blanco
                    foreground_color=(0, 0, 0, 1)  # Negro
                )
                if campo["nombre"] == "fecha":
                    input_widget.text = datetime.now().strftime('%d/%m/%Y')
            
            self.respuestas[campo["nombre"]] = input_widget
            form_layout.add_widget(input_widget)

        # Agregar espacio antes del botón de envío
        form_layout.add_widget(Widget(size_hint_y=None, height=10))  # Espacio antes del botón 

        # Botón de envío
        btn_enviar = Button(
            text='Enviar Datos',
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={'center_x': 0.5},
            background_color=(0, 0.5, 1, 1),  # Azul intenso
            color=(1, 1, 1, 1),  # Blanco
            on_press=self.confirmar_envio
        )
        form_layout.add_widget(btn_enviar)

        # Agregar el formulario al ScrollView
        scroll.add_widget(form_layout)

        # Agregar el ScrollView al layout principal
        self.root_widget.add_widget(scroll)

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
                    json=datos,
                    timeout=10
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
            if campo["nombre"] == "fecha":
                try:
                    datetime.strptime(valor, '%d/%m/%Y')
                except ValueError:
                    print("Formato de fecha inválido. Use DD/MM/YYYY.")
                    return False
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
