# Archivo: sya_operaciones_android.py
import requests
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
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
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle

API_URL = "http://34.67.103.132:5000"  # "http://127.0.0.1:5000" #
BG_COLOR = (0.1, 0.1, 0.1, 1)
BTN_COLOR = (0, 0.5, 1, 1)
WHITE = (1, 1, 1, 1)
GRAY = (0.75, 0.75, 1, 1)  # Modified to ensure visibility
BLACK = (0, 0, 0, 1)
GREEN = (0, 0.7, 0, 1)
RED = (1, 0, 0, 1)
ITEM_BG_COLOR = (0.2, 0.2, 0.2, 1)

screen_width = Window.width
screen_height = Window.height
scale_factor = min(screen_width / 1920, screen_height / 1080)

label_font_size = int(80 * scale_factor)
title_font_size = int(90 * scale_factor)
input_height = int(80 * scale_factor)
button_height = int(80 * scale_factor)
margin = int(20 * scale_factor)
padding = int(15 * scale_factor)
text_input_font_size = int(120 * scale_factor)

Window.clearcolor = BG_COLOR


def create_label(text, titulo=False):
    return Label(
        text=text,
        size_hint=(1, None),
        height=dp(input_height),
        pos_hint={'center_x': 0.5},
        color=WHITE,
        font_size=title_font_size if titulo else label_font_size
    )


def create_text_input(multiline=False, text="", **kwargs):  # Modified to accept **kwargs
    return TextInput(
        text=text,
        multiline=multiline,
        size_hint=(1, None),
        height=dp(input_height),
        pos_hint={'center_x': 0.5},
        background_color=WHITE,
        foreground_color=BLACK,
        font_size=text_input_font_size,
        padding=(dp(padding), dp(input_height * 0.5 - text_input_font_size * 0.25)),
        **kwargs  # Pass kwargs to TextInput constructor
    )


def create_button(text, size=(200, 40), color=BTN_COLOR, on_press=None):
    return Button(
        text=text,
        size_hint=(None, None),
        size=(dp(size[0]), dp(button_height)),
        pos_hint={'center_x': 0.5},
        background_color=color,
        color=WHITE,
        on_press=on_press,
        font_size=label_font_size
    )


class MainScreen(AnchorLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.padding = dp(margin * 2)
        self.spacing = dp(margin * 2)
        self.anchor_x = 'center'  # Add horizontal centering
        self.anchor_y = 'center'  # Add vertical centering

        vertical_layout = BoxLayout(orientation='vertical', spacing=dp(margin * 2), padding=dp(margin),
                                    size_hint_y=None)  # BoxLayout for vertical arrangement, size_hint_y=None

        titulo_label = create_label('SELECCIONAR UNA OPCIÓN:', titulo=True)  # Agregado el titulo
        titulo_label.color = WHITE  # Cambiar color a gris para que no resalte tanto
        vertical_layout.add_widget(titulo_label)  # Add titulo_label to vertical_layout

        # No size_hint or size specified for buttons, BoxLayout will manage their size
        reporte_button = create_button('REPORTE DIARIO DE OBRA', size=(600, button_height * 2),
                                       on_press=self.show_reporte_diario_screen)
        requerimiento_button = create_button('REQUERIMIENTO DE MATERIALES', size=(600, button_height * 2),
                                            on_press=self.show_requerimiento_materiales_screen)

        vertical_layout.add_widget(reporte_button)
        vertical_layout.add_widget(requerimiento_button)

        self.add_widget(vertical_layout)  # Add vertical_layout to AnchorLayout

    def show_reporte_diario_screen(self, instance):
        self.main_app.show_reporte_diario_screen()

    def show_requerimiento_materiales_screen(self, instance):
        self.main_app.show_requerimiento_materiales_screen()


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
        return {"nombre": self.nombre, "unidad": self.unidad, "cantidad": self.cantidad}


class EquipoEntry:  # Class for Reporte Diario Obra
    def __init__(self, nombre, cantidad, propiedad):
        self.nombre = nombre
        self.cantidad = cantidad
        self.propiedad = propiedad

    def to_dict(self):
        return {"nombre": self.nombre, "cantidad": self.cantidad, "propiedad": self.propiedad}


class RequerimientoEquipoEntry:  # New class for Requerimiento Materiales
    def __init__(self, nombre, unidad, cantidad):
        self.nombre = nombre
        self.unidad = unidad  # In Requerimiento, 'propiedad' field from CSV is used as 'unidad' in UI
        self.cantidad = cantidad

    def to_dict(self):
        return {"nombre": self.nombre, "unidad": self.unidad,
                "cantidad": self.cantidad}  # Use "unidad" as key in dict


class VehiculoEntry:
    def __init__(self, nombre, placa, propiedad):
        self.nombre = nombre
        self.placa = placa
        self.propiedad = propiedad

    def to_dict(self):
        return {"nombre": self.nombre, "placa": self.placa, "propiedad": self.propiedad}


class PersonalEntry:
    def __init__(self, nombre_completo, categoria, horas_extras):
        self.nombre_completo = nombre_completo
        self.categoria = categoria
        self.horas_extras = horas_extras

    def to_dict(self):
        return {"nombre_completo": self.nombre_completo, "categoria": self.categoria, "horas_extras": self.horas_extras}


class MaterialSelectionPopup(Popup):
    def __init__(self, add_callback, main_app, **kwargs):
        self.add_callback = add_callback
        self.main_app = main_app
        kwargs.pop('add_callback', None)
        kwargs.pop('main_app', None)
        super(MaterialSelectionPopup, self).__init__(**kwargs)
        self.title = "Selección de Materiales"
        self.size_hint = (0.9, 0.9)
        self.is_new_material = False
        # ... (rest of MaterialSelectionPopup class - no changes needed) ...
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        search_layout = BoxLayout(size_hint_y=None, height=dp(40))
        self.search_input = TextInput(
            hint_text='Buscar material...',
            multiline=False,
            size_hint=(1, None),
            height=dp(40)
        )
        search_layout.add_widget(self.search_input)

        scroll = ScrollView(size_hint_y=0.3)  # 30% del espacio
        self.materials_list = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.materials_list.bind(minimum_height=self.materials_list.setter('height'))
        scroll.add_widget(self.materials_list)

        self.selected_materials_scroll = ScrollView(size_hint_y=0.4)  # 40% del espacio
        self.selected_materials_grid = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.selected_materials_grid.bind(minimum_height=self.selected_materials_grid.setter('height'))
        self.selected_materials_scroll.add_widget(self.selected_materials_grid)

        selection_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.3, height=dp(120),
                                      padding=dp(10))  # 30% del espacio

        self.material_name = Label(text="Material: ")
        self.unit_input = TextInput(hint_text='Unidad', multiline=False, size_hint_y=None, height=dp(40))
        self.quantity_input = TextInput(hint_text='Cantidad', multiline=False, input_filter='float', size_hint_y=None,
                                        height=dp(40))

        selection_layout.add_widget(Label(text="Unidad:"))
        selection_layout.add_widget(self.unit_input)
        selection_layout.add_widget(Label(text="Cantidad:"))
        selection_layout.add_widget(self.quantity_input)

        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_button = Button(text='Cancelar', size_hint_x=0.5, background_color=RED)
        add_button = Button(text='Agregar', size_hint_x=0.5, background_color=GREEN)
        finish_button = Button(text='Terminar', size_hint_x=0.5, background_color=BTN_COLOR)

        cancel_button.bind(on_release=self.dismiss)
        add_button.bind(on_release=self.add_material)
        finish_button.bind(on_release=self.on_finish)

        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(add_button)
        buttons_layout.add_widget(finish_button)

        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(selection_layout)
        layout.add_widget(self.selected_materials_scroll)
        layout.add_widget(buttons_layout)

        self.content = layout
        self.search_input.bind(text=self.on_search_text)
        self.update_selected_materials_display()

    def on_finish(self, instance):
        self.dismiss()
        if self.main_app.materiales_seleccionados:
            self.main_app.materiales_button.background_color = BTN_COLOR

    def on_search_text(self, instance, value):
        self.materials_list.clear_widgets()
        if not value:
            return

        filtered_materials = [m['nombre_material'] for m in self.main_app.materiales_data if
                              value.lower() in m['nombre_material'].lower()]

        for material in filtered_materials:
            btn = Button(text=material, size_hint_y=None, height=dp(40), background_color=GRAY)
            btn.bind(on_release=lambda btn: self.select_material(btn.text))
            self.materials_list.add_widget(btn)

        unique_material_names = [m['nombre_material'] for m in self.main_app.materiales_data]
        if value and value not in filtered_materials and value not in unique_material_names:
            new_btn = Button(text=f"Agregar nuevo material: {value}", size_hint_y=None, height=dp(40),
                             background_color=GREEN)
            new_btn.bind(on_release=lambda btn: self.select_new_material(value))
            self.materials_list.add_widget(new_btn)

    def select_material(self, material_name):
        self.material_name.text = f"Material: {material_name}"
        self.unit_input.readonly = False
        self.unit_input.text = ""
        self.is_new_material = False  # Reset flag when selecting existing material
        for material in self.main_app.materiales_data:
            if material['nombre_material'] == material_name:
                unit = material['unidad']
                self.unit_input.text = unit
                break
        self.materials_list.clear_widgets()
        self.search_input.text = material_name

    def select_new_material(self, material_name):
        self.material_name.text = f"Material: {material_name}"
        self.unit_input.readonly = False
        self.unit_input.text = ""
        self.is_new_material = True  # Set flag when adding new material
        self.materials_list.clear_widgets()
        self.search_input.text = material_name

    def add_material(self, *args):
        material_name = self.material_name.text.replace("Material: ", "")
        unit = self.unit_input.text
        quantity = self.quantity_input.text

        if not all([material_name, unit, quantity]):
            return

        try:
            quantity = float(quantity)
            self.add_callback(material_name, unit, quantity, self.is_new_material)  # Pass is_new_material flag
            self.search_input.text = ''
            self.unit_input.text = ''
            self.quantity_input.text = ''
            self.material_name.text = 'Material: '
            self.is_new_material = False  # Reset flag after adding
            self.update_selected_materials_display()
        except ValueError:
            print("Por favor ingrese una cantidad válida")

    def update_selected_materials_display(self):
        self.selected_materials_grid.clear_widgets()
        grid = self.selected_materials_grid
        grid.spacing = dp(5)
        grid.padding = dp(5)

        for material in self.main_app.materiales_seleccionados:
            card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(80),
                spacing=dp(5),
                padding=dp(5),
            )
            with card.canvas.before:
                Color(*ITEM_BG_COLOR)
                Rectangle(pos=card.pos, size=card.size)

            text_layout = BoxLayout(
                orientation='vertical',
                size_hint_x=0.8,
                padding=[0, 0, 0, 0]
            )

            nombre_label = Label(
                text=f"[b]{material.nombre}[/b]",
                markup=True,
                font_size=label_font_size,
                halign='left',
                valign='middle',
                color=WHITE,
                size_hint_y=0.5,
                text_size=(None, None),
                padding=[0, 0]
            )

            detalles_label = Label(
                text=f"[size={int(label_font_size)}]{material.cantidad} {material.unidad}[/size]",
                markup=True,
                halign='left',
                valign='middle',
                color=WHITE,
                size_hint_y=0.5,
                text_size=(Window.width * 0.6, None),
                padding=[0, 0]
            )

            text_layout.add_widget(nombre_label)
            text_layout.add_widget(detalles_label)

            delete_btn = Button(
                text='×',
                font_size=label_font_size,
                bold=True,
                size_hint_x=None,
                width=dp(40),
                background_color=RED,
                background_normal='',
                on_press=lambda btn, m=material, card_widget=card: self.remove_material_from_popup(m, card_widget)
            )

            card.add_widget(text_layout)
            card.add_widget(delete_btn)
            self.selected_materials_grid.add_widget(card)

    def remove_material_from_popup(self, material_entry, material_layout):
        self.main_app.materiales_seleccionados.remove(material_entry)
        self.selected_materials_grid.remove_widget(material_layout)
        self.update_selected_materials_display()


