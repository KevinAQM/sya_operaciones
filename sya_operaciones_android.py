from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from datetime import datetime
import requests
import json
import pandas as pd

# Establecer colores de fondo de la ventana
Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Fondo negro

class CustomDropDown(DropDown):
    def __init__(self, **kwargs):
        super(CustomDropDown, self).__init__(**kwargs)
        self.auto_width = False
        self.width = 400

class ReporteObraApp(App):
    title = "Parte Diario de Obra"

    def build(self):
        # Cargar lista de materiales desde el servidor al iniciar la app
        self.get_materiales_from_server()

        # Contenedor principal
        self.root_widget = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Crear ScrollView para el formulario
        scroll = ScrollView(size_hint=(1, 0.9))

        # Crear un layout para el formulario
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=10)
        form_layout.bind(minimum_height=form_layout.setter("height"))
        
        # Diccionario para almacenar las respuestas
        self.respuestas = {}
        self.materiales_seleccionados = []  # Lista para almacenar los materiales seleccionados
        
        # Lista de campos del formulario
        self.campos = [
            {"nombre": "codigo_obra", "tipo": "text", "etiqueta": "Código de Obra"},
            {"nombre": "nombre_obra", "tipo": "text", "etiqueta": "Nombre de Obra"},
            {"nombre": "codigo_ingeniero", "tipo": "text", "etiqueta": "Código de Ingeniero"},
            {"nombre": "nombre_ingeniero", "tipo": "text", "etiqueta": "Nombre del Ingeniero"},
            {"nombre": "fecha", "tipo": "date", "etiqueta": "Fecha"},
            {"nombre": "materiales_usados", "tipo": "material", "etiqueta": "Materiales Usados"},
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
                color=(1, 1, 1, 1),
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
                self.respuestas[campo["nombre"]] = input_widget
                form_layout.add_widget(input_widget)
            elif campo["tipo"] == "material":
                self.setup_material_input(form_layout)

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

    def get_materiales_from_server(self):
        try:
            response = requests.get("http://34.67.103.132:5000/api/materiales", timeout=10) # Ajusta la URL a tu servidor
            response.raise_for_status()  # Lanza excepción si la respuesta no es 200 OK
            materiales = response.json()
            self.materiales_df = pd.DataFrame(materiales)
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener materiales del servidor: {e}")
            self.materiales_df = pd.DataFrame(columns=['index', 'nombre_material', 'unidad'])

    def setup_material_input(self, form_layout):
        # Layout para el campo de materiales
        materiales_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        materiales_layout.bind(minimum_height=materiales_layout.setter("height"))

        # TextInput para buscar materiales
        self.material_input = TextInput(
            hint_text="Escriba el nombre del material",
            multiline=False,
            size_hint=(None, None),
            size=(400, 40),
            pos_hint={'center_x': 0.5},
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.material_input.bind(text=self.on_material_text)
        materiales_layout.add_widget(self.material_input)

        # Dropdown para sugerencias de materiales
        self.dropdown = CustomDropDown()
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.material_input, 'text', x))
        self.material_input.bind(focus=self.on_focus)

        # Layout para mostrar los materiales seleccionados
        self.selected_materials_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.selected_materials_layout.bind(minimum_height=self.selected_materials_layout.setter("height"))
        materiales_layout.add_widget(self.selected_materials_layout)

        form_layout.add_widget(materiales_layout)

    def on_focus(self, instance, value):
        if value:
            self.dropdown.open(instance)
        else:
            self.dropdown.dismiss()

    def on_material_text(self, instance, value):
        self.dropdown.clear_widgets()
        if value and hasattr(self, 'materiales_df'):
            filtered_materials = self.materiales_df[self.materiales_df['nombre_material'].str.contains(value, case=False)]
            for index, row in filtered_materials.iterrows():
                btn = Button(text=f"{row['nombre_material']} ({row['unidad']})", size_hint_y=None, height=40)
                btn.bind(on_release=lambda btn: self.select_material(btn.text))
                self.dropdown.add_widget(btn)

    def select_material(self, material_str):
        if material_str not in self.materiales_seleccionados:
            self.materiales_seleccionados.append(material_str)
            
            # Crear un layout para el material seleccionado con un botón para eliminar
            material_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            material_label = Label(text=material_str, size_hint_x=0.8)
            remove_button = Button(text='X', size_hint_x=0.2, background_color=(1, 0, 0, 1))
            remove_button.bind(on_release=lambda btn: self.remove_material(material_str, material_layout))

            material_layout.add_widget(material_label)
            material_layout.add_widget(remove_button)
            self.selected_materials_layout.add_widget(material_layout)

            self.material_input.text = ''  # Limpiar el input después de seleccionar

    def remove_material(self, material_str, material_layout):
        self.materiales_seleccionados.remove(material_str)
        self.selected_materials_layout.remove_widget(material_layout)

    def confirmar_envio(self, instance):
        # Validar datos
        datos_validos = self.validar_datos()
        if datos_validos:
            # Crear diccionario con los datos
            datos = {}
            for campo in self.campos:
                if campo["nombre"] == "materiales_usados":
                    datos[campo["nombre"]] = ", ".join(self.materiales_seleccionados)
                else:
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
                    "http://34.67.103.132:5000/recibir-datos",
                    json=datos,
                    timeout=20
                )
                if response.status_code == 200:
                    print("Datos enviados exitosamente")
                    # Limpiar los materiales seleccionados después del envío
                    self.materiales_seleccionados = []
                    self.selected_materials_layout.clear_widgets()
                else:
                    print("Error al enviar datos")
            except Exception as e:
                print(f"Error de conexión: {e}")

    def validar_datos(self):
        for campo in self.campos:
            if campo["nombre"] == "materiales_usados":
                if not self.materiales_seleccionados:
                    print("Debe seleccionar al menos un material.")
                    return False
            else:
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