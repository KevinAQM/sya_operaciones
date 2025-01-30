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
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from datetime import datetime
import requests
import pandas as pd

# --- Constantes ---
API_URL = "http://34.67.103.132:5000"
BG_COLOR = (0.1, 0.1, 0.1, 1)
BTN_COLOR = (0, 0.5, 1, 1)
WHITE = (1, 1, 1, 1)
GRAY = (0.75, 0.75, 0.75, 1)
BLACK = (0, 0, 0, 1)
GREEN = (0, 0.7, 0, 1)
RED = (1, 0, 0, 1)

Window.clearcolor = BG_COLOR

# --- Widgets Config ---
def create_label(text):
    return Label(
        text=text,
        size_hint=(None, None),
        size=(400, 20),
        pos_hint={'center_x': 0.5},
        color=WHITE,
        font_size=18
    )

def create_text_input(multiline=False, text=""):
    return TextInput(
        text=text,
        multiline=multiline,
        size_hint=(None, None),
        size=(400, 40),
        pos_hint={'center_x': 0.5},
        background_color=WHITE,
        foreground_color=BLACK
    )

def create_button(text, size=(200, 40), color=BTN_COLOR, on_press=None):
    return Button(
        text=text,
        size_hint=(None, None),
        size=size,
        pos_hint={'center_x': 0.5},
        background_color=color,
        color=WHITE,
        on_press=on_press
    )

# --- Clases ---
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

class MaterialSelectionPopup(Popup):
    def __init__(self, add_callback, main_app, **kwargs):
        super(MaterialSelectionPopup, self).__init__(**kwargs)
        self.title = "Selección de Materiales"
        self.size_hint = (0.9, 0.8)
        self.add_callback = add_callback
        self.main_app = main_app  # Guarda la referencia

        # Layout principal
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Campo de búsqueda con ícono
        search_layout = BoxLayout(size_hint_y=None, height=dp(40))
        search_icon = Button(
            background_normal='search_icon.png',  # Asegúrate de tener este ícono
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        self.search_input = TextInput(
            hint_text='Buscar material...',
            multiline=False,
            size_hint=(1, None),
            height=dp(40)
        )
        search_layout.add_widget(search_icon)
        search_layout.add_widget(self.search_input)

        # Lista de materiales con scroll (para la búsqueda)
        scroll = ScrollView()
        self.materials_list = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.materials_list.bind(minimum_height=self.materials_list.setter('height'))
        scroll.add_widget(self.materials_list)

        # Área para mostrar los materiales seleccionados
        self.selected_materials_scroll = ScrollView()
        self.selected_materials_grid = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.selected_materials_grid.bind(
            minimum_height=self.selected_materials_grid.setter('height')
        )
        self.selected_materials_scroll.add_widget(self.selected_materials_grid)

        # Sección de material seleccionado (para ingresar unidad y cantidad)
        selection_layout = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120),
            padding=dp(10)
        )

        # Campos para el material seleccionado
        self.material_name = Label(text="Material: ")
        self.unit_input = TextInput(
            hint_text='Unidad',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        self.quantity_input = TextInput(
            hint_text='Cantidad',
            multiline=False,
            input_filter='float',
            size_hint_y=None,
            height=dp(40)
        )

        selection_layout.add_widget(Label(text="Unidad:"))
        selection_layout.add_widget(self.unit_input)
        selection_layout.add_widget(Label(text="Cantidad:"))
        selection_layout.add_widget(self.quantity_input)

        # Botones de acción
        buttons_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        cancel_button = Button(
            text='Cancelar',
            size_hint_x=0.5,
            background_color=RED
        )
        add_button = Button(
            text='Agregar Material',
            size_hint_x=0.5,
            background_color=GREEN
        )
        finish_button = Button(
            text='Terminar',
            size_hint_x=0.5,
            background_color=BTN_COLOR
        )

        cancel_button.bind(on_release=self.dismiss)
        add_button.bind(on_release=self.add_material)
        finish_button.bind(on_release=self.dismiss)

        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(add_button)
        buttons_layout.add_widget(finish_button)

        # Agregar todos los elementos al layout principal
        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(self.selected_materials_scroll)
        layout.add_widget(selection_layout)
        layout.add_widget(buttons_layout)

        self.content = layout
        self.search_input.bind(text=self.on_search_text)

        # Actualizar la lista de materiales seleccionados al iniciar el popup
        self.update_selected_materials_display()

    def on_search_text(self, instance, value):
        self.materials_list.clear_widgets()
        if not value:
            return

        # Filtrar materiales existentes
        filtered_materials = [
            m for m in self.main_app.materiales_df['nombre_material'].tolist()
            if value.lower() in m.lower()
        ]

        # Agregar materiales filtrados
        for material in filtered_materials:
            btn = Button(
                text=material,
                size_hint_y=None,
                height=dp(40),
                background_color=GRAY
            )
            btn.bind(on_release=lambda btn: self.select_material(btn.text))
            self.materials_list.add_widget(btn)

        # Agregar opción de nuevo material si no hay coincidencia exacta
        if value and value not in filtered_materials:
            new_btn = Button(
                text=f"Agregar nuevo material: {value}",
                size_hint_y=None,
                height=dp(40),
                background_color=GREEN
            )
            new_btn.bind(on_release=lambda btn: self.select_new_material(value))
            self.materials_list.add_widget(new_btn)

    def select_material(self, material_name):
        self.material_name.text = f"Material: {material_name}"
        # Actualiza la unidad si es un material existente
        if material_name in self.main_app.materiales_df['nombre_material'].tolist():
            unit = self.main_app.materiales_df[
                self.main_app.materiales_df['nombre_material'] == material_name
            ]['unidad'].iloc[0]
            self.unit_input.text = unit
            self.unit_input.readonly = True
        else:
            self.unit_input.readonly = False
            self.unit_input.text = ""

        # Limpia la lista de materiales
        self.materials_list.clear_widgets()
        # Actualiza el campo de búsqueda con el material seleccionado
        self.search_input.text = material_name

    def select_new_material(self, material_name):
        self.material_name.text = f"Material: {material_name}"
        self.unit_input.readonly = False
        self.unit_input.text = ""

        # Limpia la lista de materiales
        self.materials_list.clear_widgets()
        # Actualiza el campo de búsqueda con el material seleccionado
        self.search_input.text = material_name

    def add_material(self, *args):
        material_name = self.material_name.text.replace("Material: ", "")
        unit = self.unit_input.text
        quantity = self.quantity_input.text

        if not all([material_name, unit, quantity]):
            return

        try:
            quantity = float(quantity)
            self.add_callback(material_name, unit, quantity)
            # Limpia el campo de búsqueda después de agregar el material
            self.search_input.text = ''
            self.unit_input.text = ''
            self.quantity_input.text = ''
            self.material_name.text = 'Material: '
            # Actualiza la lista de materiales seleccionados
            self.update_selected_materials_display()
        except ValueError:
            print("Por favor ingrese una cantidad válida")

    def update_selected_materials_display(self):
        self.selected_materials_grid.clear_widgets()  # Limpia la lista actual

        for material in self.main_app.materiales_seleccionados:
            material_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40)
            )
            material_label = Label(
                text=f"{material.nombre} - {material.cantidad} {material.unidad}",
                size_hint_x=0.8
            )
            remove_button = create_button(
                'X',
                size=(dp(40), dp(40)),
                color=RED,
                on_press=lambda btn, m=material, l=material_layout: self.remove_material_from_popup(m, l)
            )
            remove_button.size_hint_x = 0.2
            
            material_layout.add_widget(material_label)
            material_layout.add_widget(remove_button)
            self.selected_materials_grid.add_widget(material_layout)

    def remove_material_from_popup(self, material_entry, material_layout):
        # Eliminar el material de la lista de materiales seleccionados en la app principal
        self.main_app.materiales_seleccionados.remove(material_entry)

        # Eliminar el layout del material del grid en el popup
        self.selected_materials_grid.remove_widget(material_layout)

        # Actualizar la visualización de materiales seleccionados en el popup
        self.update_selected_materials_display()