class EquipoSelectionPopup(Popup):  # Popup for Reporte Diario Obra - No changes needed
    def __init__(self, add_callback, main_app, **kwargs):
        self.add_callback = add_callback
        self.main_app = main_app
        kwargs.pop('add_callback', None)
        kwargs.pop('main_app', None)
        super(EquipoSelectionPopup, self).__init__(**kwargs)
        self.title = "Selección de Equipos"
        self.size_hint = (0.9, 0.9)
        self.is_new_equipo = False

        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        search_layout = BoxLayout(size_hint_y=None, height=dp(40))
        self.search_input = TextInput(
            hint_text='Buscar equipo...',
            multiline=False,
            size_hint=(1, None),
            height=dp(40)
        )
        search_layout.add_widget(self.search_input)

        scroll = ScrollView(size_hint_y=0.3)
        self.equipos_list = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.equipos_list.bind(minimum_height=self.equipos_list.setter('height'))
        scroll.add_widget(self.equipos_list)

        self.selected_equipos_scroll = ScrollView(size_hint_y=0.4)
        self.selected_equipos_grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.selected_equipos_grid.bind(minimum_height=self.selected_equipos_grid.setter('height'))
        self.selected_equipos_scroll.add_widget(
            self.selected_equipos_grid)  # Corrected line: adding grid, not scroll

        selection_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.3, height=dp(120), padding=dp(10))

        self.equipo_name = Label(text="Equipo: ")
        self.propiedad_input = TextInput(hint_text='Propiedad', multiline=False, size_hint_y=None, height=dp(40))
        self.quantity_input = TextInput(hint_text='Cantidad', multiline=False, input_filter='float', size_hint_y=None,
                                        height=dp(40))

        selection_layout.add_widget(Label(text="Propiedad:"))
        selection_layout.add_widget(self.propiedad_input)
        selection_layout.add_widget(Label(text="Cantidad:"))
        selection_layout.add_widget(self.quantity_input)

        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_button = Button(text='Cancelar', size_hint_x=0.5, background_color=RED)
        add_button = Button(text='Agregar', size_hint_x=0.5, background_color=GREEN)
        finish_button = Button(text='Terminar', size_hint_x=0.5, background_color=BTN_COLOR)

        cancel_button.bind(on_release=self.dismiss)
        add_button.bind(on_release=self.add_equipo)
        finish_button.bind(on_release=self.on_finish)

        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(add_button)
        buttons_layout.add_widget(finish_button)

        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(selection_layout)
        layout.add_widget(self.selected_equipos_scroll)
        layout.add_widget(buttons_layout)

        self.content = layout
        self.search_input.bind(text=self.on_search_text)
        self.update_selected_equipos_display()

    def on_finish(self, instance):
        self.dismiss()
        if self.main_app.equipos_seleccionados:
            self.main_app.equipos_button.background_color = BTN_COLOR

    def on_search_text(self, instance, value):  # For Reporte Diario Obra - No changes needed
        self.equipos_list.clear_widgets()
        if not value:
            return

        filtered_equipos = [e['nombre_equipo'] for e in self.main_app.equipos_data if
                            value.lower() in e['nombre_equipo'].lower()]

        for equipo in filtered_equipos:
            btn = Button(text=equipo, size_hint_y=None, height=dp(40), background_color=GRAY)
            btn.bind(on_release=lambda btn: self.select_equipo(btn.text))
            self.equipos_list.add_widget(btn)

        unique_equipo_names = [e['nombre_equipo'] for e in self.main_app.equipos_data]
        if value and value not in filtered_equipos and value not in unique_equipo_names:
            new_btn = Button(text=f"Agregar nuevo equipo: {value}", size_hint_y=None, height=dp(40),
                             background_color=GREEN)
            new_btn.bind(on_release=lambda btn: self.select_new_equipo(value))
            self.equipos_list.add_widget(new_btn)

    def select_equipo(self, equipo_name):  # For Reporte Diario Obra - no changes needed
        self.equipo_name.text = f"Equipo: {equipo_name}"
        self.propiedad_input.readonly = False
        self.propiedad_input.text = ""
        self.is_new_equipo = False
        for equipo in self.main_app.equipos_data:
            if equipo['nombre_equipo'] == equipo_name:
                propiedad = equipo['propiedad']
                self.propiedad_input.text = propiedad
                break
        self.equipos_list.clear_widgets()
        self.search_input.text = equipo_name

    def select_new_equipo(self, equipo_name):  # For Reporte Diario Obra - no changes needed
        self.equipo_name.text = f"Equipo: {equipo_name}"
        self.propiedad_input.readonly = False
        self.propiedad_input.text = ""
        self.is_new_equipo = True
        self.equipos_list.clear_widgets()
        self.search_input.text = equipo_name

    def add_equipo(self, *args):  # For Reporte Diario Obra - no changes needed
        equipo_name = self.equipo_name.text.replace("Equipo: ", "")
        propiedad = self.propiedad_input.text
        cantidad = self.quantity_input.text

        if not all([equipo_name, propiedad, cantidad]):
            return

        try:
            cantidad = float(cantidad)
            self.add_callback(equipo_name, cantidad, propiedad, self.is_new_equipo)
            self.search_input.text = ''
            self.propiedad_input.text = ''
            self.quantity_input.text = ''
            self.equipo_name.text = 'Equipo: '
            self.is_new_equipo = False
            self.update_selected_equipos_display()
        except ValueError:
            print("Por favor ingrese una cantidad válida")

    def update_selected_equipos_display(self):  # For Reporte Diario Obra - no changes needed
        self.selected_equipos_grid.clear_widgets()
        grid = self.selected_equipos_grid
        grid.spacing = dp(5)
        grid.padding = dp(5)

        for equipo in self.main_app.equipos_seleccionados:
            card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(80),
                spacing=dp(5),
                padding=dp(5),
            )
            with card.canvas.before:
                Color(*ITEM_BG_COLOR)
                Rectangle(pos=card.pos, size=card.size)

            text_layout = BoxLayout(
                orientation='vertical',
                size_hint_x=0.8,
                padding=[0, 0, 0, 0]
            )

            nombre_label = Label(
                text=f"[b]{equipo.nombre}[/b]",
                markup=True,
                font_size=label_font_size,
                halign='left',
                valign='middle',
                color=WHITE,
                size_hint_y=0.5,
                text_size=(None, None),
                padding=[0, 0]
            )

            detalles_label = Label(
                text=f"[size={int(label_font_size)}]{equipo.cantidad} und • {equipo.propiedad}[/size]",
                markup=True,
                halign='left',
                valign='middle',
                color=WHITE,
                size_hint_y=0.5,
                text_size=(Window.width * 0.6, None),
                padding=[0, 0]
            )

            text_layout.add_widget(nombre_label)
            text_layout.add_widget(detalles_label)

            delete_btn = Button(
                text='×',
                font_size=label_font_size,
                bold=True,
                size_hint_x=None,
                width=dp(40),
                background_color=RED,
                background_normal='',
                on_press=lambda btn, e=equipo, card_widget=card: self.remove_equipo_from_popup(e, card_widget)
            )

            card.add_widget(text_layout)
            card.add_widget(delete_btn)
            self.selected_equipos_grid.add_widget(card)

    def remove_equipo_from_popup(self, equipo_entry, equipo_layout):  # For Reporte Diario Obra - no changes needed
        self.main_app.equipos_seleccionados.remove(equipo_entry)
        self.selected_equipos_grid.remove_widget(equipo_layout)
        self.update_selected_equipos_display()


