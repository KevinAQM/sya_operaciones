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
API_URL = "http://34.67.103.132:5000"  # Reemplaza con la IP de tu servidor
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

class EquipoEntry:
    def __init__(self, nombre, cantidad, propiedad):
        self.nombre = nombre
        self.cantidad = cantidad
        self.propiedad = propiedad

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "propiedad": self.propiedad
        }

class VehiculoEntry:
    def __init__(self, nombre, placa, propiedad):
        self.nombre = nombre
        self.placa = placa
        self.propiedad = propiedad

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "placa": self.placa,
            "propiedad": self.propiedad
        }

class MaterialSelectionPopup(Popup):
    def __init__(self, add_callback, main_app, **kwargs):
        super(MaterialSelectionPopup, self).__init__(**kwargs)
        self.title = "Selección de Materiales"
        self.size_hint = (0.9, 0.8)
        self.add_callback = add_callback
        self.main_app = main_app

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

        # Actualizar la lista de materiales en la pantalla principal
        self.main_app.selected_materials_layout.clear_widgets()
        for mat in self.main_app.materiales_seleccionados:
            mat_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            mat_label = Label(text=f"{mat.nombre} - {mat.cantidad} {mat.unidad}", size_hint_x=0.8)
            remove_btn = create_button('X', size=(dp(40), dp(40)), color=RED, on_press=lambda btn: self.main_app.remove_material(mat, mat_layout))
            remove_btn.size_hint_x = 0.2
            mat_layout.add_widget(mat_label)
            mat_layout.add_widget(remove_btn)
            self.main_app.selected_materials_layout.add_widget(mat_layout)