class ReporteObraApp(App):
    title = "Parte Diario de Obra"

    def build(self):
        self.root_widget = BoxLayout(orientation='vertical', spacing=10, padding=20)
        scroll = ScrollView(size_hint=(1, 0.9))
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=10)
        form_layout.bind(minimum_height=form_layout.setter("height"))

        self.respuestas = {}
        self.materiales_seleccionados = []
        self.materiales_df = pd.DataFrame() # Initialize to avoid errors

        # Definir campos del formulario
        self.campos = [
            {"nombre": "fecha", "tipo": "date", "etiqueta": "Fecha"},
            {"nombre": "codigo_obra", "tipo": "text", "etiqueta": "Código de Obra"},
            {"nombre": "nombre_ingeniero", "tipo": "text", "etiqueta": "Nombre del Ingeniero"},
            {"nombre": "nombre_supervisor", "tipo": "text", "etiqueta": "Nombre del Supervisor"},
            {"nombre": "actividad_principal", "tipo": "text", "etiqueta": "Actividad Principal (trabajo realizado)"},
            {"nombre": "materiales_usados", "tipo": "material", "etiqueta": "Materiales Usados"},
            {"nombre": "supervisor_presente", "tipo": "bool", "etiqueta": "¿Supervisor Presente?"},
            {"nombre": "equipos_seguridad", "tipo": "bool", "etiqueta": "¿Equipos de Seguridad Completos?"},
            {"nombre": "incidentes", "tipo": "text", "etiqueta": "Incidentes ocurridos"},
            {"nombre": "siguiente_dia", "tipo": "text", "etiqueta": "Plan para Siguiente Día"},
            {"nombre": "observaciones", "tipo": "text", "etiqueta": "Observaciones"}
        ]

        # Crear campos del formulario
        for campo in self.campos:
            form_layout.add_widget(Widget(size_hint_y=None, height=5)) # Espaciador

            if campo["nombre"] == "materiales_usados":
                # Agregar Label para materiales usados ANTES del setup_material_input
                form_layout.add_widget(create_label(campo["etiqueta"]))
                self.setup_material_input(form_layout)
                continue # Sigue al proximo campo

            else:
                # Agregar Label para todos los campos excepto materiales_usados
                form_layout.add_widget(create_label(campo["etiqueta"]))

                if campo["tipo"] == "bool":
                    input_widget = Spinner(
                        text='Sí',
                        values=('Sí', 'No'),
                        size_hint=(None, None),
                        size=(400, 40),
                        pos_hint={'center_x': 0.5},
                        background_color=GRAY,
                        color=WHITE
                    )
                else:
                    input_widget = create_text_input()
                    if campo["nombre"] == "fecha":
                        input_widget.text = datetime.now().strftime('%d/%m/%Y')

                self.respuestas[campo["nombre"]] = input_widget
                form_layout.add_widget(input_widget)

        form_layout.add_widget(Widget(size_hint_y=None, height=10)) # Espaciador

        form_layout.add_widget(create_button('Enviar Datos', on_press=self.confirmar_envio))

        scroll.add_widget(form_layout)
        self.root_widget.add_widget(scroll)
        self.get_materiales_from_server()

        return self.root_widget

    def get_materiales_from_server(self):
        try:
            response = requests.get(f"{API_URL}/api/materiales", timeout=10)
            response.raise_for_status()
            self.materiales_df = pd.DataFrame(response.json())
            print("Materiales cargados exitosamente.")
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor.")
            self.materiales_df = pd.DataFrame(columns=['index', 'nombre_material', 'unidad'])
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al conectar al servidor.")
            self.materiales_df = pd.DataFrame(columns=['index', 'nombre_material', 'unidad'])
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener materiales del servidor: {e}")
            self.materiales_df = pd.DataFrame(columns=['index', 'nombre_material', 'unidad'])

    def setup_material_input(self, form_layout):
        # Layout principal para el campo de materiales
        material_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        material_layout.bind(minimum_height=material_layout.setter("height"))

        # Botón para abrir el popup
        open_popup_button = create_button(
            'Seleccionar Materiales',
            size=(400, 50),
            color=BTN_COLOR,
            on_press=self.show_material_popup
        )
        material_layout.add_widget(open_popup_button)

        # Layout para materiales seleccionados
        self.selected_materials_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.selected_materials_layout.bind(
            minimum_height=self.selected_materials_layout.setter("height")
        )

        material_layout.add_widget(self.selected_materials_layout)

        # Agrega el layout de materiales al layout principal del formulario
        form_layout.add_widget(material_layout)

    def show_material_popup(self, instance):
        popup = MaterialSelectionPopup(
            add_callback=self.add_material_with_quantity,
            main_app=self  # Pasa la referencia de ReporteObraApp
        )
        # Se actualiza la lista de materiales del popup al ser creado
        popup.update_selected_materials_display()
        popup.open()
    
    def on_focus(self, instance, value):
        if value:
            self.dropdown.open(instance)
        else:
            self.dropdown.dismiss()
            
    
    def on_material_text(self, instance, value):
        self.dropdown.clear_widgets()
        if value and not self.materiales_df.empty:
            filtered_materials = self.materiales_df[
                self.materiales_df['nombre_material'].str.contains(value, case=False)
            ]
            
            # Add existing materials to dropdown
            for _, row in filtered_materials.iterrows():
                btn = Button(text=f"{row['nombre_material']}", size_hint_y=None, height=40)
                btn.bind(
                    on_release=lambda btn, row=row: self.show_quantity_input(
                        row['nombre_material'],
                        row['unidad'],
                        is_new_material=False
                    )
                )
                self.dropdown.add_widget(btn)
            
            # Add "Agregar Nuevo Material" button if no exact match is found
            exact_match = self.materiales_df['nombre_material'].str.lower() == value.lower()
            if not exact_match.any() and value.strip():
                new_material_btn = Button(
                    text="Agregar Nuevo Material",
                    size_hint_y=None,
                    height=40,
                    background_color=GREEN
                )
                new_material_btn.bind(
                    on_release=lambda btn: self.show_new_material_input(value)
                )
                self.dropdown.add_widget(new_material_btn)     
    
    
    def show_new_material_input(self, material_name):
        self.dropdown.dismiss() # Cerrar dropdown
        self.material_input.text = material_name # Autocompletar texto

        # Clear existing layout
        self.quantity_layout.clear_widgets()

        # Create unit input
        unit_input = create_text_input()
        unit_input.hint_text = "Unidad de medida"
        unit_input.size_hint_x = 0.4

        # Create quantity input
        quantity_input = create_text_input()
        quantity_input.hint_text = "Cantidad"
        quantity_input.size_hint_x = 0.4

        # Create add button
        add_button = create_button(
            "Agregar",
            size=(0, 40),
            color=GREEN,
            on_press=lambda x: self.add_new_material(
                material_name,
                unit_input.text,
                quantity_input.text
            )
        )
        add_button.size_hint_x = 0.2

        # Add all widgets to layout
        self.quantity_layout.add_widget(unit_input)
        self.quantity_layout.add_widget(quantity_input)
        self.quantity_layout.add_widget(add_button)

    def add_new_material(self, material_name, unit, quantity_text):
        if not unit.strip():
            print("Por favor ingrese una unidad de medida")
            return
        
        try:
            quantity = float(quantity_text)
            material_entry = MaterialEntry(material_name, unit, quantity)
            self.materiales_seleccionados.append(material_entry)

            # Add to UI
            material_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            material_label = Label(text=f"{material_name} - {quantity} {unit}", size_hint_x=0.8)
            remove_button = create_button(
                'X',
                size=(0, 40),
                color=RED,
                on_press=lambda btn: self.remove_material(material_entry, material_layout)
            )
            remove_button.size_hint_x = 0.2

            material_layout.add_widget(material_label)
            material_layout.add_widget(remove_button)
            self.selected_materials_layout.add_widget(material_layout)

            # Clear inputs
            self.quantity_layout.clear_widgets()
            self.material_input.text = ""

        except ValueError:
            print("Por favor ingrese una cantidad válida")

    def show_quantity_input(self, material_name, unit, is_new_material=False):
        self.dropdown.dismiss() # Cerrar dropdown
        self.material_input.text = material_name # Autocompletar texto

        self.quantity_layout.clear_widgets()

        quantity_input = create_text_input()
        quantity_input.hint_text = f"Cantidad ({unit})"
        quantity_input.size_hint_x = 0.7

        add_button = create_button(
            "Agregar",
            size=(0, 40),
            color=GREEN,
            on_press=lambda x: self.add_material_with_quantity(material_name, unit, quantity_input.text)
        )
        add_button.size_hint_x = 0.3

        self.quantity_layout.add_widget(quantity_input)
        self.quantity_layout.add_widget(add_button)


    def add_material_with_quantity(self, material_name, unit, quantity):
        material_entry = MaterialEntry(material_name, unit, quantity)
        self.materiales_seleccionados.append(material_entry)

        # Actualizar UI
        material_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        
        material_label = Label(
            text=f"{material_name} - {quantity} {unit}",
            size_hint_x=0.8
        )
        remove_button = create_button(
            'X',
            size=(dp(40), dp(40)),
            color=RED,
            on_press=lambda btn: self.remove_material(material_entry, material_layout)
        )
        remove_button.size_hint_x = 0.2

        material_layout.add_widget(material_label)
        material_layout.add_widget(remove_button)
        self.selected_materials_layout.add_widget(material_layout)

    def remove_material(self, material_entry, material_layout):
        self.materiales_seleccionados.remove(material_entry)
        self.selected_materials_layout.remove_widget(material_layout)

    def confirmar_envio(self, instance):
        if not self.validar_datos():
            return
        
        datos = {
            campo["nombre"]: ([material.to_dict() for material in self.materiales_seleccionados]
                            if campo["nombre"] == "materiales_usados"
                            else (self.respuestas[campo["nombre"]].text == "Sí"
                                    if campo["tipo"] == "bool"
                                    else (float(self.respuestas[campo["nombre"]].text)
                                        if campo["tipo"] == "float"
                                        else self.respuestas[campo["nombre"]].text)))
            for campo in self.campos
        }       
                
        try:
            response = requests.post(f"{API_URL}/recibir-datos", json=datos, timeout=20)
            if response.status_code == 200:
                print("Datos enviados exitosamente")
                self.materiales_seleccionados = []
                self.selected_materials_layout.clear_widgets()
            else:
                print(f"Error al enviar datos: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor para enviar los datos.")
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al enviar los datos al servidor.")
        except Exception as e:
            print(f"Error al enviar los datos: {e}")

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
                    print(f"El campo '{campo['etiqueta']}' es obligatorio.")
                    return False
                if campo["tipo"] == "float":
                    try:
                        float(valor)
                    except ValueError:
                        print(f"El campo '{campo['etiqueta']}' debe ser un número.")
                        return False
        return True

if __name__ == '__main__':
    ReporteObraApp().run()