class VehiculoSelectionPopup(Popup):
    def __init__(self, add_callback, main_app, **kwargs):
        self.add_callback = add_callback
        self.main_app = main_app
        kwargs.pop('add_callback', None)
        kwargs.pop('main_app', None)
        super(VehiculoSelectionPopup, self).__init__(**kwargs)
        self.title = "Selección de Vehículos"
        self.size_hint = (0.9, 0.9)
        self.is_new_vehiculo = False

        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        search_layout = BoxLayout(size_hint_y=None, height=dp(40))
        self.search_input = TextInput(
            hint_text='Buscar vehículo...',
            multiline=False,
            size_hint=(1, None),
            height=dp(40)
        )
        search_layout.add_widget(self.search_input)

        scroll = ScrollView(size_hint_y=0.3)  # 30% del espacio
        self.vehiculos_list = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.vehiculos_list.bind(minimum_height=self.vehiculos_list.setter('height'))
        scroll.add_widget(self.vehiculos_list)

        self.selected_vehiculos_scroll = ScrollView(size_hint_y=0.4)  # 40% del espacio
        self.selected_vehiculos_grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.selected_vehiculos_grid.bind(minimum_height=self.selected_vehiculos_grid.setter('height'))
        self.selected_vehiculos_scroll.add_widget(self.selected_vehiculos_grid)

        selection_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.3, height=dp(120),
                                      padding=dp(10))  # 30% del espacio

        self.vehiculo_name = Label(text="Vehículo: ")
        self.propiedad_input = TextInput(hint_text='Propiedad', multiline=False, size_hint_y=None, height=dp(40))
        self.placa_input = TextInput(hint_text='Placa', multiline=False, size_hint_y=None, height=dp(40))

        selection_layout.add_widget(Label(text="Propiedad:"))
        selection_layout.add_widget(self.propiedad_input)
        selection_layout.add_widget(Label(text="Placa:"))
        selection_layout.add_widget(self.placa_input)

        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_button = Button(text='Cancelar', size_hint_x=0.5, background_color=RED)
        add_button = Button(text='Agregar', size_hint_x=0.5, background_color=GREEN)
        finish_button = Button(text='Terminar', size_hint_x=0.5, background_color=BTN_COLOR)

        cancel_button.bind(on_release=self.dismiss)
        add_button.bind(on_release=self.add_vehiculo)
        finish_button.bind(on_release=self.on_finish)

        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(add_button)
        buttons_layout.add_widget(finish_button)

        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(selection_layout)
        layout.add_widget(self.selected_vehiculos_scroll)
        layout.add_widget(buttons_layout)

        self.content = layout
        self.search_input.bind(text=self.on_search_text)
        self.update_selected_vehiculos_display()

    def on_finish(self, instance):
        self.dismiss()
        if self.main_app.vehiculos_seleccionados:
            self.main_app.vehiculos_button.background_color = BTN_COLOR

    def on_search_text(self, instance, value):
        self.vehiculos_list.clear_widgets()
        if not value:
            return

        filtered_vehiculos = [v['nombre_vehiculo'] for v in self.main_app.vehiculos_data if
                              value.lower() in v['nombre_vehiculo'].lower()]

        for vehiculo in filtered_vehiculos:
            btn = Button(text=vehiculo, size_hint_y=None, height=dp(40), background_color=GRAY)
            btn.bind(on_release=lambda btn: self.select_vehiculo(btn.text))
            self.vehiculos_list.add_widget(btn)

        unique_vehiculo_names = [v['nombre_vehiculo'] for v in self.main_app.vehiculos_data]
        if value and value not in filtered_vehiculos and value not in unique_vehiculo_names:
            new_btn = Button(text=f"Agregar nuevo vehículo: {value}", size_hint_y=None, height=dp(40), background_color=GREEN)
            new_btn.bind(on_release=lambda btn: self.select_new_vehiculo(value))
            self.vehiculos_list.add_widget(new_btn)

    def select_vehiculo(self, vehiculo_name):
        self.vehiculo_name.text = f"Vehículo: {vehiculo_name}"
        self.placa_input.readonly = False
        self.propiedad_input.readonly = False
        self.placa_input.text = ""
        self.propiedad_input.text = ""
        self.is_new_vehiculo = False
        for vehiculo in self.main_app.vehiculos_data:
            if vehiculo['nombre_vehiculo'] == vehiculo_name:
                placa = vehiculo['placa']
                propiedad = vehiculo['propiedad']
                self.placa_input.text = placa
                self.propiedad_input.text = propiedad
                break
        self.vehiculos_list.clear_widgets()
        self.search_input.text = vehiculo_name

    def select_new_vehiculo(self, vehiculo_name):
        self.vehiculo_name.text = f"Vehículo: {vehiculo_name}"
        self.placa_input.readonly = False
        self.propiedad_input.readonly = False
        self.placa_input.text = ""
        self.propiedad_input.text = ""
        self.is_new_vehiculo = True
        self.vehiculos_list.clear_widgets()
        self.search_input.text = vehiculo_name

    def add_vehiculo(self, *args):
        vehiculo_name = self.vehiculo_name.text.replace("Vehículo: ", "")
        placa = self.placa_input.text
        propiedad = self.propiedad_input.text

        if not all([vehiculo_name, placa, propiedad]):
            return

        self.add_callback(vehiculo_name, placa, propiedad, self.is_new_vehiculo)
        self.search_input.text = ''
        self.placa_input.text = ''
        self.propiedad_input.text = ''
        self.vehiculo_name.text = 'Vehículo: '
        self.is_new_vehiculo = False
        self.update_selected_vehiculos_display()

    def update_selected_vehiculos_display(self):
        self.selected_vehiculos_grid.clear_widgets()
        grid = self.selected_vehiculos_grid
        grid.spacing = dp(5)
        grid.padding = dp(5)

        for vehiculo in self.main_app.vehiculos_seleccionados:
            card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(80),
                spacing=dp(5),
                padding=dp(5),
            )
            with card.canvas.before:
                Color(*ITEM_BG_COLOR)
                Rectangle(pos=card.pos, size=card.size)

            text_layout = BoxLayout(
                orientation='vertical',
                size_hint_x=0.8,
                padding=[0,0,0,0]
            )

            nombre_label = Label(
                text=f"[b]{vehiculo.nombre}[/b]",
                markup=True,
                font_size=label_font_size,
                halign='left',
                valign='middle',
                color=WHITE,
                size_hint_y=0.5,
                text_size=(None, None),
                padding=[0,0]
            )

            detalles_label = Label(
                text=f"[size={int(label_font_size)}]{vehiculo.placa} • {vehiculo.propiedad}[/size]",
                markup=True,
                halign='left',
                valign='middle',
                color=WHITE,
                size_hint_y=0.5,
                text_size=(Window.width * 0.6, None),
                padding=[0,0]
            )

            text_layout.add_widget(nombre_label)
            text_layout.add_widget(detalles_label)

            delete_btn = Button(
                text='×',
                font_size=label_font_size,
                bold=True,
                size_hint_x=None,
                width=dp(40),
                background_color=RED,
                background_normal='',
                on_press=lambda btn, v=vehiculo, card_widget=card: self.remove_vehiculo_from_popup(v, card_widget)
            )

            card.add_widget(text_layout)
            card.add_widget(delete_btn)
            self.selected_vehiculos_grid.add_widget(card)

    def remove_vehiculo_from_popup(self, vehiculo_entry, vehiculo_layout):
        self.main_app.vehiculos_seleccionados.remove(vehiculo_entry)
        self.selected_vehiculos_grid.remove_widget(vehiculo_layout)
        self.update_selected_vehiculos_display()


