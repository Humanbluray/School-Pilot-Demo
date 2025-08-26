import flet as ft
from services.async_functions.students_functions import *
from services.supabase_client import supabase_client
from components import MyButton, DateSelection, MyMiniIcon, ColoredButton, FlatButton, ColoredIconButton, ColoredIcon
from utils.styles import *
from utils.couleurs import *
from translations.translations import languages
from utils.useful_functions import format_number, add_separator
import os, qrcode, uuid, mimetypes, asyncio, threading
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import datetime
import os
import io

# Bucket for pictures
BUCKET_STUDENTS_PICTURES = "students_pictures"
BUCKET_REGISTRATIONS = 'receipts'
DEFAULT_IMAGE_URL = ''
selected_fees = ''


class Students(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center
        )
        # parent container (Home) ____________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # Widgets main window _________________________________________________________________
        self.current_year = ft.Text(f"{get_current_year_id()}")
        self.current_year_label = ft.Text(f"{get_current_year_label()}", size=11, color='indigo', font_family="PPM")
        self.search = ft.TextField(
            **cool_style, on_change=self.on_search_change,
            prefix_icon='search', width=300,
        )
        self.table = ft.DataTable(
            **datatable_style, expand=True,
            columns=[
                ft.DataColumn(ft.Text(languages[self.lang]['name'].capitalize())),
                ft.DataColumn(ft.Text(languages[self.lang]['profile'].capitalize())),
                ft.DataColumn(ft.Text(languages[self.lang]['class'].capitalize())),
                ft.DataColumn(ft.Text('Actions'))
            ]
        )

        self.registered_count = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.boys = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.girls = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.completed_rate = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.pb_rate = ft.ProgressBar(
            color=BASE_COLOR, bgcolor='amber50', height=10, border_radius=10, width=150
        )

        self.main_window = ft.Container(
            expand=True, content=ft.Column(
                expand=True, controls=[
                    ft.Text(languages[lang]['students table'].capitalize(), size=20, font_family='PPB'),
                    ft.Row(
                        expand=True,
                        controls=[
                            ft.Container(
                                expand=True, bgcolor='white', border_radius=16,
                                padding=0,
                                content=ft.Column(
                                    expand=True,
                                    controls=[
                                        ft.Container(
                                            padding=20, border=ft.border.all(1, "#f0f0f6"),
                                            content=ft.Row(
                                                controls=[
                                                    ft.Row(
                                                        controls=[
                                                            ColoredButton(
                                                                languages[self.lang]['new registration'],
                                                                ft.Icons.ADD_HOME,
                                                                self.open_ct_registrations
                                                            ),
                                                            ColoredButton(
                                                                languages[self.lang]['new student'],
                                                                ft.Icons.PERSON_ADD_OUTLINED,
                                                                self.open_new_student_container
                                                            ),
                                                            ColoredButton(
                                                                'discipline',
                                                                ft.Icons.EMERGENCY,
                                                                self.open_discipline_window
                                                            ),
                                                            ColoredButton(
                                                                languages[self.lang]['pdf format'],
                                                                ft.Icons.PICTURE_AS_PDF_SHARP,
                                                                None
                                                            ),
                                                            ColoredButton(
                                                                languages[self.lang]['xls format'],
                                                                ft.Icons.FILE_PRESENT,
                                                                None
                                                            )
                                                        ]
                                                    ),
                                                    self.search
                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            )
                                        ),
                                        ft.ListView(expand=True, controls=[self.table]),
                                        ft.Container(
                                            padding=10,
                                            content=ft.Row(
                                                controls=[
                                                    ft.IconButton(ft.Icons.KEYBOARD_ARROW_LEFT_ROUNDED,
                                                                  icon_color='black',icon_size=18),
                                                    ft.Text('page 1 de 1', size=13, font_family='PPM'),
                                                    ft.IconButton(ft.Icons.KEYBOARD_ARROW_RIGHT_ROUNDED,
                                                                  icon_color='black',icon_size=18),

                                                ], alignment=ft.MainAxisAlignment.END
                                            )
                                        )
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            ),
                            # KPI ...
                            ft.Column(
                                controls=[
                                    ft.Container(
                                        width=170, height=120, padding=10, border_radius=24,
                                        border=ft.border.all(1, 'white'),
                                        bgcolor='white',
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ColoredIcon(ft.Icons.GROUPS, 'indigo', 'indigo50'),
                                                        ft.Text(languages[self.lang]['head count'].upper(), size=12,
                                                                font_family='PPI',
                                                                color='indigo')
                                                    ], alignment=ft.MainAxisAlignment.START
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        self.registered_count,
                                                        ft.Text(languages[self.lang]['nb students'], size=11,
                                                                font_family='PPI',
                                                                color='grey')
                                                    ], spacing=0
                                                )
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),
                                    ft.Container(
                                        width=170, height=120, padding=10, border_radius=24,
                                        border=ft.border.all(1, 'white'),
                                        bgcolor='white',
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ColoredIcon(ft.Icons.MAN_2, 'teal', 'teal50'),
                                                        ft.Text(languages[self.lang]['boys'].upper(), size=12,
                                                                font_family='PPI',
                                                                color='teal')
                                                    ], alignment=ft.MainAxisAlignment.START
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        self.boys,
                                                        ft.Text(languages[self.lang]['boys registered'], size=11,
                                                                font_family='PPI',
                                                                color='grey')
                                                    ], spacing=0
                                                )
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),
                                    ft.Container(
                                        width=170, height=120, padding=10, border_radius=24,
                                        border=ft.border.all(1, 'white'),
                                        bgcolor='white',
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ColoredIcon(ft.Icons.WOMAN_2, 'deeporange', 'deeporange50'),
                                                        ft.Text(languages[self.lang]['girls'].upper(), size=12,
                                                                font_family='PPI',
                                                                color='deeporange')
                                                    ], alignment=ft.MainAxisAlignment.START
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        self.girls,
                                                        ft.Text(languages[self.lang]['girls registered'], size=11,
                                                                font_family='PPI',
                                                                color='grey')
                                                    ], spacing=0
                                                )
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),
                                    ft.Container(
                                        width=170, height=120, padding=10, border_radius=24,
                                        border=ft.border.all(1, 'white'),
                                        bgcolor='white',
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ColoredIcon(ft.Icons.PIE_CHART_ROUNDED, 'green', 'green50'),
                                                        ft.Text(languages[self.lang]['cp'].upper(), size=12,
                                                                font_family='PPI',
                                                                color='green')
                                                    ], alignment=ft.MainAxisAlignment.START
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        self.completed_rate,
                                                        ft.Text(languages[self.lang]['complete profiles'], size=11,
                                                                font_family='PPI',
                                                                color='grey')
                                                    ], spacing=0
                                                )
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    )
                                ]
                            ),
                        ]
                    )
                ],
            )
        )

        # New student window _____________________________________________________________________________________
        self.new_nom = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED, width=330,
            capitalization=ft.TextCapitalization.CHARACTERS
        )
        self.new_prenom = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED, width=330,
        )
        self.new_date = DateSelection(self)
        self.new_sex = ft.Dropdown(
            **drop_style, width=160, label=languages[self.lang]['gender'],
            prefix_icon=ft.Icons.WC_OUTLINED, options=[
                ft.dropdown.Option(gender) for gender in ['M', 'F']
            ]
        )
        self.new_lieu = ft.TextField(**cool_style, prefix_icon=ft.Icons.PLACE_OUTLINED, width=200)
        self.new_pere = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.MAN_3_OUTLINED, width=330,
            capitalization=ft.TextCapitalization.CHARACTERS
        )
        self.new_mere = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.WOMAN_OUTLINED, width=330,
            capitalization=ft.TextCapitalization.CHARACTERS
        )
        self.new_contact = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200, prefix_text="+237 ",
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.new_other = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200, prefix_text="+237 ",
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.new_residence = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, expand=True,
        )

        self.ct_new_student = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=700, height=650, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.PERSON_ADD, size=28, color='black'),
                                            ft.Text(languages[self.lang]['new student'], size=16, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_new_student_container
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['student info'].upper(), size=13,
                                                    font_family="PPB"),
                                            ft.Divider(height=1, thickness=1)
                                        ], spacing=0
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['name'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_nom
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['surname'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_prenom
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Row([self.new_date, self.new_sex,]),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['place of birth'], size=11,
                                                    font_family='PPM',
                                                    color='grey'),
                                            self.new_lieu,
                                        ], spacing=2
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['parent info'].upper(), size=11, font_family="PPB"),
                                            ft.Divider(height=1, thickness=1)
                                        ], spacing=0
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['father'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_pere
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['mother'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_mere
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Row(
                                        [
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['contact'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_contact
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['contact 2'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_other
                                                ], spacing=2
                                            )
                                        ]
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['residence'], size=11, font_family='PPM',
                                                    color='grey'),
                                            self.new_residence
                                        ], spacing=2
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row([MyButton(languages[self.lang]['valid'], 'check', 200, self.add_eleve)])
                                ], spacing=10,
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # Edit student window ______________________________________________________________________________________
        self.edit_id_student = ''
        self.edit_nom = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED, width=400, label=languages[self.lang]['name'],
            capitalization=ft.TextCapitalization.CHARACTERS
        )
        self.edit_prenom = ft.TextField(**login_style, prefix_icon=ft.Icons.PERSON_OUTLINE_OUTLINED, width=400)
        self.edit_mat = ft.TextField(
            **login_style, width=200, read_only=True
        )
        self.edit_date = ft.TextField(
            **login_style, width=150, prefix_icon=ft.Icons.CALENDAR_MONTH
        )
        self.edit_sex = ft.TextField(
            **login_style, width=120, prefix_icon='wc'
        )
        self.edit_lieu = ft.TextField(**login_style, prefix_icon=ft.Icons.PLACE_OUTLINED, width=200)
        self.edit_pere = ft.TextField(
            **login_style, prefix_icon=ft.Icons.MAN_3_OUTLINED, width=250,
            capitalization=ft.TextCapitalization.CHARACTERS
        )
        self.edit_mere = ft.TextField(
            **login_style, prefix_icon=ft.Icons.WOMAN_OUTLINED, width=250,
            capitalization=ft.TextCapitalization.CHARACTERS
        )
        self.edit_contact = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.edit_other = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.edit_residence = ft.TextField(
            **login_style, prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, width=250,
        )
        self.edit_image_url = ft.TextField(
            **other_style, read_only=True, prefix_icon=ft.Icons.PICTURE_IN_PICTURE_OUTLINED,
        )
        self.cp.fp_image_student.on_result = self.set_image_url
        self.image_button = MyButton(
            languages[self.lang]['load image'], ft.Icons.ADD_A_PHOTO_OUTLINED, 200,
            lambda _: self.cp.fp_image_student.pick_files(allow_multiple=False, allowed_extensions=['png', 'jpg', 'webp', 'avif'])
        )
        self.image_preview = ft.CircleAvatar(radius=50)
        self.ct_edit_student = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=650, height=650, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.EDIT, size=28, color='black'),
                                            ft.Text(languages[self.lang]['edit student'], size=16, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                                  on_click=self.close_ct_edit_student),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.image_preview,
                                            ft.Column(
                                                controls=[
                                                    ft.Column(
                                                        controls=[
                                                            ft.Text(languages[self.lang]['name'], color='grey', size=11, font_family='PPM'),
                                                            self.edit_nom
                                                        ], spacing=2
                                                    ),
                                                    ft.Column(
                                                        controls=[
                                                            ft.Text(languages[self.lang]['surname'], color='grey', size=11,
                                                                    font_family='PPM'),
                                                            self.edit_prenom
                                                        ], spacing=2
                                                    )
                                                ]
                                            )
                                        ], spacing=50
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['gender'], color='grey', size=11,
                                                            font_family='PPM'),
                                                    self.edit_sex
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['born in'], color='grey', size=11,
                                                            font_family='PPM'),
                                                    self.edit_date
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['born at'], color='grey', size=11,
                                                            font_family='PPM'),
                                                    self.edit_lieu
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['father'], color='grey', size=11,
                                                            font_family='PPM'),
                                                    self.edit_pere
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['mother'], color='grey', size=11,
                                                            font_family='PPM'),
                                                    self.edit_mere
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['contact'], color='grey', size=11,
                                                            font_family='PPM'),
                                                    self.edit_contact
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['contact 2'], color='grey', size=11,
                                                            font_family='PPM'),
                                                    self.edit_other
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['residence'], color='grey', size=11,
                                                            font_family='PPM'),
                                                    self.edit_residence
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['registration number'], color='grey', size=11,
                                                            font_family='PPM'),
                                                    self.edit_mat
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Text('URL image', color='grey', size=11, font_family='PPM'),
                                            self.edit_image_url
                                        ], spacing=2
                                    ),
                                    ft.Container(
                                        padding=10, content=ft.Column(
                                            controls=[
                                                ft.Row([self.image_button, ]),
                                                ft.Row([MyButton(languages[self.lang]['valid'], 'check', 200,
                                                                 self.update_student)]),
                                            ]
                                        )
                                    )
                                ], spacing=10
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # Registration window ____________________________________________________________________________________________
        self.ins_class = ft.Dropdown(
            **drop_style, prefix_icon=ft.Icons.ACCOUNT_BALANCE_OUTLINED,
            on_change=self.changing_class, menu_height=200, expand=True
        )
        self.unregistered = ft.Dropdown(
            **drop_style, prefix_icon=ft.Icons.PERSON_OUTLINED, expand=True,
            on_change=self.changing_class, menu_height=200
        )
        self.ins_mat = ft.TextField(**other_style, prefix_icon=ft.Icons.CREDIT_CARD, expand=True, read_only=True)
        self.ins_check = ft.Checkbox(
            label=languages[self.lang]['repeater check'], label_style=ft.TextStyle(size=12, font_family="PPI", color='grey'),
            active_color="#f0f0f6", check_color=MAIN_COLOR
        )
        self.ins_fees = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED, expand=True,
            text_align=ft.TextAlign.RIGHT, on_blur=self.on_blur_fees
        )
        self.tranche_1 = ft.TextField(
            **cool_style, expand=True, label=languages[self.lang]['fees part 1'], input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 1'
        )
        self.tranche_2 = ft.TextField(
            **cool_style, expand=True, label=languages[self.lang]['fees part 2'], input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 2'
        )
        self.tranche_3 = ft.TextField(
            **cool_style, expand=True, label=languages[self.lang]['fees part 3'], input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 3'
        )
        self.switch = ft.Switch(
            active_color=FOURTH_COLOR, thumb_color=MAIN_COLOR, track_outline_color="black",
            scale=0.7, on_change=self.changing_pay_off_state
        )

        self.ct_registration = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=530, height=650, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(
                                bottom=ft.BorderSide(1, CT_BORDER_COLOR)
                            ),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.ADD_HOME, size=24, color="black"),
                                            ft.Text(languages[self.lang]['registration'], size=16, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                                  on_click=self.close_ct_registrations),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(
                                top=ft.BorderSide(1, CT_BORDER_COLOR)
                            ),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['name'], size=11, color='grey', font_family='PPM'),
                                            self.unregistered
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['class'], size=11, color='grey',
                                                    font_family='PPM'),
                                            self.ins_class
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['registration number'], size=11, color='grey',
                                                    font_family='PPM'),
                                            self.ins_mat
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['fees'], size=11, color='grey', font_family='PPM'),
                                            self.ins_fees
                                        ], spacing=2
                                    ),
                                    self.ins_check,
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['school fees'].upper(), size=13,
                                                            font_family="PPB"),
                                                    ft.Divider(height=1, thickness=1),
                                                ], spacing=0
                                            ),
                                            ft.Row([ft.Text(languages[self.lang]['pay off'], size=12,
                                                            font_family="PPM"), self.switch]),
                                            ft.Row([self.tranche_1, self.tranche_2, self.tranche_3,]),
                                            MyButton(
                                                'Valider', 'check', 150, self.add_registration
                                            ),
                                        ]
                                    ),

                                ], spacing=10, expand=True
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # School fees window ________________________________________________
        self.sc_name = ft.Text(size=24, font_family='PPM')
        self.sc_surname = ft.Text(size=16, font_family='PPM', color='black54')
        self.sc_student_id = ft.Text(size=11, font_family='PPI', color='grey', visible=False)
        self.sc_class = ft.Text(size=13, font_family="PPB")
        self.sc_payment_table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CALENDAR_MONTH, color='grey', size=18),
                            ft.Text("Date")
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.REPARTITION_OUTLINED, color='grey', size=18),
                            ft.Text(languages[self.lang]['fees part'])
                        ]
                    )
                ),ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.MONETIZATION_ON_OUTLINED, color='grey', size=18),
                            ft.Text(languages[self.lang]['amount'])
                        ]
                    )
                ),

            ]
        )
        self.sc_amount_paid = ft.Text(size=24, font_family="PPM")
        self.sc_amount_expected = ft.Text(size=24, font_family="PPM")
        self.sc_amount_due = ft.Text(size=24, font_family="PPM")

        self.status = ft.Text(size=11, font_family="PPM")
        self.status_icon = ft.Icon(size=12)
        self.status_container = ft.Container(
            alignment=ft.alignment.center, padding=5, border_radius=8,
            content=ft.Row([self.status_icon, self.status], spacing=3)
        )
        self.sc_pay_button = MyButton(languages[self.lang]['make a payment'], 'monetization_on_outlined', 200, self.make_a_payment)
        self.pay_print_button = MyButton(languages[self.lang]['print receipt'], 'print_outlined', 200, None)
        self.sc_tranche_1 = ft.TextField(
            **other_style, width=150, label=languages[self.lang]['fees part 1'], input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 1'
        )
        self.sc_tranche_2 = ft.TextField(
            **other_style, width=150, label=languages[self.lang]['fees part 2'], input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 2'
        )
        self.sc_tranche_3 = ft.TextField(
            **other_style, width=150, label=languages[self.lang]['fees part 3'], input_filter=ft.NumbersOnlyInputFilter(),
            prefix_icon=ft.Icons.MONETIZATION_ON_OUTLINED,
            text_align=ft.TextAlign.RIGHT, data='fees part 3'
        )
        self.sc_switch = ft.Switch(
            active_color=FOURTH_COLOR, thumb_color=MAIN_COLOR, track_outline_color="black",
            scale=0.7, on_change=self.changing_pay_off_state
        )
        self.payment_container = ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[self.lang]['make a payment'], size=13,
                                font_family="PPB"),
                        ft.Row(controls=[self.sc_tranche_1, self.sc_tranche_2,
                                         self.sc_tranche_3])
                    ], spacing=5
                ),
                ft.Row([self.sc_pay_button, self.pay_print_button])
            ]
        )
        self.sc_second_container = ft.Column(
            expand=True, alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[self.lang]['loading screen'], size=12, font_family='PPM'),
                        ft.ProgressRing(color=BASE_COLOR)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ]
        )
        self.school_fees_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=600, height=700, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.MONETIZATION_ON, size=28, color='black'),
                                            ft.Text(languages[self.lang]['school fees'], size=16, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                                  on_click=self.close_school_fees_window),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True, width=600,
                            content=self.sc_second_container
                        )
                    ], spacing=0
                )
            )
        )

        # Discipline window...
        self.dis_student = ft.Dropdown(
            **drop_style, prefix_icon='person_outlined', expand=True, menu_height=200,
            options=[ft.dropdown.Option(key=' ', text=languages[self.lang]['select option'])]
        )
        self.dis_sequence = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            value=self.cp.active_sequence.data, width=200, disabled=True
        )
        self.dis_type = ft.Dropdown(
            **drop_style, prefix_icon=ft.Icons.WARNING_AMBER_OUTLINED, menu_height=200,
            options=[
                ft.dropdown.Option(
                    key=choice['key'], text=choice['text']
                ) for choice in [
                    {'key': ' ', 'text': languages[self.lang]['select option']},
                    {'key': 'ban', 'text': languages[self.lang]['ban']},
                    {'key': 'detention', 'text': languages[self.lang]['detention']},
                    {'key': 'justified absence', 'text': languages[self.lang]['justified absence']},
                    {'key': 'late', 'text': languages[self.lang]['late']},
                    {'key': 'permanent ban', 'text': languages[self.lang]['permanent ban']},
                    {'key': 'reprimand', 'text': languages[self.lang]['reprimand']},
                    {'key': 'unjustified absence', 'text': languages[self.lang]['unjustified absence']},
                    {'key': 'warning', 'text': languages[self.lang]['warning']},
                ]
            ],
            expand=True
        )
        self.dis_qty = ft.TextField(
            **cool_style, width=150, prefix_icon=ft.Icons.ONETWOTHREE, text_align=ft.TextAlign.RIGHT,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.dis_comment = ft.TextField(
            **cool_style, multiline=True, min_lines=8,
            expand=True,
        )
        self.discipline_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=600, height=620, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.EMERGENCY, size=28, color='black'),
                                            ft.Text('discipline', size=16, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton('close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                                  on_click=self.close_discipline_window),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['student'], size=11, font_family='PPM', color='grey'),
                                            self.dis_student
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text('type', size=11, font_family='PPM',
                                                    color='grey'),
                                            self.dis_type
                                        ], spacing=2
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['sequence'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.dis_sequence
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[self.lang]['quantity'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.dis_qty
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[self.lang]['comment'], size=11, font_family='PPM',
                                                    color='grey'),
                                            self.dis_comment
                                        ], spacing=2
                                    ),
                                    ft.Container(
                                        padding=10, content=MyButton(
                                            languages[self.lang]['valid'], 'check_circle', 200,
                                            self.create_new_sanction
                                        )
                                    )
                                ]
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # Content _______________________________________________________________________________________
        self.content = ft.Stack(
            expand=True,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[self.lang]['loading screen'], size=12, font_family='PPM'),
                        ft.ProgressRing(color=BASE_COLOR)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ], alignment=ft.alignment.center
        )
        self.on_mount()

    async def build_main_view(self):
        self.content.controls.clear()

        for widget in [
            self.main_window, self.ct_new_student, self.ct_edit_student,
            self.ct_registration, self.school_fees_window, self.discipline_window
        ]:
            self.content.controls.append(widget)

        self.cp.page.update()

    async def build_school_fees_container(self):
        self.sc_second_container.controls.clear()
        self.sc_second_container.controls = [
            ft.Column(
                expand=True,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                [self.sc_name, self.sc_surname, self.sc_student_id], spacing=0
                            ),
                            self.status_container
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=1, thickness=1),
                    ft.Divider(color=ft.Colors.TRANSPARENT, height=1),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(languages[self.lang]["amount paid"], size=12,
                                            font_family='PPI'),
                                    self.sc_amount_paid
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(languages[self.lang]["amount expected"], size=12,
                                            font_family='PPI'),
                                    self.sc_amount_expected
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(languages[self.lang]["amount due"], size=12,
                                            font_family='PPI'),
                                    self.sc_amount_due
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(color=ft.Colors.TRANSPARENT, height=1),
                    ft.Divider(height=1, thickness=1),
                    ft.Divider(color=ft.Colors.TRANSPARENT, height=1),
                    ft.Text(languages[self.lang]['payment history'], size=13,
                            font_family='PPB'),
                    ft.ListView(expand=True, height=200,
                                controls=[self.sc_payment_table]),
                    ft.Divider(height=1, thickness=1),
                    ft.Divider(color=ft.Colors.TRANSPARENT, height=1),
                ]
            ),
            self.payment_container
        ]
        self.sc_second_container.alignment = ft.MainAxisAlignment.CENTER
        self.sc_second_container.horizontal_alignment = None
        self.cp.page.update()

    def hide_one_window(self, window_to_hide: object):
        """
        This function helps to make menus clickable
        :param window_to_hide:
        :return:
        """
        window_to_hide.scale = 0

        self.cp.left_menu.disabled = False
        self.cp.top_menu.disabled = False
        self.main_window.disabled = False
        self.cp.left_menu.opacity = 1
        self.cp.top_menu.opacity = 1
        self.main_window.opacity = 1
        self.cp.page.update()

    def show_one_window(self, window_to_show):
        """
        This function helps to make menus non-clickable
        :param window_to_show:
        :return:
        """
        window_to_show.scale = 1

        self.cp.left_menu.disabled = True
        self.cp.top_menu.disabled = True
        self.main_window.disabled = True
        self.cp.left_menu.opacity = 0.1
        self.cp.top_menu.opacity = 0.1
        self.main_window.opacity = 0.1
        self.cp.page.update()

    @staticmethod
    def run_async_in_thread(coro):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        thread = threading.Thread(target=runner)
        thread.start()

    async def on_init_async(self):
        await self.load_datas()
        await self.load_unregistered_students()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_datas(self):
        active_classes = await get_active_classes(self.cp.page.client_storage.get("access_token"))

        self.table.rows.clear()
        boys, girls, completed_profiles = 0, 0, 0
        details = await get_students_with_details(self.cp.page.client_storage.get("access_token"))

        for i, detail in enumerate(details):
            if detail['image_url']:
                color = 'teal'
                bgcolor = 'teal50'
                status = languages[self.lang]['complete']
                icone = 'check_circle'
                completed_profiles += 1
            else:
                color = 'red'
                bgcolor = 'red50'
                status = languages[self.lang]['incomplete']
                icone = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED

            if detail['gender'] == 'M':
                boys += 1
            else:
                girls += 1

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.CircleAvatar(radius=15, foreground_image_src=detail['image_url']),
                                    ft.Text(f"{detail['name']} {detail['surname']}".upper())
                                ]
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=bgcolor, padding=5, border_radius=10, width=100,
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(icone, size=16, color=color),
                                        ft.Text(status, size=11, font_family='PPM', color=color)
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=2
                                )
                            )
                        ),
                        ft.DataCell(ft.Text(detail['class_code'])),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    MyMiniIcon('edit_outlined', '', 'grey', detail, self.open_edit_window),
                                    ft.PopupMenuButton(
                                        bgcolor='white',
                                        content=ft.Icon(ft.Icons.FORMAT_LIST_BULLETED_SHARP, size=18, color='grey'),
                                        items=[
                                            ft.PopupMenuItem(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Icon(ft.Icons.ATTACH_MONEY, size=18, color='black54'),
                                                        ft.Text(languages[self.lang]['school fees'], size=13,
                                                                font_family='PPM')
                                                    ]
                                                ), on_click=self.open_school_fees_window, data=detail
                                            ),
                                            ft.PopupMenuItem(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Icon(ft.Icons.DANGEROUS_OUTLINED, size=18, color='black54'),
                                                        ft.Text(languages[self.lang]['alert'], size=13,
                                                                font_family='PPM')
                                                    ]
                                                ), on_click=None
                                            ),
                                            ft.PopupMenuItem(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Icon(ft.Icons.PRINT_OUTLINED, size=18, color='black54'),
                                                        ft.Text(languages[self.lang]['print receipt'], size=13,
                                                                font_family='PPM'),
                                                        ft.IconButton(
                                                            ft.Icons.ATTACH_FILE, icon_size=18, icon_color='black87',
                                                            url=detail['receipt_url'],
                                                            visible=True if detail['receipt_url'] else False
                                                        )
                                                    ]
                                                ), on_click=None
                                            )
                                        ]
                                    )
                                ], spacing=0
                            )
                        )
                    ],
                ),
            )

        await self.build_main_view()
        self.boys.value = boys
        self.girls.value = girls
        self.registered_count.value = len(details)
        self.completed_rate.value = f"{completed_profiles * 100 / len(details):.0f} %"
        self.pb_rate.value = completed_profiles / len(details)
        self.cp.page.update()

    async def filter_datas(self, e):
        details = await get_students_with_details(self.cp.page.client_storage.get("access_token"))
        search = self.search.value.lower() if self.search else ''

        filtered_datas = list(filter(lambda x: search in x['name'].lower() or search in x['surname'].lower(), details))
        print(len(filtered_datas))
        self.table.rows.clear()

        for i, detail in enumerate(filtered_datas):
            if detail['image_url']:
                color = 'teal'
                bgcolor = 'teal50'
                status = languages[self.lang]['complete']
                icone = 'check_circle'
            else:
                color = 'red'
                bgcolor = 'red50'
                status = languages[self.lang]['incomplete']
                icone = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.CircleAvatar(radius=15, foreground_image_src=detail['image_url']),
                                    ft.Text(f"{detail['name']} {detail['surname']}".upper())
                                ]
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=bgcolor, padding=5, border_radius=10, width=100,
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(icone, size=16, color=color),
                                        ft.Text(status, size=11, font_family='PPM', color=color)
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=2
                                )
                            )
                        ),
                        ft.DataCell(ft.Text(detail['class_code'])),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    MyMiniIcon('edit_outlined', '', 'grey', detail, self.open_edit_window),
                                    ft.PopupMenuButton(
                                        bgcolor='white',
                                        content=ft.Icon(ft.Icons.FORMAT_LIST_BULLETED_SHARP, size=18, color='grey'),
                                        items=[
                                            ft.PopupMenuItem(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Icon(ft.Icons.ATTACH_MONEY, size=18, color='black54'),
                                                        ft.Text(languages[self.lang]['school fees'], size=13,
                                                                font_family='PPM')
                                                    ]
                                                ), on_click=self.open_school_fees_window, data=detail
                                            ),
                                            ft.PopupMenuItem(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Icon(ft.Icons.DANGEROUS_OUTLINED, size=18, color='black54'),
                                                        ft.Text(languages[self.lang]['alert'], size=13,
                                                                font_family='PPM')
                                                    ]
                                                ), on_click=None
                                            ),
                                            ft.PopupMenuItem(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Icon(ft.Icons.PRINT_OUTLINED, size=18, color='black54'),
                                                        ft.Text(languages[self.lang]['print receipt'], size=13,
                                                                font_family='PPM'),
                                                        ft.IconButton(
                                                            ft.Icons.ATTACH_FILE, icon_size=18, icon_color='black87',
                                                            url=detail['receipt_url'],
                                                            visible=True if detail['receipt_url'] else False
                                                        )
                                                    ]
                                                ), on_click=None
                                            )
                                        ]
                                    )
                                ], spacing=0
                            )
                        )
                    ],
                ),
            )

        self.table.update()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    def open_new_student_container(self, e):
        role = self.cp.page.client_storage.get('role')
        if role in ['secrétaire', 'économe']:
            self.show_one_window(self.ct_new_student)
        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()

    def close_new_student_container(self, e):
        self.hide_one_window(self.ct_new_student)

    def open_ct_registrations(self, e):
        role = self.cp.page.client_storage.get('role')
        if role in ['secrétaire', 'économe']:
            self.show_one_window(self.ct_registration)
        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()

    def close_ct_registrations(self, e):
        self.hide_one_window(self.ct_registration)

    async def load_unregistered_students(self):
        access_token = self.cp.page.client_storage.get("access_token")

        students = await get_unregistered_students(access_token)

        for student in students:
            self.unregistered.options.append(
                ft.dropdown.Option(
                    key=student['id'], text=f"{student['name']} {student['surname']}".upper()
                )
            )

        self.unregistered.update()

        classes = await get_all_classes_basic_info(access_token)
        self.ins_class.options.clear()

        for one_class in classes:
            self.ins_class.options.append(
                ft.dropdown.Option(
                    key=one_class['id'], text=f"{one_class['code']}"
                )
            )

        self.ins_class.update()

    def add_eleve(self, e):
        counter = 0
        for widget in (
            self.new_nom, self.new_prenom, self.new_sex, self.new_lieu, self.new_pere, self.new_mere,
            self.new_date.year, self.new_date.month, self.new_date.day,
            self.new_contact, self.new_date.day, self.new_date.month, self.new_date.year
        ):
            if widget.value is None or widget.value == "":
                counter += 1

        if counter == 0:
            try:
                supabase_client.table('students').insert(
                    {
                        'name': self.new_nom.value, 'surname': self.new_prenom.value, 'gender': self.new_sex.value,
                        'birth_place': self.new_lieu.value,
                        'birth_date': f"{int(self.new_date.day.value)}/{int(self.new_date.month.value)}/{int(self.new_date.year.value)}",
                        'father': self.new_pere.value, 'mother': self.new_mere.value, 'contact': self.new_contact.value,
                        'other_contact': self.new_other.value, 'city': self.new_residence.value
                    }
                ).execute()

                for widget in (
                    self.new_nom, self.new_prenom, self.new_sex, self.new_lieu, self.new_pere, self.new_mere,
                    self.new_date.year, self.new_date.month, self.new_date.day, self.new_other, self.new_residence,
                    self.new_contact, self.new_date.day, self.new_date.month, self.new_date.year
                ):
                    widget.value = None
                    widget.update()

                # Mise à jour de données
                self.run_async_in_thread(self.load_unregistered_students())

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.box.content.value = languages[self.lang]['student added']
                self.cp.box.open = True
                self.cp.box.update()

                self.registered_count.update()
                self.completed_rate.update()
                self.search.update()

            except Exception as e:
                self.cp.box.title.value = languages[self.lang]['error']
                # print(str(e))
                # print(type(e))
                # self.cp.box.content.value = f"{e}"
                self.cp.box.open = True
                self.cp.box.update()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error msg']
            self.cp.box.open = True
            self.cp.box.update()

    def close_ct_edit_student(self, e):
        self.hide_one_window(self.ct_edit_student)

    def open_edit_window(self, e):
        self.edit_id_student = e.control.data['student_id']

        resp = supabase_client.table("students").select('*').eq('id', e.control.data['student_id']).single().execute()

        self.edit_nom.value = resp.data['name']
        self.edit_prenom.value = resp.data['surname']
        self.edit_sex.value = resp.data['gender']
        self.edit_lieu.value = resp.data['birth_place']
        self.edit_date.value = resp.data['birth_date']
        self.edit_pere.value = resp.data['father']
        self.edit_mere.value = resp.data['mother']
        self.edit_contact.value = resp.data['contact']
        self.edit_other.value = resp.data['other_contact']
        self.edit_residence.value = resp.data['city']
        self.edit_mat.value = resp.data['registration_number']
        self.edit_image_url.value = resp.data['image_url']
        self.image_preview.foreground_image_src = e.control.data['image_url'] if e.control.data['image_url'] is not None else DEFAULT_IMAGE_URL

        for widget in (
            self.edit_nom, self.edit_prenom, self.edit_sex, self.edit_lieu, self.edit_date,
            self.edit_pere, self.edit_mere, self.edit_contact, self.edit_other, self.edit_residence,
            self.edit_mat, self.edit_image_url, self.image_preview
        ):
            widget.update()

        self.show_one_window( self.ct_edit_student)

    def set_image_url(self, e):
        if e.files:
            file_path = e.files[0].path
            file_name = os.path.basename(file_path)

            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = "application/octet-stream"

            with open(file_path, "rb") as f:
                data = f.read()

            # Upload to Supabase
            try:
                storage_path = f"{self.edit_id_student}{file_name}"
                supabase_client.storage.from_(BUCKET_STUDENTS_PICTURES).upload(
                    path=storage_path,
                    file=data,
                    file_options={"content-type": mime_type}
                )

                signed_url_response = supabase_client.storage.from_(BUCKET_STUDENTS_PICTURES).create_signed_url(storage_path, 60 * 60 * 24 * 365)
                image_url = signed_url_response['signedURL']

                self.edit_image_url.value = image_url
                self.image_preview.background_image_src = image_url
                self.edit_image_url.update()
                self.image_preview.update()

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.box.content.value = languages[self.lang]['import image success']
                self.cp.box.open = True
                self.cp.box.update()

            except Exception as e:
                self.cp.box.title.value = languages[self.lang]['error']
                print(f"{e}")
                self.cp.box.content.value = ''
                self.cp.box.open = True
                self.cp.box.update()

    def update_student(self, e):
        role = self.cp.page.client_storage.get('role')

        if role in ['secrétaire' or 'économe']:
            try:
                supabase_client.table('students').update(
                    {
                        'name': self.edit_nom.value, 'surname': self.edit_prenom.value, 'gender': self.edit_sex.value,
                        'birth_place': self.edit_lieu.value, 'birth_date': self.edit_date.value,
                        'father': self.edit_pere.value, 'mother': self.edit_mere.value, 'contact': self.edit_contact.value,
                        'other_contact': self.edit_other.value, 'city': self.edit_residence.value,
                        'registration_number': self.edit_mat.value, 'image_url': self.edit_image_url.value,
                    }
                ).eq('id', self.edit_id_student).execute()

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.box.content.value = languages[self.lang]['student updated']
                self.cp.box.open = True
                self.cp.box.update()

                self.on_mount()

                self.hide_one_window(self.ct_edit_student)

            except Exception as e:
                self.cp.box.title.value = languages[self.lang]['error']
                print(f"{e}")
                self.cp.box.content.value = f""
                self.cp.box.open = True
                self.cp.box.update()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()

    async def set_registration_number(self, e):
        self.ins_mat.value = get_new_registration_number() if self.ins_mat.value in ['', None] else self.ins_mat.value
        self.ins_mat.update()

    def on_blur_fees(self, e):
        global selected_fees
        selected_fees = self.ins_fees.value

    def changing_class(self, e):
        self.run_async_in_thread(self.set_registration_number(e))

    async def solder_pension(self, e):
        if self.switch.value:
            access_token = self.cp.page.client_storage.get("access_token")
            year_id = self.cp.year_id

            fees = await get_fees_amount_by_year(access_token, year_id)

            self.tranche_1.value = fees['fees_part_1']
            self.tranche_2.value = fees['fees_part_2']
            self.tranche_3.value = fees['fees_part_3']
            self.cp.page.update()
        else:
            self.tranche_3.value = None
            self.tranche_2.value = None
            self.tranche_1.value = None
            self.cp.page.update()

    def changing_pay_off_state(self, e):
        self.run_async_in_thread(self.solder_pension(e))

    @staticmethod
    def create_pdf_fonts():
        pdfmetrics.registerFont(TTFont('clb', "assets/fonts/calibrib.ttf"))
        pdfmetrics.registerFont(TTFont('cli', "assets/fonts/calibrii.ttf"))
        pdfmetrics.registerFont(TTFont('cal', "assets/fonts/calibri.ttf"))

    async def generate_receipt_pdf(self) -> str:
        global selected_fees
        selected_student, selected_student_id, selected_class = '', '', ''
        registration_date = datetime.datetime.now().strftime("%d/%m/%Y")
        access_token = self.cp.page.client_storage.get('access_token')

        selected_student = get_student_name_by_id(self.unregistered.value)
        selected_student_id = self.unregistered.value
        selected_class = await get_class_code_by_id_async(self.ins_class.value, access_token)

        print("-------generer reçu__________")
        print(selected_student, selected_student_id, selected_class, selected_fees)

        # QR Code
        qr_data = (
            f"ID élève"
            f"\nAnnée scolaire: {self.current_year_label.value}"
            f"\nID élève: {self.unregistered.value}"
            f"\nNom: {selected_student}"
            f"\nClasse: {selected_class}"
            f"\nMatricule: {self.ins_mat.value}"
            f"\nPar: {self.cp.user_name.value}"
            f"\nLe {registration_date}"
        )
        qr_img = qrcode.make(qr_data)
        qr_img_pil = qr_img.convert("RGB")
        qr_reader = ImageReader(qr_img_pil)

        self.create_pdf_fonts()

        # PDF config
        buffer = io.BytesIO()
        page_width = 7.2 * cm
        page_height = 29.7 * cm
        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
        c.translate(0.5 * cm, 0)  # Juste une petite marge à gauche

        y = page_height - 1 * cm  # Commence en haut

        def write_centered_line(text, font_size=8, bold=False, space=0.5 * cm, police='cal'):
            nonlocal y
            font = 'cal' if bold else police
            c.setFont(font, font_size)
            c.drawCentredString((page_width - 1 * cm) / 2, y, text)
            y -= space

        # Entête
        write_centered_line("Reçu / Receipt", police='clb', font_size=12, bold=False, space=1 * cm)
        write_centered_line(school_republic_fr, font_size=9, bold=False)
        write_centered_line(national_devise_fr, font_size=9, bold=False)
        write_centered_line(school_delegation_fr, font_size=9, bold=False)
        write_centered_line(school_name_fr, font_size=9, bold=False)
        write_centered_line("", space=0.7 * cm)

        # Infos élève
        write_centered_line(f"Année scolaire : {self.current_year_label.value}")
        write_centered_line(f"Nom : {selected_student}")
        write_centered_line(f"Classe : {selected_class}")
        write_centered_line(f"Frais d'inscription : {selected_fees} FCFA")
        write_centered_line(f"Date d'inscription : {registration_date}")
        write_centered_line("", space=1 * cm)

        # QR Code
        c.drawImage(qr_reader, x=2.1 * cm, y=y - 3 * cm, width=3 * cm, height=3 * cm)
        y -= 3.5 * cm

        # Signature
        write_centered_line("", space=1 * cm)
        write_centered_line("Signature de la Direction")
        write_centered_line("_________________________")

        # Enregistrement
        c.save()
        buffer.seek(0)

        # Upload Supabase
        file_path = f"fiche_{self.unregistered.value}_{uuid.uuid4().hex[:6]}.pdf"

        supabase_client.storage.from_(BUCKET_REGISTRATIONS).upload(
            path=file_path,
            file=buffer.getvalue(),
            file_options={"content-type": "application/pdf"}
        )

        signed_url_response = supabase_client.storage.from_(BUCKET_REGISTRATIONS).create_signed_url(
            file_path, 3600 * 24 * 365
        )
        signed_url = signed_url_response.get("signedURL")
        return signed_url

    async def valider_inscription(self, e):
        if self.ins_class.value:

            # update registration number...
            # try:
            supabase_client.table('students').update(
                {'registration_number': self.ins_mat.value}).eq('id', self.unregistered.value).execute()

            my_url = await self.generate_receipt_pdf()

            # Add a registration...
            repeater = True if self.ins_check.value else False
            supabase_client.table('registrations').insert(
                {'year_id': self.current_year.value, 'student_id': self.unregistered.value,
                 'class_id': self.ins_class.value, 'receipt_url': my_url,
                 'repeater': repeater, "amount": int(self.ins_fees.value)}
            ).execute()

            self.cp.page.launch_url(my_url)

            # inscription dans la table school_fees...
            supabase_client.table('school_fees').insert(
                {
                    'year_id': self.current_year.value, 'student_id': self.unregistered.value,
                    "part": "registration", "amount": int(self.ins_fees.value)
                }
            ).execute()

            # add school fees
            for tranche in (self.tranche_1, self.tranche_2, self.tranche_3):
                if tranche.value is None or tranche.value == "":
                    pass
                else:
                    amount_part = int(tranche.value)
                    supabase_client.table('school_fees').insert(
                        {
                            'year_id': self.current_year.value, 'student_id': self.unregistered.value,
                            'part': tranche.data, 'amount': amount_part,
                        }
                    ).execute()

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.box.content.value = languages[self.lang]['student registered']
            self.cp.box.open = True
            self.cp.box.update()

            # empty fields...
            for widget in (
                    self.ins_fees, self.ins_mat, self.ins_check, self.switch,
                    self.tranche_1, self.tranche_2, self.tranche_3, self.unregistered
            ):
                widget.value = None
                widget.update()

            self.on_mount()
            self.cp.page.update()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error msg']
            self.cp.box.open = True
            self.cp.box.update()

    def add_registration(self, e):
        self.run_async_in_thread(self.valider_inscription(e))

    async def load_fees_widgets(self, e):
        self.show_one_window(self.school_fees_window)
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        all_fees_part = await get_fees_amount_by_year(access_token, year_id)
        total_to_pay = all_fees_part['fees_part_1'] + all_fees_part['fees_part_2'] + all_fees_part['fees_part_3'] + all_fees_part['registration']


        total_payments = await get_student_payments_for_active_year(
            access_token, e.control.data['student_id'], year_id
        )
        total_paid = sum(item['amount'] for item in total_payments)

        total_due = total_to_pay - total_paid
        self.sc_student_id.value = e.control.data['student_id']

        if total_due > 0:
            self.sc_amount_due.color = 'red'
            self.status_icon.name = ft.Icons.INDETERMINATE_CHECK_BOX
            self.status_icon.color = 'red'
            self.status.value = languages[self.lang]['on going']
            self.status.color = 'red'
            self.status_container.bgcolor = 'red50'
            self.status_container.border = ft.border.all(1, 'red')
            self.payment_container.visible = True

        else:
            self.sc_amount_due.color = 'green'
            self.status_icon.name = ft.Icons.CHECK_CIRCLE
            self.status_icon.color = 'green'
            self.status.value = languages[self.lang]['sold out']
            self.status.color = 'green'
            self.status_container.bgcolor = 'green50'
            self.status_container.border = ft.border.all(1, 'green')
            self.payment_container.visible = False

        if total_paid < total_due:
            self.sc_amount_paid.color = 'grey'
        else:
            self.sc_amount_paid.color = 'green'

        self.sc_amount_paid.value = format_number(total_paid)
        self.sc_amount_due.value = format_number(total_due)
        self.sc_amount_expected.value =  format_number(total_to_pay)
        self.sc_name.value = e.control.data['name']
        self.sc_surname.value = e.control.data['surname']

        self.sc_payment_table.rows.clear()
        for payment in total_payments:
            self.sc_payment_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(payment['date'])[0:10])),
                        ft.DataCell(ft.Text(payment['part'])),
                        ft.DataCell(ft.Text(add_separator(payment['amount'])))
                    ]
                )
            )

        await self.build_school_fees_container()

    def open_school_fees_window(self, e):
        self.run_async_in_thread(self.load_fees_widgets(e))

    def close_school_fees_window(self, e):
        self.hide_one_window(self.school_fees_window)
        self.sc_second_container.controls.clear()
        self.sc_second_container.controls = [
            ft.Column(
                controls=[
                    ft.Text(languages[self.lang]['loading screen'], size=12, font_family='PPM'),
                    ft.ProgressRing(color=BASE_COLOR)
                ], alignment = ft.MainAxisAlignment.CENTER,
                horizontal_alignment = ft.CrossAxisAlignment.CENTER

            )
        ]
        self.sc_second_container.alignment = ft.MainAxisAlignment.CENTER
        self.sc_second_container.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.cp.page.update()

    def make_a_payment(self, e):
        role = self.cp.page.client_storage.get('role')

        if role in ['secrétaire', 'économe']:

            for tranche in (self.sc_tranche_1, self.sc_tranche_2, self.sc_tranche_3):
                if tranche.value is None or tranche.value == "":
                    pass
                else:
                    amount_part = int(tranche.value)
                    supabase_client.table('school_fees').insert(
                        {
                            'year_id': self.current_year.value, 'student_id': self.sc_student_id.value,
                            'part': tranche.label, 'amount': amount_part,
                        }
                    ).execute()

            # update view
            # empty fields...
            for widget in (
                    self.ins_fees, self.ins_mat, self.ins_check, self.switch,
                    self.sc_tranche_1, self.sc_tranche_2, self.sc_tranche_3,
            ):
                widget.value = None
                widget.update()

            total_paid = get_amount_paid_by_student_id(self.sc_student_id.value)
            total_expected = total_school_fees()
            total_due = total_expected - total_paid
            self.sc_student_id.value = self.sc_student_id.value

            if total_due > 0:
                self.sc_amount_due.color = 'red'
                self.status_icon.name = ft.Icons.INDETERMINATE_CHECK_BOX
                self.status_icon.color = 'red'
                self.status.value = languages[self.lang]['on going']
                self.status.color = 'red'
                self.status_container.bgcolor = 'red50'
                self.status_container.border = ft.border.all(1, 'red')
                self.payment_container.visible = True
            else:
                self.sc_amount_due.color = 'green'
                self.status_icon.name = ft.Icons.CHECK_CIRCLE
                self.status_icon.color = 'green'
                self.status.value = languages[self.lang]['sold out']
                self.status.color = 'green'
                self.status_container.bgcolor = 'green50'
                self.status_container.border = ft.border.all(1, 'green')
                self.payment_container.visible = False

            if total_paid < total_due:
                self.sc_amount_paid.color = 'grey'
            else:
                self.sc_amount_paid.color = 'green'

            self.sc_amount_paid.value = format_number(total_paid)
            self.sc_amount_due.value = format_number(total_due)
            self.sc_amount_expected.value = format_number(total_expected)
            # self.sc_name.value = e.control.data['name']
            # self.sc_surname.value = e.control.data['surname']

            self.sc_payment_table.rows.clear()
            for payment in get_all_payments_by_student(self.sc_student_id.value):
                self.sc_payment_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(payment['date'])[0:10])),
                            ft.DataCell(ft.Text(payment['part'])),
                            ft.DataCell(ft.Text(add_separator(payment['amount'])))
                        ]
                    )
                )
            self.sc_payment_table.update()
            self.cp.page.update()

            # Generate pdf file

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()

    def open_discipline_window(self, e):
        self.run_async_in_thread(self.load_discipline_data(e))

    async def load_discipline_data(self, e):
        year_id = self.cp.year_id
        print(year_id)
        access_token = self.cp.page.client_storage.get('access_token')
        students = await get_registered_students(access_token, year_id)

        for item in students:
            self.dis_student.options.append(
                ft.dropdown.Option(
                    key=item['id'],
                    text=f"{item['name']} {item['surname']}".upper()
                )
            )

        role = self.cp.page.client_storage.get('role')

        if role in ['secrétaire', "économe"]:
            self.show_one_window(self.discipline_window)

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()

    def close_discipline_window(self, e):
        self.hide_one_window(self.discipline_window)

        self.dis_student.options.clear()
        self.dis_student.options.append(
            ft.dropdown.Option(
                key=' ',
                text=languages[self.lang]['select option']
            )
        )
        self.dis_student.value = ' '
        self.dis_type.value = ' '
        self.cp.page.update()

    async def create_new_discipline_entry(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        count = 0
        for widget in (self.dis_student, self.dis_type, self.dis_qty):
            if widget.value is None or widget.value == " ":
                count += 1

        if count > 0:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error msg']
            self.cp.box.open = True
            self.cp.box.update()

        else:
            datas = {
                'year_id': self.cp.year_id,
                'student_id': self.dis_student.value,
                'sequence': self.dis_sequence.value,
                'type': self.dis_type.value,
                'quantity': int(self.dis_qty.value),
                "comment": self.dis_comment.value
            }
            await insert_discipline_entry(access_token, datas)

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.box.content.value = languages[self.lang]['sanction saved']
            self.cp.box.open = True
            self.cp.box.update()

    def create_new_sanction(self, e):
        self.run_async_in_thread(self.create_new_discipline_entry(e))









