from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from datetime import datetime
import requests
import json
import pandas as pd

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class CustomDropDown(DropDown):
    def __init__(self, **kwargs):
        super(CustomDropDown, self).__init__(**kwargs)
        self.auto_width = False
        self.width = 400

class MaterialEntry:
    def __init__(self, nombre, unidad, cantidad):
        self.nombre = nombre
        self.unidad = unidad
        self.cantidad = cantidad

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "unidad": self.unidad,
            "cantidad": self.cantidad
        }

class ReporteObraApp(App):
    title = "Parte Diario de Obra"

    def build(self):
        # Main container setup remains the same
        self.root_widget = BoxLayout(orientation='vertical', spacing=10, padding=20)
        scroll = ScrollView(size_hint=(1, 0.9))
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=10)
        form_layout.bind(minimum_height=form_layout.setter("height"))
        
        self.respuestas = {}
        self.materiales_seleccionados = []  # Will store MaterialEntry objects
        
        # Define form fields
        self.campos = [
            {"nombre": "codigo_obra", "tipo": "text", "etiqueta": "Código de Obra"},
            {"nombre": "actividad_principal", "tipo": "text", "etiqueta": "Actividad Principal"},
            {"nombre": "nombre_ingeniero", "tipo": "text", "etiqueta": "Nombre del Ingeniero"},
            {"nombre": "nombre_supervisor", "tipo": "text", "etiqueta": "Nombre del Supervisor"},
            {"nombre": "fecha", "tipo": "date", "etiqueta": "Fecha"},
            {"nombre": "materiales_usados", "tipo": "material", "etiqueta": "Materiales Usados"},
            {"nombre": "horas_trabajo", "tipo": "float", "etiqueta": "Horas de Trabajo"},
            {"nombre": "incidentes", "tipo": "bool", "etiqueta": "¿Hubo Incidentes?"},
            {"nombre": "equipos_seguridad", "tipo": "bool", "etiqueta": "¿Equipos de Seguridad Completos?"},
            {"nombre": "supervisor_presente", "tipo": "bool", "etiqueta": "¿Supervisor Presente?"},
            {"nombre": "material_restante", "tipo": "float", "etiqueta": "¿Material Restante?"},
            {"nombre": "siguiente_dia", "tipo": "text", "etiqueta": "Plan para Siguiente Día"},
            {"nombre": "observaciones", "tipo": "text", "etiqueta": "Observaciones"}
        ]
        
        # Create form fields
        for campo in self.campos:
            form_layout.add_widget(Widget(size_hint_y=None, height=5))
            
            label = Label(
                text=campo["etiqueta"],
                size_hint=(None, None),
                size=(400, 20),
                pos_hint={'center_x': 0.5},
                color=(1, 1, 1, 1),
                font_size=18
            )
            form_layout.add_widget(label)
            
            if campo["tipo"] == "bool":
                input_widget = Spinner(
                    text='Sí',
                    values=('Sí', 'No'),
                    size_hint=(None, None),
                    size=(400, 40),
                    pos_hint={'center_x': 0.5},
                    background_color=(0.75, 0.75, 0.75, 1),
                    color=(1, 1, 1, 1)
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
                    background_color=(1, 1, 1, 1),
                    foreground_color=(0, 0, 0, 1)
                )
                if campo["nombre"] == "fecha":
                    input_widget.text = datetime.now().strftime('%d/%m/%Y')
                self.respuestas[campo["nombre"]] = input_widget
                form_layout.add_widget(input_widget)

        form_layout.add_widget(Widget(size_hint_y=None, height=10))

        btn_enviar = Button(
            text='Enviar Datos',
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={'center_x': 0.5},
            background_color=(0, 0.5, 1, 1),
            color=(1, 1, 1, 1),
            on_press=self.confirmar_envio
        )
        form_layout.add_widget(btn_enviar)

        scroll.add_widget(form_layout)
        self.root_widget.add_widget(scroll)
        self.get_materiales_from_server()

        return self.root_widget

    def get_materiales_from_server(self):
        try:
            response = requests.get("http://34.67.103.132:5000/api/materiales", timeout=10)
            response.raise_for_status()
            materiales = response.json()
            self.materiales_df = pd.DataFrame(materiales)
            print("Materiales cargados exitosamente.")
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener materiales del servidor: {e}")
            self.materiales_df = pd.DataFrame(columns=['index', 'nombre_material', 'unidad'])

    def setup_material_input(self, form_layout):
        materiales_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        materiales_layout.bind(minimum_height=materiales_layout.setter("height"))

        # Search input for materials
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

        # Dropdown for material suggestions
        self.dropdown = CustomDropDown()
        self.material_input.bind(focus=self.on_focus)

        # Layout for quantity input (will be shown after material selection)
        self.quantity_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(400, 40),
            pos_hint={'center_x': 0.5}
        )

        # Layout for selected materials
        self.selected_materials_layout = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None
        )
        self.selected_materials_layout.bind(
            minimum_height=self.selected_materials_layout.setter("height")
        )
        
        materiales_layout.add_widget(self.quantity_layout)
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
            filtered_materials = self.materiales_df[
                self.materiales_df['nombre_material'].str.contains(value, case=False)
            ]
            for _, row in filtered_materials.iterrows():
                btn = Button(
                    text=f"{row['nombre_material']}",
                    size_hint_y=None,
                    height=40
                )
                btn.bind(
                    on_release=lambda btn, row=row: self.show_quantity_input(
                        row['nombre_material'],
                        row['unidad']
                    )
                )
                self.dropdown.add_widget(btn)

    def show_quantity_input(self, material_name, unit):
        self.dropdown.dismiss()
        self.material_input.text = material_name
        
        # Clear previous quantity input if exists
        self.quantity_layout.clear_widgets()
        
        # Create quantity input
        quantity_input = TextInput(
            hint_text=f"Cantidad ({unit})",
            multiline=False,
            size_hint_x=0.7,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        
        # Add button
        add_button = Button(
            text="Agregar",
            size_hint_x=0.3,
            background_color=(0, 0.7, 0, 1)
        )
        
        # Bind add button to add material with quantity
        add_button.bind(
            on_release=lambda x: self.add_material_with_quantity(
                material_name,
                unit,
                quantity_input.text
            )
        )
        
        self.quantity_layout.add_widget(quantity_input)
        self.quantity_layout.add_widget(add_button)

    def add_material_with_quantity(self, material_name, unit, quantity_text):
        try:
            quantity = float(quantity_text)
            material_entry = MaterialEntry(material_name, unit, quantity)
            self.materiales_seleccionados.append(material_entry)
            
            # Create layout for the selected material entry
            material_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=40
            )
            
            # Label showing material info
            material_label = Label(
                text=f"{material_name} - {quantity} {unit}",
                size_hint_x=0.8
            )
            
            # Remove button
            remove_button = Button(
                text='X',
                size_hint_x=0.2,
                background_color=(1, 0, 0, 1)
            )
            remove_button.bind(
                on_release=lambda btn: self.remove_material(material_entry, material_layout)
            )

            material_layout.add_widget(material_label)
            material_layout.add_widget(remove_button)
            self.selected_materials_layout.add_widget(material_layout)
            
            # Clear quantity input and material input after successful addition
            self.quantity_layout.clear_widgets()
            self.material_input.text = ""
            
        except ValueError:
            print("Por favor ingrese una cantidad válida")

    def remove_material(self, material_entry, material_layout):
        self.materiales_seleccionados.remove(material_entry)
        self.selected_materials_layout.remove_widget(material_layout)

    def confirmar_envio(self, instance):
        if self.validar_datos():
            datos = {}
            for campo in self.campos:
                if campo["nombre"] == "materiales_usados":
                    # Convert material entries to list of dictionaries
                    datos[campo["nombre"]] = [
                        material.to_dict() for material in self.materiales_seleccionados
                    ]
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

            datos["timestamp"] = datetime.now().isoformat()

            try:
                response = requests.post(
                    "http://34.67.103.132:5000/recibir-datos",
                    json=datos,
                    timeout=20
                )
                if response.status_code == 200:
                    print("Datos enviados exitosamente")
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