class PersonalSelectionPopup(Popup):
    def __init__(self, add_callback, main_app, **kwargs):
        self.add_callback = add_callback
        self.main_app = main_app
        kwargs.pop('add_callback', None)
        kwargs.pop('main_app', None)
        super(PersonalSelectionPopup, self).__init__(**kwargs)
        self.title = "Selección de Personal de Campo"
        self.size_hint = (0.9, 0.9)
        self.is_new_personal = False

        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        search_layout = BoxLayout(size_hint_y=None, height=dp(40))
        self.search_input = TextInput(
            hint_text='Buscar personal...',
            multiline=False,
            size_hint=(1, None),
            height=dp(40)
        )
        search_layout.add_widget(self.search_input)

        scroll = ScrollView(size_hint_y=0.3)  # 30% del espacio
        self.personal_list = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.personal_list.bind(minimum_height=self.personal_list.setter('height'))
        scroll.add_widget(self.personal_list)

        self.selected_personal_scroll = ScrollView(size_hint_y=0.4)  # 40% del espacio
        self.selected_personal_grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.selected_personal_grid.bind(minimum_height=self.selected_personal_grid.setter('height'))
        self.selected_personal_scroll.add_widget(self.selected_personal_grid)

        selection_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.3, height=dp(120), padding=dp(10))  # 30% del espacio

        self.personal_name = Label(text="Personal: ")
        self.categoria_input = TextInput(hint_text='Categoría', multiline=False, size_hint_y=None, height=dp(40))
        self.horas_extras_input = TextInput(hint_text='Horas Extras', multiline=False, input_filter='float', size_hint_y=None, height=dp(40))

        selection_layout.add_widget(Label(text="Categoría:"))
        selection_layout.add_widget(self.categoria_input)
        selection_layout.add_widget(Label(text="Horas Extras:"))
        selection_layout.add_widget(self.horas_extras_input)

        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_button = Button(text='Cancelar', size_hint_x=0.5, background_color=RED)
        add_button = Button(text='Agregar', size_hint_x=0.5, background_color=GREEN)
        finish_button = Button(text='Terminar', size_hint_x=0.5, background_color=BTN_COLOR)

        cancel_button.bind(on_release=self.dismiss)
        add_button.bind(on_release=self.add_personal)
        finish_button.bind(on_release=self.on_finish)

        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(add_button)
        buttons_layout.add_widget(finish_button)

        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(selection_layout)
        layout.add_widget(self.selected_personal_scroll)
        layout.add_widget(buttons_layout)

        self.content = layout
        self.search_input.bind(text=self.on_search_text)
        self.update_selected_personal_display()

    def on_finish(self, instance):
        self.dismiss()
        if self.main_app.personal_seleccionados:
            self.main_app.personal_button.background_color = BTN_COLOR

    def on_search_text(self, instance, value):
        self.personal_list.clear_widgets()
        if not value:
            return

        filtered_personal = [p['NOMBRE_COMPLETO'] for p in self.main_app.personal_data if value.lower() in p['NOMBRE_COMPLETO'].lower()]

        for personal in filtered_personal:
            btn = Button(text=personal, size_hint_y=None, height=dp(40), background_color=GRAY)
            btn.bind(on_release=lambda btn: self.select_personal(btn.text))
            self.personal_list.add_widget(btn)

        unique_personal_names = [p['NOMBRE_COMPLETO'] for p in self.main_app.personal_data]
        if value and value not in filtered_personal and value not in unique_personal_names:
            new_btn = Button(text=f"Agregar nuevo personal: {value}", size_hint_y=None, height=dp(40), background_color=GREEN)
            new_btn.bind(on_release=lambda btn: self.select_new_personal(value))
            self.personal_list.add_widget(new_btn)

    def select_personal(self, personal_name):
        self.personal_name.text = f"Personal: {personal_name}"
        self.categoria_input.readonly = False
        self.categoria_input.text = ""
        self.selected_categoria = None
        self.is_new_personal = False
        for personal in self.main_app.personal_data:
            if personal['NOMBRE_COMPLETO'] == personal_name:
                categoria_personal = personal['CATEGORIA']
                self.categoria_input.text = categoria_personal
                self.selected_categoria = categoria_personal
                break
        self.personal_list.clear_widgets()
        self.search_input.text = personal_name

    def select_new_personal(self, personal_name):
        self.personal_name.text = f"Personal: {personal_name}"
        self.categoria_input.readonly = False
        self.categoria_input.text = ""
        self.selected_categoria = None
        self.is_new_personal = True
        self.personal_list.clear_widgets()
        self.search_input.text = personal_name

    def add_personal(self, *args):
        personal_name = self.personal_name.text.replace("Personal: ", "")
        horas_extras = self.horas_extras_input.text
        categoria_ingresada = self.categoria_input.text

        if not horas_extras:
            horas_extras = "0.0"

        if not all([personal_name, horas_extras]):
            return

        try:
            horas_extras = float(horas_extras)
            categoria = categoria_ingresada if categoria_ingresada else "N/A"
            self.add_callback(personal_name, categoria, horas_extras, self.is_new_personal)
            self.search_input.text = ''
            self.horas_extras_input.text = ''
            self.categoria_input.text = ''
            self.personal_name.text = 'Personal: '
            self.selected_categoria = None
            self.is_new_personal = False
            self.update_selected_personal_display()
        except ValueError:
            print("Por favor ingrese horas extras válidas")

    def update_selected_personal_display(self):
        self.selected_personal_grid.clear_widgets()
        grid = self.selected_personal_grid
        grid.spacing = dp(5)
        grid.padding = dp(5)

        for personal in self.main_app.personal_seleccionados:
            card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(80),
                spacing=dp(5),
                padding=dp(5),
            )
            with card.canvas.before:
                Color(*ITEM_BG_COLOR)
                Rectangle(pos=card.pos, size=card.size)

            text_layout = BoxLayout(
                orientation='vertical',
                size_hint_x=0.8,
                padding=[0,0,0,0]
            )

            nombre_label = Label(
                text=f"[b]{personal.nombre_completo}[/b]",
                markup=True,
                font_size=label_font_size,
                halign='left',
                valign='middle',
                color=WHITE,
                size_hint_y=0.5,
                text_size=(None, None),
                padding=[0,0]
            )

            detalles_label = Label(
                text=f"[size={int(label_font_size)}]{personal.categoria} • HE: {personal.horas_extras}[/size]",
                markup=True,
                halign='left',
                valign='middle',
                color=WHITE,
                size_hint_y=0.5,
                text_size=(Window.width * 0.6, None),
                padding=[0,0]
            )

            text_layout.add_widget(nombre_label)
            text_layout.add_widget(detalles_label)

            delete_btn = Button(
                text='×',
                font_size=label_font_size,
                bold=True,
                size_hint_x=None,
                width=dp(40),
                background_color=RED,
                background_normal='',
                on_press=lambda btn, p=personal, card_widget=card: self.remove_personal_from_popup(p, card_widget)
            )

            card.add_widget(text_layout)
            card.add_widget(delete_btn)
            self.selected_personal_grid.add_widget(card)

    def remove_personal_from_popup(self, personal_entry, personal_layout):
        self.main_app.personal_seleccionados.remove(personal_entry)
        self.selected_personal_grid.remove_widget(personal_layout)
        self.update_selected_personal_display()