class EquipoSelectionPopup(Popup):
    def __init__(self, add_callback, main_app, **kwargs):
        super(EquipoSelectionPopup, self).__init__(**kwargs)
        self.title = "Selección de Equipos"
        self.size_hint = (0.9, 0.8)
        self.add_callback = add_callback
        self.main_app = main_app

        # Layout principal
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Campo de búsqueda con ícono
        search_layout = BoxLayout(size_hint_y=None, height=dp(40))
        search_icon = Button(
            background_normal='search_icon.png',
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        self.search_input = TextInput(
            hint_text='Buscar equipo...',
            multiline=False,
            size_hint=(1, None),
            height=dp(40)
        )
        search_layout.add_widget(search_icon)
        search_layout.add_widget(self.search_input)

        # Lista de equipos con scroll (para la búsqueda)
        scroll = ScrollView()
        self.equipos_list = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.equipos_list.bind(minimum_height=self.equipos_list.setter('height'))
        scroll.add_widget(self.equipos_list)

        # Área para mostrar los equipos seleccionados
        self.selected_equipos_scroll = ScrollView()
        self.selected_equipos_grid = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.selected_equipos_grid.bind(
            minimum_height=self.selected_equipos_grid.setter('height')
        )
        self.selected_equipos_scroll.add_widget(self.selected_equipos_grid)

        # Sección de equipo seleccionado (para ingresar propiedad y cantidad)
        # Usar GridLayout de 2 columnas
        selection_layout = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120),
            padding=dp(10)
        )

        self.equipo_name = Label(text="Equipo: ")
        self.propiedad_input = TextInput(
            hint_text='Propiedad',
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

        # Agregar los widgets a selection_layout
        selection_layout.add_widget(Label(text="Propiedad:"))
        selection_layout.add_widget(self.propiedad_input)
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
            text='Agregar Equipo',
            size_hint_x=0.5,
            background_color=GREEN
        )
        finish_button = Button(
            text='Terminar',
            size_hint_x=0.5,
            background_color=BTN_COLOR
        )

        cancel_button.bind(on_release=self.dismiss)
        add_button.bind(on_release=self.add_equipo)
        finish_button.bind(on_release=self.dismiss)

        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(add_button)
        buttons_layout.add_widget(finish_button)

        # Agregar todos los elementos al layout principal
        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(self.selected_equipos_scroll)
        layout.add_widget(selection_layout)
        layout.add_widget(buttons_layout)

        self.content = layout
        self.search_input.bind(text=self.on_search_text)

        # Actualizar la lista de equipos seleccionados al iniciar el popup
        self.update_selected_equipos_display()

    def on_search_text(self, instance, value):
        self.equipos_list.clear_widgets()
        if not value:
            return

        # Filtrar equipos existentes
        filtered_equipos = [
            e for e in self.main_app.equipos_df['nombre_equipo'].tolist()
            if value.lower() in e.lower()
        ]

        # Agregar equipos filtrados
        for equipo in filtered_equipos:
            btn = Button(
                text=equipo,
                size_hint_y=None,
                height=dp(40),
                background_color=GRAY
            )
            btn.bind(on_release=lambda btn: self.select_equipo(btn.text))
            self.equipos_list.add_widget(btn)

        # Agregar opción de nuevo equipo si no hay coincidencia exacta
        if value and value not in filtered_equipos:
            new_btn = Button(
                text=f"Agregar nuevo equipo: {value}",
                size_hint_y=None,
                height=dp(40),
                background_color=GREEN
            )
            new_btn.bind(on_release=lambda btn: self.select_new_equipo(value))
            self.equipos_list.add_widget(new_btn)

    def select_equipo(self, equipo_name):
        self.equipo_name.text = f"Equipo: {equipo_name}"
        # Actualiza la propiedad si es un equipo existente
        if equipo_name in self.main_app.equipos_df['nombre_equipo'].tolist():
            propiedad = self.main_app.equipos_df[
                self.main_app.equipos_df['nombre_equipo'] == equipo_name
            ]['propiedad'].iloc[0]
            self.propiedad_input.text = propiedad
            self.propiedad_input.readonly = True
        else:
            self.propiedad_input.readonly = False
            self.propiedad_input.text = ""

        # Limpia la lista de equipos
        self.equipos_list.clear_widgets()
        # Actualiza el campo de búsqueda con el equipo seleccionado
        self.search_input.text = equipo_name

    def select_new_equipo(self, equipo_name):
        self.equipo_name.text = f"Equipo: {equipo_name}"
        self.propiedad_input.readonly = False
        self.propiedad_input.text = ""

        # Limpia la lista de equipos
        self.equipos_list.clear_widgets()
        # Actualiza el campo de búsqueda con el equipo seleccionado
        self.search_input.text = equipo_name

    def add_equipo(self, *args):
        equipo_name = self.equipo_name.text.replace("Equipo: ", "")
        propiedad = self.propiedad_input.text
        cantidad = self.quantity_input.text  # Corregido a quantity_input

        if not all([equipo_name, propiedad, cantidad]):
            return

        try:
            cantidad = float(cantidad)
            self.add_callback(equipo_name, cantidad, propiedad)
            # Limpia el campo de búsqueda después de agregar el equipo
            self.search_input.text = ''
            self.propiedad_input.text = ''
            self.quantity_input.text = ''  # Corregido a quantity_input
            self.equipo_name.text = 'Equipo: '
            # Actualiza la lista de equipos seleccionados
            self.update_selected_equipos_display()
        except ValueError:
            print("Por favor ingrese una cantidad válida")

    def update_selected_equipos_display(self):
        self.selected_equipos_grid.clear_widgets()  # Limpia la lista actual

        for equipo in self.main_app.equipos_seleccionados:
            equipo_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40)
            )
            equipo_label = Label(
                text=f"{equipo.nombre} - {equipo.cantidad} ({equipo.propiedad})",
                size_hint_x=0.8
            )
            remove_button = create_button(
                'X',
                size=(dp(40), dp(40)),
                color=RED,
                on_press=lambda btn, e=equipo, l=equipo_layout: self.remove_equipo_from_popup(e, l)
            )
            remove_button.size_hint_x = 0.2

            equipo_layout.add_widget(equipo_label)
            equipo_layout.add_widget(remove_button)
            self.selected_equipos_grid.add_widget(equipo_layout)

    def remove_equipo_from_popup(self, equipo_entry, equipo_layout):
        # Eliminar el equipo de la lista de equipos seleccionados en la app principal
        self.main_app.equipos_seleccionados.remove(equipo_entry)

        # Eliminar el layout del equipo del grid en el popup
        self.selected_equipos_grid.remove_widget(equipo_layout)

        # Actualizar la visualización de equipos seleccionados en el popup
        self.update_selected_equipos_display()

        # Actualizar la lista de equipos en la pantalla principal
        self.main_app.selected_equipos_layout.clear_widgets()
        for eq in self.main_app.equipos_seleccionados:
            eq_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            eq_label = Label(text=f"{eq.nombre} - {eq.cantidad} ({eq.propiedad})", size_hint_x=0.8)
            remove_btn = create_button('X', size=(dp(40), dp(40)), color=RED, on_press=lambda btn: self.main_app.remove_equipo(eq, eq_layout))
            remove_btn.size_hint_x = 0.2
            eq_layout.add_widget(eq_label)
            eq_layout.add_widget(remove_btn)
            self.main_app.selected_equipos_layout.add_widget(eq_layout)

