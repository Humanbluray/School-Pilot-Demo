import flet as ft
from utils.couleurs import *

login_style = {'border_radius': 6, 'text_style': ft.TextStyle(size=14, font_family='PPM', color='black'),
               'label_style': ft.TextStyle(size=13, font_family='PPM', color='black'),
               'hint_style': ft.TextStyle(size=13, font_family='PPM', color='black'), 'border_width': 1, 'focused_border_width': 1,
               'cursor_height': 24, 'content_padding': 12,
               'cursor_color': 'black', 'dense': True, 'focused_bgcolor': '#c4c4cc', 'focused_border_color': '#c4c4cc'}

cool_style = {'border_radius': 6, 'text_style': ft.TextStyle(size=14, font_family='PPM', color='black'),
               'label_style': ft.TextStyle(size=13, font_family='PPM', color='black'),
               'hint_style': ft.TextStyle(size=13, font_family='PPM', color='black'), 'border_width': 1, 'focused_border_width': 1,
               'cursor_height': 24, 'content_padding': 12,
               'cursor_color': 'black87', 'dense': True, 'focused_bgcolor': '#c4c4cc', 'focused_border_color': '#c4c4cc'}

other_style = {'border_radius': 6, 'text_style': ft.TextStyle(size=14, font_family='PPM', color='black'),
               'label_style': ft.TextStyle(size=13, font_family='PPM', color='black'),
               'hint_style': ft.TextStyle(size=13, font_family='PPM', color='black'), 'border_width': 1, 'focused_border_width': 1,
               'focused_border_color': '#f0f0f6', 'cursor_height': 24, 'content_padding': 12, 'bgcolor': '#f0f0f6',
               'cursor_color': 'black', 'dense': True, 'border_color': '#f0f0f6'}

numeric_style = {'border_radius': 6, 'text_style': ft.TextStyle(size=14, font_family='PPM', color='black'),
               'label_style': ft.TextStyle(size=13, font_family='PPM', color='black'),
               'hint_style': ft.TextStyle(size=13, font_family='PPM', color='black'), 'border_width': 1, 'focused_border_width': 1,
               'focused_border_color': '#f0f0f6', 'cursor_height': 24, 'content_padding': 12, 'bgcolor': '#f0f0f6',
               'cursor_color': 'black', 'dense': True, 'border_color': '#f0f0f6',
                'text_align': ft.TextAlign.RIGHT, 'input_filter': ft.NumbersOnlyInputFilter()
                 }

search_style = {'border_radius': 6, 'text_style': ft.TextStyle(size=14, font_family='PPM', color='black'),
                'label_style': ft.TextStyle(size=13, font_family='PPM', color='black'),
                'hint_style': ft.TextStyle(size=13, font_family='PPM', color='black'), 'border_width': 1,
                'focused_border_width': 1, 'cursor_height': 24, 'bgcolor': '#f0f0f6', 'border_color': '#f0f0f6',
                'content_padding': 12, 'cursor_color': 'black'}

drop_style: dict = dict(
    dense=True, border_radius=6,
    label_style=ft.TextStyle(size=12, font_family="PPM"),
    text_style=ft.TextStyle(size=13, font_family="PPM", color="black"),
    hint_style=ft.TextStyle(size=12, font_family="PPM", color="black"),
    border_width=1,
    editable=True, enable_filter=True, enable_search=True, max_menu_height=200,
    focused_border_color='black', focused_border_width=1
)
datatable_style: dict = dict(
    data_text_style=ft.TextStyle(size=13, font_family='PPM', color='black87'),
    heading_text_style=ft.TextStyle(size=13, font_family='PPM', color='grey'),
    horizontal_lines=ft.BorderSide(width=0, color='white'),
)