class ReporteObraApp(App):
    title = "SYA Operaciones"

    def build(self):
        self.main_screen_layout = MainScreen(self)
        Window.flip()
        return self.main_screen_layout

    def on_start(self):
        self.materiales_data = []
        self.equipos_data = []
        self.vehiculos_data = []
        self.personal_data = []
        self.new_materials_to_add = []
        self.new_equipos_to_add = []
        self.new_vehiculos_to_add = []
        self.new_personal_to_add = []
        self.get_materiales_from_server()
        self.get_equipos_from_server()
        self.get_vehiculos_from_server()
        self.get_personal_from_server()
        self.reporte_diario_submitted = False  # Flag for single submission
        self.requerimiento_materiales_submitted = False  # Flag for single submission

    def show_reporte_diario_screen(self):
        if not self.reporte_diario_submitted:
            self.reporte_diario_screen = ReporteDiarioObraScreen(self)
            Window.clearcolor = BG_COLOR
            self.root_window.remove_widget(self.main_screen_layout)
            self.root_window.add_widget(self.reporte_diario_screen)
        else:
            self.show_already_submitted_popup("Reporte Diario de Obra")

    def show_requerimiento_materiales_screen(self):
        if not self.requerimiento_materiales_submitted:
            self.requerimiento_materiales_screen = RequerimientoMaterialesScreen(self)
            Window.clearcolor = BG_COLOR
            self.root_window.remove_widget(self.main_screen_layout)
            self.root_window.add_widget(self.requerimiento_materiales_screen)
        else:
            self.show_already_submitted_popup("Requerimiento de Materiales")

    def show_already_submitted_popup(self, form_name):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        message_label = Label(text=f"Ya has enviado el formulario de {form_name} una vez. Cierra y vuelve a abrir la aplicación para enviar de nuevo.", font_size=label_font_size, color=WHITE, halign='center')
        content.add_widget(message_label)

        popup = Popup(
            title='Formulario ya enviado',
            content=content,
            size_hint=(None, None),
            size=(dp(500), dp(250)),
            auto_dismiss=True,
            separator_height=0,
            background_color = (0.1, 0.1, 0.1, 0.9)
        )
        popup.open()

    def go_back_to_main_screen(self, current_screen):
        Window.clearcolor = BG_COLOR
        self.root_window.remove_widget(current_screen)
        self.root_window.add_widget(self.main_screen_layout)


    def get_materiales_from_server(self):
        try:
            response = requests.get(f"{API_URL}/api/materiales", timeout=10)
            response.raise_for_status()
            self.materiales_data = response.json()
            print("Materiales cargados exitosamente.")
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor.")
            self.materiales_data = []
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al conectar al servidor.")
            self.materiales_data = []
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener materiales del servidor: {e}")
            self.materiales_data = []

    def get_equipos_from_server(self):
        try:
            response = requests.get(f"{API_URL}/api/equipos", timeout=10)
            response.raise_for_status()
            self.equipos_data = response.json()
            print("Equipos cargados exitosamente.")
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor.")
            self.equipos_data = []
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al conectar al servidor.")
            self.equipos_data = []
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener equipos del servidor: {e}")
            self.equipos_data = []

    def get_vehiculos_from_server(self):
        try:
            response = requests.get(f"{API_URL}/api/vehiculos", timeout=10)
            response.raise_for_status()
            self.vehiculos_data = response.json()
            print("Vehículos cargados exitosamente.")
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor.")
            self.vehiculos_data = []
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al conectar al servidor.")
            self.vehiculos_data = []
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener vehículos del servidor: {e}")
            self.vehiculos_data = []

    def get_personal_from_server(self):
        try:
            response = requests.get(f"{API_URL}/api/personal", timeout=10)
            response.raise_for_status()
            personal_data = response.json()
            for person in personal_data:
                person['NOMBRE_COMPLETO'] = person['AP. PATERNO'] + ' ' + person.get('AP. MATERNO', '') + ', ' + person['NOMBRES']
            self.personal_data = personal_data
            print("Personal de campo cargado exitosamente.")
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor.")
            self.personal_data = []
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al conectar al servidor.")
            self.personal_data = []
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener personal del servidor: {e}")
            self.personal_data = []


class RequerimientoMaterialesScreen(BoxLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.orientation='vertical'
        self.padding = dp(margin)
        self.spacing = dp(margin)

        self.requerimientos_seleccionados = []
        self.materiales_data = main_app.materiales_data
        self.equipos_data = main_app.equipos_data

        self.material_popup = MaterialSelectionPopupRequerimiento(add_callback=self.add_requerimiento_material, main_app=self)
        self.equipo_popup = EquipoSelectionPopupRequerimiento(add_callback=self.add_requerimiento_equipo, main_app=self)  # Use new EquipoSelectionPopupRequerimiento

        self.fecha_input = create_text_input(hint_text='Fecha (DD/MM/YYYY)')  # Added Fecha label
        self.fecha_input.text = datetime.now().strftime('%d/%m/%Y')
        self.codigo_obra_input = create_text_input(hint_text='Código de Obra')
        self.nombre_ingeniero_input = create_text_input(hint_text='Nombre del Ingeniero')

        self.materiales_button = create_button('Agregar Material', color=GREEN, on_press=self.show_material_popup)
        self.equipos_button = create_button('Agregar Equipo', color=GREEN, on_press=self.show_equipo_popup)
        self.enviar_button = create_button('ENVIAR REQUERIMIENTOS', color=BTN_COLOR, on_press=self.enviar_requerimientos)
        self.enviar_button.disabled = main_app.requerimiento_materiales_submitted  # Disable button if already submitted

        self.selected_items_scroll = ScrollView(size_hint_y=0.5)
        self.selected_items_grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.selected_items_grid.bind(minimum_height=self.selected_items_grid.setter('height'))
        self.selected_items_scroll.add_widget(self.selected_items_grid)

        self.add_widget(create_label("Requerimiento de Materiales", titulo=True))
        self.add_widget(create_label("Fecha"))
        self.add_widget(self.fecha_input)
        self.add_widget(create_label("Código de Obra"))
        self.add_widget(self.codigo_obra_input)
        self.add_widget(create_label("Nombre del Ingeniero"))
        self.add_widget(self.nombre_ingeniero_input)
        self.add_widget(self.materiales_button)
        self.add_widget(self.equipos_button)
        self.add_widget(create_label("Requerimientos Seleccionados", titulo=True))
        self.add_widget(self.selected_items_scroll)
        self.add_widget(self.enviar_button)

        self.update_selected_items_display()

    def show_material_popup(self, instance):
        self.material_popup.open()

    def show_equipo_popup(self, instance):
        self.equipo_popup.open()

    def add_requerimiento_material(self, material_name, unit, quantity, is_new_material=False):
        try:
            quantity = float(quantity)
        except ValueError:
            print("Cantidad inválida. Por favor, ingrese un número.")
            return

        requerimiento_entry = MaterialEntry(material_name, unit, float(quantity))
        self.requerimientos_seleccionados.append(requerimiento_entry)
        self.update_selected_items_display()

    def add_requerimiento_equipo(self, equipo_name, cantidad, unidad, is_new_equipo=False):  # unidad instead of propiedad
        requerimiento_entry = RequerimientoEquipoEntry(equipo_name, unidad, cantidad)  # Use RequerimientoEquipoEntry
        self.requerimientos_seleccionados.append(requerimiento_entry)
        self.update_selected_items_display()

    def update_selected_items_display(self):
        self.selected_items_grid.clear_widgets()
        grid = self.selected_items_grid
        grid.spacing = dp(5)
        grid.padding = dp(5)

        for item in self.requerimientos_seleccionados:
            card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(80),
                spacing=dp(5),
                padding=dp(5),
            )
            with card.canvas.before:
                Color(*ITEM_BG_COLOR)
                Rectangle(pos=card.pos, size=card.size)

            text_layout = BoxLayout(
                orientation='vertical',
                size_hint_x=0.8,
                padding=[0,0,0,0]
            )

            nombre_label = Label(
                text=f"[b]{item.nombre}[/b]",
                markup=True,
                font_size=label_font_size,
                halign='left',
                valign='middle',
                color=WHITE,
                size_hint_y=0.5,
                text_size=(None, None),
                padding=[0,0]
            )

            if isinstance(item, MaterialEntry):
                detalles_label = Label(
                    text=f"[size={int(label_font_size)}]{item.cantidad} {item.unidad}[/size]",
                    markup=True,
                    halign='left',
                    valign='middle',
                    color=WHITE,
                    size_hint_y=0.5,
                    text_size=(Window.width * 0.6, None),
                    padding=[0,0]
                )
            elif isinstance(item, RequerimientoEquipoEntry):  # Handle RequerimientoEquipoEntry
                detalles_label = Label(
                    text=f"[size={int(label_font_size)}]{item.cantidad} {item.unidad}[/size]",  # Use item.unidad here
                    markup=True,
                    halign='left',
                    valign='middle',
                    color=WHITE,
                    size_hint_y=0.5,
                    text_size=(Window.width * 0.6, None),
                    padding=[0,0]
                )
            else:
                detalles_label = Label(text="")

            text_layout.add_widget(nombre_label)
            text_layout.add_widget(detalles_label)

            delete_btn = Button(
                text='×',
                font_size=label_font_size,
                bold=True,
                size_hint_x=None,
                width=dp(40),
                background_color=RED,
                background_normal='',
                on_press=lambda btn, req_item=item, card_widget=card: self.remove_requerimiento_item(req_item, card_widget)
            )

            card.add_widget(text_layout)
            card.add_widget(delete_btn)
            self.selected_items_grid.add_widget(card)

    def remove_requerimiento_item(self, item_entry, item_layout):
        self.requerimientos_seleccionados.remove(item_entry)
        self.selected_items_grid.remove_widget(item_layout)
        self.update_selected_items_display()

    def enviar_requerimientos(self, instance):
        if not self.validar_requerimientos():
            return

        datos = {
            "fecha": self.fecha_input.text,  # Added fecha
            "codigo_obra": self.codigo_obra_input.text,
            "nombre_ingeniero": self.nombre_ingeniero_input.text,
            "requerimientos": [item.to_dict() for item in self.requerimientos_seleccionados]  # to_dict() will work for both MaterialEntry and RequerimientoEquipoEntry
        }

        print("Datos a enviar requerimientos:", datos)  # Log datos before sending

        try:
            response = requests.post(f"{API_URL}/recibir-requerimientos", json=datos, timeout=20)  # Corrected URL
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            if response.status_code == 200:
                print("Requerimientos enviados exitosamente")
                self.requerimientos_seleccionados = []
                self.update_selected_items_display()
                self.show_success_popup()
                self.enviar_button.disabled = True  # Disable button after successful submission
                self.main_app.requerimiento_materiales_submitted = True  # Set flag in main app
            else:
                print(f"Error al enviar requerimientos: {response.status_code} - {response.text}")
                print(f"Error detail: {response.text}")  # Print the error detail
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor para enviar los requerimientos.")
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al enviar los requerimientos al servidor.")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar los requerimientos: {e}")
            print(f"Detailed error: {e.response.text if e.response else e}")  # Print more details if available

    def validar_requerimientos(self):
        if not self.fecha_input.text:  # Added fecha validation
            print("El campo 'Fecha' es obligatorio.")
            return False
        try:
            datetime.strptime(self.fecha_input.text, '%d/%m/%Y')
        except ValueError:
            print("Formato de fecha inválido. Use DD/MM/YYYY.")
            return False
        if not self.codigo_obra_input.text:
            print("El campo 'Código de Obra' es obligatorio.")
            return False
        if not self.nombre_ingeniero_input.text:
            print("El campo 'Nombre del Ingeniero' es obligatorio.")
            return False
        if not self.requerimientos_seleccionados:
            print("Debe seleccionar al menos un material o equipo.")
            return False
        return True

    def show_success_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        message_label = Label(text="Los requerimientos se han enviado correctamente", font_size=label_font_size, color=WHITE)
        content.add_widget(message_label)

        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(400), dp(200)),
            auto_dismiss=True,
            separator_height=0,
            background_color = (0.1, 0.1, 0.1, 0.9)
        )
        popup.open()
        anim = Animation(opacity=0, duration=3.0) + Animation(size=(0, 0), duration=3.0)
        anim.bind(on_complete=lambda *args: popup.dismiss())
        anim.start(popup)