class VehiculoSelectionPopup(Popup):
    def __init__(self, add_callback, main_app, **kwargs):
        super(VehiculoSelectionPopup, self).__init__(**kwargs)
        self.title = "Selección de Vehículos"
        self.size_hint = (0.9, 0.8)
        self.add_callback = add_callback
        self.main_app = main_app

        # Layout principal
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Campo de búsqueda con ícono
        search_layout = BoxLayout(size_hint_y=None, height=dp(40))
        search_icon = Button(
            background_normal='search_icon.png',
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        self.search_input = TextInput(
            hint_text='Buscar vehículo...',
            multiline=False,
            size_hint=(1, None),
            height=dp(40)
        )
        search_layout.add_widget(search_icon)
        search_layout.add_widget(self.search_input)

        # Lista de vehículos con scroll (para la búsqueda)
        scroll = ScrollView()
        self.vehiculos_list = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.vehiculos_list.bind(minimum_height=self.vehiculos_list.setter('height'))
        scroll.add_widget(self.vehiculos_list)

        # Área para mostrar los vehículos seleccionados
        self.selected_vehiculos_scroll = ScrollView()
        self.selected_vehiculos_grid = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.selected_vehiculos_grid.bind(
            minimum_height=self.selected_vehiculos_grid.setter('height')
        )
        self.selected_vehiculos_scroll.add_widget(self.selected_vehiculos_grid)

        # Sección de vehículo seleccionado (para ingresar placa y propiedad)
        selection_layout = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120),
            padding=dp(10)
        )

        # Campos para el vehículo seleccionado
        self.vehiculo_name = Label(text="Vehículo: ")
        self.placa_input = TextInput(
            hint_text='Placa',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        self.propiedad_input = TextInput(
            hint_text='Propiedad',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )

        selection_layout.add_widget(Label(text="Placa:"))
        selection_layout.add_widget(self.placa_input)
        selection_layout.add_widget(Label(text="Propiedad:"))
        selection_layout.add_widget(self.propiedad_input)

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
            text='Agregar Vehículo',
            size_hint_x=0.5,
            background_color=GREEN
        )
        finish_button = Button(
            text='Terminar',
            size_hint_x=0.5,
            background_color=BTN_COLOR
        )

        cancel_button.bind(on_release=self.dismiss)
        add_button.bind(on_release=self.add_vehiculo)
        finish_button.bind(on_release=self.dismiss)

        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(add_button)
        buttons_layout.add_widget(finish_button)

        # Agregar todos los elementos al layout principal
        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(self.selected_vehiculos_scroll)
        layout.add_widget(selection_layout)
        layout.add_widget(buttons_layout)

        self.content = layout
        self.search_input.bind(text=self.on_search_text)

        # Actualizar la lista de vehículos seleccionados al iniciar el popup
        self.update_selected_vehiculos_display()

    def on_search_text(self, instance, value):
        self.vehiculos_list.clear_widgets()
        if not value:
            return

        # Filtrar vehículos existentes
        filtered_vehiculos = [
            v for v in self.main_app.vehiculos_df['nombre_vehiculo'].tolist()
            if value.lower() in v.lower()
        ]

        # Agregar vehículos filtrados
        for vehiculo in filtered_vehiculos:
            btn = Button(
                text=vehiculo,
                size_hint_y=None,
                height=dp(40),
                background_color=GRAY
            )
            btn.bind(on_release=lambda btn: self.select_vehiculo(btn.text))
            self.vehiculos_list.add_widget(btn)

        # Agregar opción de nuevo vehículo si no hay coincidencia exacta
        if value and value not in filtered_vehiculos:
            new_btn = Button(
                text=f"Agregar nuevo vehículo: {value}",
                size_hint_y=None,
                height=dp(40),
                background_color=GREEN
            )
            new_btn.bind(on_release=lambda btn: self.select_new_vehiculo(value))
            self.vehiculos_list.add_widget(new_btn)

    def select_vehiculo(self, vehiculo_name):
        self.vehiculo_name.text = f"Vehículo: {vehiculo_name}"
        # Actualiza la placa y propiedad si es un vehículo existente
        if vehiculo_name in self.main_app.vehiculos_df['nombre_vehiculo'].tolist():
            placa = self.main_app.vehiculos_df[
                self.main_app.vehiculos_df['nombre_vehiculo'] == vehiculo_name
            ]['placa'].iloc[0]
            propiedad = self.main_app.vehiculos_df[
                self.main_app.vehiculos_df['nombre_vehiculo'] == vehiculo_name
            ]['propiedad'].iloc[0]
            self.placa_input.text = placa
            self.propiedad_input.text = propiedad
            self.placa_input.readonly = True
            self.propiedad_input.readonly = True
        else:
            self.placa_input.readonly = False
            self.propiedad_input.readonly = False
            self.placa_input.text = ""
            self.propiedad_input.text = ""

        # Limpia la lista de vehículos
        self.vehiculos_list.clear_widgets()
        # Actualiza el campo de búsqueda con el vehículo seleccionado
        self.search_input.text = vehiculo_name

    def select_new_vehiculo(self, vehiculo_name):
        self.vehiculo_name.text = f"Vehículo: {vehiculo_name}"
        self.placa_input.readonly = False
        self.propiedad_input.readonly = False
        self.placa_input.text = ""
        self.propiedad_input.text = ""

        # Limpia la lista de vehículos
        self.vehiculos_list.clear_widgets()
        # Actualiza el campo de búsqueda con el vehículo seleccionado
        self.search_input.text = vehiculo_name

    def add_vehiculo(self, *args):
        vehiculo_name = self.vehiculo_name.text.replace("Vehículo: ", "")
        placa = self.placa_input.text
        propiedad = self.propiedad_input.text

        if not all([vehiculo_name, placa, propiedad]):
            return

        self.add_callback(vehiculo_name, placa, propiedad)
        # Limpia el campo de búsqueda después de agregar el vehículo
        self.search_input.text = ''
        self.placa_input.text = ''
        self.propiedad_input.text = ''
        self.vehiculo_name.text = 'Vehículo: '
        # Actualiza la lista de vehículos seleccionados
        self.update_selected_vehiculos_display()

    def update_selected_vehiculos_display(self):
        self.selected_vehiculos_grid.clear_widgets()  # Limpia la lista actual

        for vehiculo in self.main_app.vehiculos_seleccionados:
            vehiculo_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40)
            )
            vehiculo_label = Label(
                text=f"{vehiculo.nombre} ({vehiculo.placa}) - {vehiculo.propiedad}",
                size_hint_x=0.8
            )
            remove_button = create_button(
                'X',
                size=(dp(40), dp(40)),
                color=RED,
                on_press=lambda btn, v=vehiculo, l=vehiculo_layout: self.remove_vehiculo_from_popup(v, l)
            )
            remove_button.size_hint_x = 0.2

            vehiculo_layout.add_widget(vehiculo_label)
            vehiculo_layout.add_widget(remove_button)
            self.selected_vehiculos_grid.add_widget(vehiculo_layout)

    def remove_vehiculo_from_popup(self, vehiculo_entry, vehiculo_layout):
        # Eliminar el vehículo de la lista de vehículos seleccionados en la app principal
        self.main_app.vehiculos_seleccionados.remove(vehiculo_entry)

        # Eliminar el layout del vehículo del grid en el popup
        self.selected_vehiculos_grid.remove_widget(vehiculo_layout)

        # Actualizar la visualización de vehículos seleccionados en el popup
        self.update_selected_vehiculos_display()

        # Actualizar la lista de vehículos en la pantalla principal
        self.main_app.selected_vehiculos_layout.clear_widgets()
        for v in self.main_app.vehiculos_seleccionados:
            v_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            v_label = Label(text=f"{v.nombre} ({v.placa}) - {v.propiedad}", size_hint_x=0.8)
            remove_btn = create_button('X', size=(dp(40), dp(40)), color=RED, on_press=lambda btn: self.main_app.remove_vehiculo(v, v_layout))
            remove_btn.size_hint_x = 0.2
            v_layout.add_widget(v_label)
            v_layout.add_widget(remove_btn)
            self.main_app.selected_vehiculos_layout.add_widget(v_layout)