class MaterialSelectionPopupRequerimiento(Popup):
    def __init__(self, add_callback, main_app, **kwargs):
        self.add_callback = add_callback
        self.main_app = main_app
        kwargs.pop('add_callback', None)
        kwargs.pop('main_app', None)
        super().__init__(**kwargs)
        self.title = "Selección de Materiales"
        self.size_hint = (0.9, 0.9)
        self.is_new_material = False

        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        search_layout = BoxLayout(size_hint_y=None, height=dp(40))
        self.search_input = TextInput(
            hint_text='Buscar material...',
            multiline=False,
            size_hint=(1, None),
            height=dp(40)
        )
        search_layout.add_widget(self.search_input)

        scroll = ScrollView(size_hint_y=0.5)
        self.materials_list = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        self.materials_list.bind(minimum_height=self.materials_list.setter('height'))
        scroll.add_widget(self.materials_list)

        selection_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.5, height=dp(120), padding=dp(10))

        self.material_name = Label(text="Material: ")
        self.unit_input = TextInput(hint_text='Unidad', multiline=False, size_hint_y=None, height=dp(40))
        self.quantity_input = TextInput(hint_text='Cantidad', multiline=False, input_filter='float', size_hint_y=None,
                                        height=dp(40))

        selection_layout.add_widget(Label(text="Unidad:"))
        selection_layout.add_widget(self.unit_input)
        selection_layout.add_widget(Label(text="Cantidad:"))
        selection_layout.add_widget(self.quantity_input)

        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_button = Button(text='Cancelar', size_hint_x=0.5, background_color=RED)
        add_button = Button(text='Agregar', size_hint_x=0.5, background_color=GREEN)

        cancel_button.bind(on_release=self.dismiss)
        add_button.bind(on_release=self.add_material)

        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(add_button)

        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(selection_layout)
        layout.add_widget(buttons_layout)

        self.content = layout
        self.search_input.bind(text=self.on_search_text)

    def on_search_text(self, instance, value):
        self.materials_list.clear_widgets()
        if not value:
            return

        filtered_materials = [m['nombre_material'] for m in self.main_app.materiales_data if
                              value.lower() in m['nombre_material'].lower()]

        for material in filtered_materials:
            btn = Button(text=material, size_hint_y=None, height=dp(40), background_color=GRAY)
            btn.bind(on_release=lambda btn: self.select_material(btn.text))
            self.materials_list.add_widget(btn)

        unique_material_names = [m['nombre_material'] for m in self.main_app.materiales_data]
        if value and value not in filtered_materials and value not in unique_material_names:
            new_btn = Button(text=f"Agregar nuevo material: {value}", size_hint_y=None, height=dp(40),
                             background_color=GREEN)
            new_btn.bind(on_release=lambda btn: self.select_new_material(value))
            self.materials_list.add_widget(new_btn)

    def select_material(self, material_name):
        self.material_name.text = f"Material: {material_name}"
        self.unit_input.readonly = False
        self.unit_input.text = ""
        self.is_new_material = False
        for material in self.main_app.materiales_data:
            if material['nombre_material'] == material_name:
                unit = material['unidad']
                self.unit_input.text = unit
                break
        self.materials_list.clear_widgets()
        self.search_input.text = material_name

    def select_new_material(self, material_name):
        self.material_name.text = f"Material: {material_name}"
        self.unit_input.readonly = False
        self.unit_input.text = ""
        self.is_new_material = True
        self.materials_list.clear_widgets()
        self.search_input.text = material_name

    def add_material(self, *args):
        material_name = self.material_name.text.replace("Material: ", "")
        unit = self.unit_input.text
        quantity = self.quantity_input.text

        if not all([material_name, unit, quantity]):
            return

        try:
            quantity = float(quantity)
            self.add_callback(material_name, unit, quantity, self.is_new_material)
            self.search_input.text = ''
            self.unit_input.text = ''
            self.quantity_input.text = ''
            self.material_name.text = 'Material: '
            self.is_new_material = False
            self.dismiss()
        except ValueError:
            print("Por favor ingrese una cantidad válida")


class EquipoSelectionPopupRequerimiento(Popup):  # Popup for Requerimiento Materiales - Modified
    def __init__(self, add_callback, main_app, **kwargs):
        self.add_callback = add_callback
        self.main_app = main_app
        kwargs.pop('add_callback', None)
        kwargs.pop('main_app', None)
        super().__init__(**kwargs)
        self.title = "Selección de Equipos"
        self.size_hint = (0.9, 0.9)
        self.is_new_equipo = False

        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        search_layout = BoxLayout(size_hint_y=None, height=dp(40))
        self.search_input = TextInput(
            hint_text='Buscar equipo...',
            multiline=False,
            size_hint=(1, None),
            height=dp(40)
        )
        search_layout.add_widget(self.search_input)

        scroll = ScrollView(size_hint_y=0.5)
        self.equipos_list = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.equipos_list.bind(minimum_height=self.equipos_list.setter('height'))
        scroll.add_widget(self.equipos_list)

        selection_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.5, height=dp(120), padding=dp(10))

        self.equipo_name = Label(text="Equipo: ")
        self.unidad_input = TextInput(hint_text='Unidad', multiline=False, size_hint_y=None,
                                      height=dp(40))  # Changed to unidad_input - Now Unidad is used for Requerimiento
        self.quantity_input = TextInput(hint_text='Cantidad', multiline=False, input_filter='float', size_hint_y=None,
                                        height=dp(40))

        selection_layout.add_widget(Label(
            text="Unidad:"))  # Changed to Unidad Label - Now Unidad is used for Requerimiento
        selection_layout.add_widget(
            self.unidad_input)  # Changed to unidad_input
        selection_layout.add_widget(Label(text="Cantidad:"))
        selection_layout.add_widget(self.quantity_input)

        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_button = Button(text='Cancelar', size_hint_x=0.5, background_color=RED)
        add_button = Button(text='Agregar', size_hint_x=0.5, background_color=GREEN)  # Corrected: Set background_color here

        cancel_button.bind(on_release=self.dismiss)
        add_button.bind(on_release=self.add_equipo_requerimiento)  # Changed to add_equipo_requerimiento

        buttons_layout.add_widget(cancel_button)
        buttons_layout.add_widget(add_button)

        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(selection_layout)
        layout.add_widget(buttons_layout)

        self.content = layout
        self.search_input.bind(text=self.on_search_text)

    def on_search_text(self, instance, value):  # For Requerimiento Materiales - No changes needed
        self.equipos_list.clear_widgets()
        if not value:
            return

        filtered_equipos = [e['nombre_equipo'] for e in self.main_app.equipos_data if
                            value.lower() in e['nombre_equipo'].lower()]

        for equipo in filtered_equipos:
            btn = Button(text=equipo, size_hint_y=None, height=dp(40), background_color=GRAY)
            btn.bind(on_release=lambda btn: self.select_equipo(btn.text))
            self.equipos_list.add_widget(btn)

        unique_equipo_names = [e['nombre_equipo'] for e in self.main_app.equipos_data]
        if value and value not in filtered_equipos and value not in unique_equipo_names:
            new_btn = Button(text=f"Agregar nuevo equipo: {value}", size_hint_y=None, height=dp(40),
                             background_color=GREEN)
            new_btn.bind(on_release=lambda btn: self.select_new_equipo(value))
            self.equipos_list.add_widget(new_btn)

    def select_equipo(self, equipo_name):  # For Requerimiento Materiales - No changes needed
        self.equipo_name.text = f"Equipo: {equipo_name}"
        self.unidad_input.readonly = False  # Changed to unidad_input
        self.unidad_input.text = ""  # Changed to unidad_input
        self.is_new_equipo = False
        for equipo in self.main_app.equipos_data:
            if equipo['nombre_equipo'] == equipo_name:
                unidad = "und"  # Default unidad for equipos in requerimientos
                self.unidad_input.text = unidad  # Changed to unidad_input
                break
        self.equipos_list.clear_widgets()
        self.search_input.text = equipo_name

    def select_new_equipo(self, equipo_name):  # For Requerimiento Materiales - No changes needed
        self.equipo_name.text = f"Equipo: {equipo_name}"
        self.unidad_input.readonly = False  # Changed to unidad_input
        self.unidad_input.text = ""  # Changed to unidad_input
        self.is_new_equipo = True
        self.equipos_list.clear_widgets()
        self.search_input.text = equipo_name

    def add_equipo_requerimiento(self, *args):  # Changed function name and logic for Requerimiento
        equipo_name = self.equipo_name.text.replace("Equipo: ", "")
        unidad = self.unidad_input.text  # Now unidad is taken from unidad_input
        cantidad = self.quantity_input.text

        if not all([equipo_name, unidad, cantidad]):  # Now check for unidad as well
            return

        try:
            cantidad = float(cantidad)
            self.add_callback(equipo_name, cantidad, unidad, self.is_new_equipo)  # Pass unidad to add_callback
            self.search_input.text = ''
            self.unidad_input.text = ''  # Clear unidad_input
            self.quantity_input.text = ''
            self.equipo_name.text = 'Equipo: '
            self.is_new_equipo = False
            self.dismiss()
        except ValueError:
            print("Por favor ingrese una cantidad válida")


class ReporteDiarioObraScreen(BoxLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.orientation = 'vertical'

        self.respuestas = {}
        self.materiales_seleccionados = []
        self.equipos_seleccionados = []
        self.vehiculos_seleccionados = []
        self.personal_seleccionados = []
        self.materiales_data = main_app.materiales_data
        self.equipos_data = main_app.equipos_data
        self.vehiculos_data = main_app.vehiculos_data
        self.personal_data = main_app.personal_data
        self.new_materials_to_add = main_app.new_materials_to_add  # List to hold new materials to be added to CSV
        self.new_equipos_to_add = main_app.new_equipos_to_add  # List to hold new equipos to be added to CSV
        self.new_vehiculos_to_add = main_app.new_vehiculos_to_add  # List to hold new vehiculos to be added to CSV
        self.new_personal_to_add = main_app.new_personal_to_add  # List to hold new personal to be added to CSV
        self.submit_button = None  # Initialize submit_button as class attribute

        self.campos = [
            {"nombre": "fecha", "tipo": "date", "etiqueta": "Fecha"},
            {"nombre": "codigo_obra", "tipo": "text", "etiqueta": "Código de Obra"},
            {"nombre": "nombre_ingeniero", "tipo": "text", "etiqueta": "Nombre del Ingeniero"},
            {"nombre": "nombre_supervisor", "tipo": "text", "etiqueta": "Nombre del Supervisor Seguridad"},
            {"nombre": "actividad_principal", "tipo": "text", "etiqueta": "Actividad Realizada"},
            {"nombre": "materiales_usados", "tipo": "material", "etiqueta": "Materiales Usados"},
            {"nombre": "equipos_usados", "tipo": "equipo", "etiqueta": "Equipos Usados"},
            {"nombre": "vehiculos_usados", "tipo": "vehiculo", "etiqueta": "Vehículos Usados"},
            {"nombre": "personal_de_campo", "tipo": "personal", "etiqueta": "Personal de Campo"},
            {"nombre": "supervisor_presente", "tipo": "bool", "etiqueta": "¿Supervisor Presente?"},
            {"nombre": "avance_diario", "tipo": "text", "etiqueta": "Avance Diario"},
            {"nombre": "incidentes", "tipo": "text", "etiqueta": "Incidentes ocurridos"},
            {"nombre": "siguiente_dia", "tipo": "text", "etiqueta": "Plan para Siguiente Día"},
            {"nombre": "observaciones", "tipo": "text", "etiqueta": "Observaciones"}
        ]

        form_layout = BoxLayout(orientation='vertical', spacing=dp(margin), padding=(dp(margin), dp(margin)),
                                size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter("height"))

        for campo in self.campos:
            if campo["nombre"] in ["materiales_usados", "equipos_usados", "vehiculos_usados", "personal_de_campo"]:
                form_layout.add_widget(create_label(campo["etiqueta"], titulo=True))
                if campo["nombre"] == "materiales_usados":
                    self.setup_material_input(form_layout)
                elif campo["nombre"] == "equipos_usados":
                    self.setup_equipo_input(form_layout)
                elif campo["nombre"] == "vehiculos_usados":
                    self.setup_vehiculo_input(form_layout)
                elif campo["nombre"] == "personal_de_campo":
                    self.setup_personal_input(form_layout)
                continue

            form_layout.add_widget(create_label(campo["etiqueta"], titulo=True))

            if campo["tipo"] == "bool":
                input_widget = Spinner(
                    text='Sí',
                    values=('Sí', 'No'),
                    size_hint=(1, None),
                    height=dp(input_height),
                    pos_hint={'center_x': 0.5},
                    background_color=GRAY,
                    color=WHITE,
                    font_size=label_font_size
                )
            else:
                input_widget = create_text_input()
                if campo["nombre"] == "fecha":
                    input_widget.text = datetime.now().strftime('%d/%m/%Y')

            self.respuestas[campo["nombre"]] = input_widget
            form_layout.add_widget(input_widget)

        self.submit_button = create_button('ENVIAR DATOS', size=(400, button_height), color=BTN_COLOR,
                                           on_press=self.confirmar_envio)  # Assign to self.submit_button
        self.submit_button.font_size = label_font_size
        self.submit_button.disabled = main_app.reporte_diario_submitted  # Disable button if already submitted
        form_layout.add_widget(Widget(size_hint_y=None, height=dp(margin * 0.1)))
        form_layout.add_widget(self.submit_button)

        self.material_popup = MaterialSelectionPopup(add_callback=self.add_material_with_quantity, main_app=self)
        self.equipo_popup = EquipoSelectionPopup(add_callback=self.add_equipo_with_quantity, main_app=self)
        self.vehiculo_popup = VehiculoSelectionPopup(add_callback=self.add_vehiculo_with_placa_propiedad, main_app=self)
        self.personal_popup = PersonalSelectionPopup(add_callback=self.add_personal_with_horas_extras, main_app=self)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll.add_widget(form_layout)

        self.add_widget(scroll)

    def setup_material_input(self, form_layout):
        material_layout = BoxLayout(orientation='vertical', spacing=dp(margin), size_hint_y=None)
        material_layout.bind(minimum_height=material_layout.setter("height"))
        self.materiales_button = create_button('Seleccionar Materiales', size=(400, button_height), color=GREEN,
                                               on_press=self.show_material_popup)
        material_layout.add_widget(self.materiales_button)
        form_layout.add_widget(material_layout)

    def setup_equipo_input(self, form_layout):
        equipo_layout = BoxLayout(orientation='vertical', spacing=dp(margin), size_hint_y=None)
        equipo_layout.bind(minimum_height=equipo_layout.setter("height"))
        self.equipos_button = create_button('Seleccionar Equipos', size=(400, button_height), color=GREEN,
                                            on_press=self.show_equipo_popup)
        equipo_layout.add_widget(self.equipos_button)
        form_layout.add_widget(equipo_layout)

    def setup_vehiculo_input(self, form_layout):
        vehiculo_layout = BoxLayout(orientation='vertical', spacing=dp(margin), size_hint_y=None)
        vehiculo_layout.bind(minimum_height=vehiculo_layout.setter("height"))
        self.vehiculos_button = create_button('Seleccionar Vehículos', size=(400, button_height), color=GREEN,
                                              on_press=self.show_vehiculo_popup)
        vehiculo_layout.add_widget(self.vehiculos_button)
        form_layout.add_widget(vehiculo_layout)

    def setup_personal_input(self, form_layout):
        personal_layout = BoxLayout(orientation='vertical', spacing=dp(margin), size_hint_y=None)
        personal_layout.bind(minimum_height=personal_layout.setter("height"))
        self.personal_button = create_button('Seleccionar Personal', size=(400, button_height), color=GREEN,
                                             on_press=self.show_personal_popup)
        personal_layout.add_widget(self.personal_button)
        form_layout.add_widget(personal_layout)

    def show_material_popup(self, instance):
        if self.materiales_seleccionados:
            self.materiales_button.background_color = BTN_COLOR
        else:
            self.materiales_button.background_color = GREEN
        self.material_popup.open()

    def show_equipo_popup(self, instance):
        if self.equipos_seleccionados:
            self.equipos_button.background_color = BTN_COLOR
        else:
            self.equipos_button.background_color = GREEN
        self.equipo_popup.open()

    def show_vehiculo_popup(self, instance):
        if self.vehiculos_seleccionados:
            self.vehiculos_button.background_color = BTN_COLOR
        else:
            self.vehiculos_button.background_color = GREEN
        self.vehiculo_popup.open()

    def show_personal_popup(self, instance):
        if self.personal_seleccionados:
            self.personal_button.background_color = BTN_COLOR
        else:
            self.personal_button.background_color = GREEN
        self.personal_popup.open()

    def add_material_with_quantity(self, material_name, unit, quantity, is_new_material=False):
        try:
            float(quantity)
        except ValueError:
            print("Cantidad inválida. Por favor, ingrese un número.")
            return

        material_entry = MaterialEntry(material_name, unit, float(quantity))
        self.materiales_seleccionados.append(material_entry)
        if is_new_material:
            self.new_materials_to_add.append(
                {'nombre_material': material_name, 'unidad': unit})  # Add to new items list
        self.material_popup.update_selected_materials_display()
        self.materiales_button.background_color = BTN_COLOR

    def add_equipo_with_quantity(self, equipo_name, cantidad, propiedad, is_new_equipo=False):
        equipo_entry = EquipoEntry(equipo_name, cantidad, propiedad)
        self.equipos_seleccionados.append(equipo_entry)
        if is_new_equipo:
            self.new_equipos_to_add.append({'nombre_equipo': equipo_name, 'propiedad': propiedad})
        self.equipo_popup.update_selected_equipos_display()
        self.equipos_button.background_color = BTN_COLOR

    def add_vehiculo_with_placa_propiedad(self, vehiculo_name, placa, propiedad, is_new_vehiculo=False):
        vehiculo_entry = VehiculoEntry(vehiculo_name, placa, propiedad)
        self.vehiculos_seleccionados.append(vehiculo_entry)
        if is_new_vehiculo:
            self.new_vehiculos_to_add.append({'nombre_vehiculo': vehiculo_name, 'placa': placa, 'propiedad': propiedad})
        self.vehiculo_popup.update_selected_vehiculos_display()
        self.vehiculos_button.background_color = BTN_COLOR

    def add_personal_with_horas_extras(self, nombre_completo, categoria, horas_extras, is_new_personal=False):
        personal_entry = PersonalEntry(nombre_completo, categoria, horas_extras)
        self.personal_seleccionados.append(personal_entry)
        if is_new_personal:
            self.new_personal_to_add.append({'nombre_completo': nombre_completo, 'categoria': categoria})
        self.personal_popup.update_selected_personal_display()
        self.personal_button.background_color = BTN_COLOR

    def remove_material(self, material_entry, material_layout):
        self.materiales_seleccionados.remove(material_entry)
        self.material_popup.update_selected_materials_display()
        if not self.materiales_seleccionados:
            self.materiales_button.background_color = GREEN

    def remove_equipo(self, equipo_entry, equipo_layout):
        self.equipos_seleccionados.remove(equipo_entry)
        self.equipo_popup.update_selected_equipos_display()
        if not self.equipos_seleccionados:
            self.equipos_button.background_color = GREEN

    def remove_vehiculo(self, vehiculo_entry, vehiculo_layout):
        self.vehiculos_seleccionados.remove(vehiculo_entry)
        self.vehiculo_popup.update_selected_vehiculos_display()
        if not self.vehiculos_seleccionados:
            self.vehiculos_button.background_color = GREEN

    def remove_personal(self, personal_entry, personal_layout):
        self.personal_seleccionados.remove(personal_entry)
        self.personal_popup.update_selected_personal_display()
        if not self.personal_seleccionados:
            self.personal_button.background_color = GREEN

    def show_success_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        message_label = Label(text="Los datos se han enviado correctamente", font_size=label_font_size, color=WHITE)
        content.add_widget(message_label)

        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(400), dp(200)),
            auto_dismiss=True,
            separator_height=0,
            background_color=(0.1, 0.1, 0.1, 0.9)
        )
        popup.open()
        anim = Animation(opacity=0, duration=3.0) + Animation(size=(0, 0), duration=3.0)
        anim.bind(on_complete=lambda *args: popup.dismiss())
        anim.start(popup)

    def confirmar_envio(self, instance):
        if not self.validar_datos():
            return

        # Add new items to CSVs first
        new_items_added_successfully = True
        for material_data in self.new_materials_to_add:
            response = requests.post(f"{API_URL}/api/materiales/new", json=material_data, timeout=10)
            if response.status_code != 201:
                print(f"Error adding new material: {response.status_code} - {response.text}")
                new_items_added_successfully = False
                break
        if not new_items_added_successfully: return False

        for equipo_data in self.new_equipos_to_add:
            response = requests.post(f"{API_URL}/api/equipos/new", json=equipo_data, timeout=10)
            if response.status_code != 201:
                print(f"Error adding new equipo: {response.status_code} - {response.text}")
                new_items_added_successfully = False
                break
        if not new_items_added_successfully: return False

        for vehiculo_data in self.new_vehiculos_to_add:
            response = requests.post(f"{API_URL}/api/vehiculos/new", json=vehiculo_data, timeout=10)
            if response.status_code != 201:
                print(f"Error adding new vehiculo: {response.status_code} - {response.text}")
                new_items_added_successfully = False
                break
        if not new_items_added_successfully: return False

        for personal_data in self.new_personal_to_add:
            response = requests.post(f"{API_URL}/api/personal/new", json=personal_data, timeout=10)
            if response.status_code != 201:
                print(f"Error adding new personal: {response.status_code} - {response.text}")
                new_items_added_successfully = False
                break
        if not new_items_added_successfully: return False

        datos = {
            campo["nombre"]: (
                [material.to_dict() for material in self.materiales_seleccionados] if campo["nombre"] == "materiales_usados" else
                [equipo.to_dict() for equipo in self.equipos_seleccionados] if campo["nombre"] == "equipos_usados" else
                [vehiculo.to_dict() for vehiculo in self.vehiculos_seleccionados] if campo["nombre"] == "vehiculos_usados" else
                [personal.to_dict() for personal in self.personal_seleccionados] if campo["nombre"] == "personal_de_campo" else
                (self.respuestas[campo["nombre"]].text == "Sí" if campo["tipo"] == "bool" else
                 (float(self.respuestas[campo["nombre"]].text) if campo["tipo"] == "float" else self.respuestas[campo["nombre"]].text))
            )
            for campo in self.campos
        }
        print("Datos a enviar reporte diario:", datos)  # Log datos before sending

        try:
            response = requests.post(f"{API_URL}/recibir-datos", json=datos, timeout=20)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            if response.status_code == 200:
                print("Datos enviados exitosamente")
                self.materiales_seleccionados = []
                self.equipos_seleccionados = []
                self.vehiculos_seleccionados = []
                self.personal_seleccionados = []
                self.new_materials_to_add = []  # Clear new materials list
                self.new_equipos_to_add = []  # Clear new equipos list
                self.new_vehiculos_to_add = []  # Clear new vehiculos list
                self.new_personal_to_add = []  # Clear new personal list
                self.show_success_popup()
                self.submit_button.disabled = True  # Disable button after successful submission # Removed, submit_button not defined here.
                self.main_app.reporte_diario_submitted = True  # Set flag in main app
                instance.disabled = True  # Disable the button that called this function.
            else:
                print(f"Error al enviar datos: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"Error: No se pudo conectar al servidor para enviar los datos.")
        except requests.exceptions.Timeout:
            print(f"Error: Tiempo de espera agotado al enviar los datos al servidor.")
        except Exception as e:
            print(f"Error al enviar los datos: {e}")
            if isinstance(e, requests.exceptions.RequestException):  # Check if it's a RequestException
                print(f"Detailed error: {e.response.text if e.response else e}")  # Print response text if available
            else:  # Handle other exceptions
                print(f"Detailed error: {e}")

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
            elif campo["nombre"] == "personal_de_campo":
                if not self.personal_seleccionados:
                    print("Debe seleccionar al menos un personal de campo.")
                    return False
            else:
                valor = self.respuestas[campo["nombre"]].text
                if campo["nombre"] == "fecha":
                    try:
                        datetime.strptime(valor, '%d/%m/%Y')
                    except ValueError:
                        print("Formato de fecha inválido. Use DD/MM/YYYY.")
                        return False
                if not valor and campo["nombre"] not in ["observaciones", "incidentes", "siguiente_dia"]:
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