class ReporteObraApp(App):
    title = "Parte Diario de Obra"

    def build(self):
        self.root_widget = BoxLayout(orientation='vertical', spacing=10, padding=20)
        scroll = ScrollView(size_hint=(1, 0.9))
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=10)
        form_layout.bind(minimum_height=form_layout.setter("height"))

        self.respuestas = {}
        self.materiales_seleccionados = []
        self.equipos_seleccionados = []
        self.vehiculos_seleccionados = []
        self.materiales_df = pd.DataFrame()
        self.equipos_df = pd.DataFrame()
        self.vehiculos_df = pd.DataFrame()

        # Definir campos del formulario
        self.campos = [
            {"nombre": "fecha", "tipo": "date", "etiqueta": "Fecha"},
            {"nombre": "codigo_obra", "tipo": "text", "etiqueta": "Código de Obra"},
            {"nombre": "nombre_ingeniero", "tipo": "text", "etiqueta": "Nombre del Ingeniero"},
            {"nombre": "nombre_supervisor", "tipo": "text", "etiqueta": "Nombre del Supervisor"},
            {"nombre": "actividad_principal", "tipo": "text", "etiqueta": "Actividad Principal (trabajo realizado)"},
            {"nombre": "materiales_usados", "tipo": "material", "etiqueta": "Materiales Usados"},
            {"nombre": "equipos_usados", "tipo": "equipo", "etiqueta": "Equipos Usados"},
            {"nombre": "vehiculos_usados", "tipo": "vehiculo", "etiqueta": "Vehículos Usados"},
            {"nombre": "supervisor_presente", "tipo": "bool", "etiqueta": "¿Supervisor Presente?"},
            {"nombre": "equipos_seguridad", "tipo": "bool", "etiqueta": "¿Equipos de Seguridad Completos?"},
            {"nombre": "incidentes", "tipo": "text", "etiqueta": "Incidentes ocurridos"},
            {"nombre": "siguiente_dia", "tipo": "text", "etiqueta": "Plan para Siguiente Día"},
            {"nombre": "observaciones", "tipo": "text", "etiqueta": "Observaciones"}
        ]

        # Crear campos del formulario
        for campo in self.campos:
            form_layout.add_widget(Widget(size_hint_y=None, height=5))

            if campo["nombre"] == "materiales_usados":
                form_layout.add_widget(create_label(campo["etiqueta"]))
                self.setup_material_input(form_layout)
                continue

            elif campo["nombre"] == "equipos_usados":
                form_layout.add_widget(create_label(campo["etiqueta"]))
                self.setup_equipo_input(form_layout)
                continue

            elif campo["nombre"] == "vehiculos_usados":
                form_layout.add_widget(create_label(campo["etiqueta"]))
                self.setup_vehiculo_input(form_layout)
                continue

            else:
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

        form_layout.add_widget(Widget(size_hint_y=None, height=10))

        form_layout.add_widget(create_button('Enviar Datos', on_press=self.confirmar_envio))

        scroll.add_widget(form_layout)
        self.root_widget.add_widget(scroll)
        self.get_materiales_from_server()
        self.get_equipos_from_server()
        self.get_vehiculos_from_server()

        self.material_popup = MaterialSelectionPopup(
            add_callback=self.add_material_with_quantity,
            main_app=self
        )
        self.equipo_popup = EquipoSelectionPopup(
            add_callback=self.add_equipo_with_quantity,
            main_app=self
        )
        self.vehiculo_popup = VehiculoSelectionPopup(
            add_callback=self.add_vehiculo_with_placa_propiedad,
            main_app=self
        )

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

    def get_equipos_from_server(self):
        try:
            response = requests.get(f"{API_URL}/api/equipos", timeout=10)
            response.raise_for_status()
            self.equipos_df = pd.DataFrame(response.json())
            print("Equipos cargados exitosamente.")
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor.")
            self.equipos_df = pd.DataFrame(columns=['index', 'nombre_equipo', 'propiedad'])
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al conectar al servidor.")
            self.equipos_df = pd.DataFrame(columns=['index', 'nombre_equipo', 'propiedad'])
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener equipos del servidor: {e}")
            self.equipos_df = pd.DataFrame(columns=['index', 'nombre_equipo', 'propiedad'])

    def get_vehiculos_from_server(self):
        try:
            response = requests.get(f"{API_URL}/api/vehiculos", timeout=10)
            response.raise_for_status()
            self.vehiculos_df = pd.DataFrame(response.json())
            print("Vehículos cargados exitosamente.")
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor.")
            self.vehiculos_df = pd.DataFrame(columns=['index', 'nombre_vehiculo', 'placa', 'propiedad'])
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al conectar al servidor.")
            self.vehiculos_df = pd.DataFrame(columns=['index', 'nombre_vehiculo', 'placa', 'propiedad'])
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener vehículos del servidor: {e}")
            self.vehiculos_df = pd.DataFrame(columns=['index', 'nombre_vehiculo', 'placa', 'propiedad'])

    def setup_material_input(self, form_layout):
        material_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        material_layout.bind(minimum_height=material_layout.setter("height"))

        open_popup_button = create_button(
            'Seleccionar Materiales',
            size=(400, 50),
            color=BTN_COLOR,
            on_press=self.show_material_popup
        )
        material_layout.add_widget(open_popup_button)

        self.selected_materials_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.selected_materials_layout.bind(
            minimum_height=self.selected_materials_layout.setter("height")
        )

        material_layout.add_widget(self.selected_materials_layout)
        form_layout.add_widget(material_layout)

    def setup_equipo_input(self, form_layout):
        equipo_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        equipo_layout.bind(minimum_height=equipo_layout.setter("height"))

        open_popup_button = create_button(
            'Seleccionar Equipos',
            size=(400, 50),
            color=BTN_COLOR,
            on_press=self.show_equipo_popup
        )
        equipo_layout.add_widget(open_popup_button)

        self.selected_equipos_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.selected_equipos_layout.bind(
            minimum_height=self.selected_equipos_layout.setter("height")
        )

        equipo_layout.add_widget(self.selected_equipos_layout)
        form_layout.add_widget(equipo_layout)

    def setup_vehiculo_input(self, form_layout):
        vehiculo_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        vehiculo_layout.bind(minimum_height=vehiculo_layout.setter("height"))

        open_popup_button = create_button(
            'Seleccionar Vehículos',
            size=(400, 50),
            color=BTN_COLOR,
            on_press=self.show_vehiculo_popup
        )
        vehiculo_layout.add_widget(open_popup_button)

        self.selected_vehiculos_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.selected_vehiculos_layout.bind(
            minimum_height=self.selected_vehiculos_layout.setter("height")
        )

        vehiculo_layout.add_widget(self.selected_vehiculos_layout)
        form_layout.add_widget(vehiculo_layout)

    def show_material_popup(self, instance):
        self.material_popup.open()

    def show_equipo_popup(self, instance):
        self.equipo_popup.open()

    def show_vehiculo_popup(self, instance):
        self.vehiculo_popup.open()

    def add_material_with_quantity(self, material_name, unit, quantity):
        try:
            quantity_float = float(quantity)
        except ValueError:
            print("Cantidad inválida. Por favor, ingrese un número.")
            return

        material_entry = MaterialEntry(material_name, unit, quantity_float)
        self.materiales_seleccionados.append(material_entry)

        material_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        material_label = Label(
            text=f"{material_name} - {quantity_float} {unit}",
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
        self.material_popup.update_selected_materials_display()

    def add_equipo_with_quantity(self, equipo_name, cantidad, propiedad):
        equipo_entry = EquipoEntry(equipo_name, cantidad, propiedad)
        self.equipos_seleccionados.append(equipo_entry)

        equipo_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        equipo_label = Label(
            text=f"{equipo_name} - {cantidad} ({propiedad})",
            size_hint_x=0.8
        )
        remove_button = create_button(
            'X',
            size=(dp(40), dp(40)),
            color=RED,
            on_press=lambda btn: self.remove_equipo(equipo_entry, equipo_layout)
        )
        remove_button.size_hint_x = 0.2

        equipo_layout.add_widget(equipo_label)
        equipo_layout.add_widget(remove_button)
        self.selected_equipos_layout.add_widget(equipo_layout)
        self.equipo_popup.update_selected_equipos_display()

    def add_vehiculo_with_placa_propiedad(self, vehiculo_name, placa, propiedad):
        vehiculo_entry = VehiculoEntry(vehiculo_name, placa, propiedad)
        self.vehiculos_seleccionados.append(vehiculo_entry)

        vehiculo_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        vehiculo_label = Label(
            text=f"{vehiculo_name} ({placa}) - {propiedad}",
            size_hint_x=0.8
        )
        remove_button = create_button(
            'X',
            size=(dp(40), dp(40)),
            color=RED,
            on_press=lambda btn: self.remove_vehiculo(vehiculo_entry, vehiculo_layout)
        )
        remove_button.size_hint_x = 0.2

        vehiculo_layout.add_widget(vehiculo_label)
        vehiculo_layout.add_widget(remove_button)
        self.selected_vehiculos_layout.add_widget(vehiculo_layout)
        self.vehiculo_popup.update_selected_vehiculos_display()

    def remove_material(self, material_entry, material_layout):
        self.materiales_seleccionados.remove(material_entry)
        self.selected_materials_layout.remove_widget(material_layout)
        self.material_popup.update_selected_materials_display()

    def remove_equipo(self, equipo_entry, equipo_layout):
        self.equipos_seleccionados.remove(equipo_entry)
        self.selected_equipos_layout.remove_widget(equipo_layout)
        self.equipo_popup.update_selected_equipos_display()

    def remove_vehiculo(self, vehiculo_entry, vehiculo_layout):
        self.vehiculos_seleccionados.remove(vehiculo_entry)
        self.selected_vehiculos_layout.remove_widget(vehiculo_layout)
        self.vehiculo_popup.update_selected_vehiculos_display()

    def confirmar_envio(self, instance):
        if not self.validar_datos():
            return

        datos = {
            campo["nombre"]: (
                [material.to_dict() for material in self.materiales_seleccionados]
                if campo["nombre"] == "materiales_usados"
                else [equipo.to_dict() for equipo in self.equipos_seleccionados]
                if campo["nombre"] == "equipos_usados"
                else [vehiculo.to_dict() for vehiculo in self.vehiculos_seleccionados]
                if campo["nombre"] == "vehiculos_usados"
                else (self.respuestas[campo["nombre"]].text == "Sí"
                      if campo["tipo"] == "bool"
                      else (float(self.respuestas[campo["nombre"]].text)
                            if campo["tipo"] == "float"
                            else self.respuestas[campo["nombre"]].text))
            )
            for campo in self.campos
        }

        try:
            response = requests.post(f"{API_URL}/recibir-datos", json=datos, timeout=20)
            if response.status_code == 200:
                print("Datos enviados exitosamente")
                self.materiales_seleccionados = []
                self.equipos_seleccionados = []
                self.vehiculos_seleccionados = []
                self.selected_materials_layout.clear_widgets()
                self.selected_equipos_layout.clear_widgets()
                self.selected_vehiculos_layout.clear_widgets()
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
            elif campo["nombre"] == "equipos_usados":
                if not self.equipos_seleccionados:
                    print("Debe seleccionar al menos un equipo.")
                    return False
            elif campo["nombre"] == "vehiculos_usados":
                if not self.vehiculos_seleccionados:
                    print("Debe seleccionar al menos un vehículo.")
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