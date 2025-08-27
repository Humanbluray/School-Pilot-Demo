from components import MyButton, MyIconButton, MyMiniIcon, ColoredIcon, ColoredButton, BoxStudentNote
from utils.styles import *
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading, openpyxl, uuid
import pandas as pd
from io import BytesIO
from services.async_functions.notes_functions import *
from utils.useful_functions import add_separator

DOCUMENTS_BUCKET = 'documents'
page_number: int = 1


class Notes(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center
        )
        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # main window _______________________________________________________
        self.search_class = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.ROOFING, expand=True, menu_height=200,
            on_change=self.on_filter_class_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' ',
        )
        self.search_subject = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.BOOK_OUTLINED, expand=True, menu_height=200,
            on_change=None, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.search_sequence = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.BOOK_OUTLINED, expand=True, menu_height=200,
            options=[
                ft.dropdown.Option(
                    key='sequence 1', text=f"{languages[lang]['sequence 1']}"
                ),
                ft.dropdown.Option(
                    key='sequence 2', text=f"{languages[lang]['sequence 2']}"
                ),ft.dropdown.Option(
                    key='sequence 3', text=f"{languages[lang]['sequence 3']}"
                ),ft.dropdown.Option(
                    key='sequence 4', text=f"{languages[lang]['sequence 4']}"
                ),
                ft.dropdown.Option(
                    key='sequence 5', text=f"{languages[lang]['sequence 5']}"
                ),ft.dropdown.Option(
                    key='sequence 6', text=f"{languages[lang]['sequence 6']}"
                ),
                ft.dropdown.Option(
                    key=' ', text=f"{languages[lang]['select option']}"
                )
            ], value=' '
        )
        self.table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[lang]['class'], languages[lang]['name'], languages[lang]['sequence'],
                    languages[lang]['subject'], languages[lang]['note'], 'actions'
                ]
            ]
        )
        self.nb_result_search = ft.Text(size=12, font_family="PPI", color='grey')
        self.page_number = ft.Text(f"{page_number}", size=12, font_family='PPM')
        self.back_bt = ft.IconButton(
            ft.Icons.ARROW_CIRCLE_LEFT_OUTLINED, icon_size=20, icon_color="black", bgcolor="#f0f0f6",
            on_click=self.click_back
        )
        self.forward_bt = ft.IconButton(
            ft.Icons.ARROW_CIRCLE_RIGHT_OUTLINED, icon_size=20, icon_color="black", bgcolor="#f0f0f6",
            on_click=self.click_forward
        )

        self.main_window = ft.Container(
            expand=True, content=ft.Column(
                controls=[
                    ft.Text('Notes'.capitalize(), size=16, font_family='PPB'),
                    ft.Container(
                        bgcolor="white", padding=0, expand=True, border_radius=16,
                        content=ft.Column(
                            controls=[
                                ft.Container(
                                    padding=20, border=ft.border.only(bottom=ft.BorderSide(1, "#f0f0f6")),
                                    content=ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ColoredButton(
                                                        languages[lang]['add notes'], ft.Icons.NOTE_ADD, self.open_new_note_window
                                                    ),
                                                    ColoredButton(
                                                        languages[lang]['import notes'], ft.Icons.UPLOAD_FILE_OUTLINED,
                                                        self.open_import_window
                                                    ),
                                                    ColoredButton(
                                                        languages[lang]['export template'],
                                                        ft.Icons.FILE_DOWNLOAD_DONE_OUTLINED, self.open_export_xls_window
                                                    ),
                                                    ColoredButton(
                                                        languages[lang]['pdf format'],
                                                        ft.Icons.PICTURE_AS_PDF_SHARP,
                                                        None
                                                    ),
                                                    ColoredButton(
                                                        languages[lang]['xls format'],
                                                        ft.Icons.FILE_PRESENT,
                                                        None
                                                    )
                                                ]
                                            ),
                                            ft.Row(
                                                controls=[
                                                    ColoredButton(
                                                        languages[lang]['filter'], ft.Icons.FILTER_ALT_OUTLINED,
                                                        self.open_filter_window
                                                    ),
                                                    ColoredButton(
                                                        languages[lang]['stats by class'],
                                                        ft.Icons.AREA_CHART,
                                                        self.open_statistics_window
                                                    ),
                                                    MyMiniIcon(
                                                        ft.Icons.FILTER_ALT_OFF_OUTLINED, languages[lang]['delete filter'],
                                                        'black', None, self.supp_filters
                                                    )
                                                ]
                                            )
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    )
                                ),
                                ft.Divider(color=ft.Colors.TRANSPARENT),
                                ft.ListView(expand=True, controls=[self.table]),
                                ft.Container(
                                    padding=10,
                                    content=ft.Row(
                                        controls=[
                                            self.nb_result_search,
                                            ft.Row([self.back_bt, self.page_number, self.forward_bt])
                                        ], alignment=ft.MainAxisAlignment.END
                                    )
                                ),
                            ]
                        )
                    )
                ]
            )
        )

        self.filter_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=500, height=430,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['filter window'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_filter_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True, width=450,
                            content=ft.Column(
                                expand=True,
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['sequence'], size=11, font_family='PPM', color='grey'),
                                            self.search_sequence,
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['class'], size=11, font_family='PPM',
                                                    color='grey'),
                                            self.search_class,
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['subject'], size=11, font_family='PPM',
                                                    color='grey'),
                                            self.search_subject,
                                        ], spacing=2
                                    ),
                                    ft.Container(
                                        padding=10, content=MyButton(
                                            languages[lang]['valid'], 'check_circle',
                                            200, self.valid_filters
                                        )
                                    )
                                ], spacing=10,
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # new note window...
        self.new_class = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.ROOFING, width=200,
            on_change=self.on_new_class_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.new_subject = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.BOOK_OUTLINED, width=400,
            on_change=self.on_new_subject_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.new_sequence = ft.TextField(
            **cool_style, value=f"{languages[lang][self.cp.active_sequence.data]}", data=self.cp.active_sequence.data,
            prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED, width=170, read_only=True
        )
        self.new_table = ft.ListView(
            expand=True, divider_thickness=1, spacing=10
        )
        self.nb_students = ft.Text(size=13, font_family='PPB', visible=True)
        self.new_progress_bar = ft.ProgressBar(
            width=100, height=7, color=BASE_COLOR, bgcolor=SECOND_COLOR, border_radius=16,
            value=0
        )
        self.new_coefficient = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.ONETWOTHREE, width=80, read_only=True
        )
        self.no_data = ft.Text(
            size=13, font_family='PPB', color='red', value=languages[lang]['no data'],
            visible=False
        )
        self.new_note_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=550, height=750,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['add notes'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_new_note_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True,
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['class'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_class
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['sequence'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_sequence
                                                ], spacing=2
                                            )
                                        ]
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['subject'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_subject
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['coefficient'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_coefficient
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['students without note'].upper(), size=13,
                                                            font_family='PPB'),
                                                    ft.Row(
                                                        controls=[
                                                            ft.Text(languages[self.lang]['total'].upper(), size=13, font_family='PPB', color='red'),
                                                            self.nb_students, self.no_data
                                                        ]
                                                    ),

                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            ),
                                            ft.Divider(height=1, thickness=1)
                                        ], spacing=0
                                    ),

                                    self.new_table,

                                    ft.Container(
                                        padding=10, content=ft.Row(
                                            controls=[
                                                MyButton(
                                                    languages[lang]['valid'], 'check_circle', 200,
                                                    self.valider_notes
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            languages[lang]['progress'], size=13, font_family='PPM',
                                                            color='grey'
                                                        ),
                                                        self.new_progress_bar
                                                    ]
                                                ),
                                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    )
                                ], spacing=10,
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # edit note window...
        self.edit_student = ft.TextField(
            **cool_style, width=400, prefix_icon='person_outlined', read_only=True
        )
        self.edit_note_id = ft.Text(visible=False)
        self.edit_subject_name = ft.TextField(
            **cool_style, width=400, prefix_icon='book_outlined', read_only=True
        )
        self.edit_sequence = ft.TextField(
            **cool_style, width=200, prefix_icon=ft.Icons.CALENDAR_MONTH, read_only=True
        )
        self.edit_note = ft.TextField(
            **cool_style, width=80,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]", replacement_string=""),
            text_align=ft.TextAlign.RIGHT,
        )

        self.edit_note_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=450, height=500,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['edit note'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_edit_note_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True,
                                controls=[
                                    self.edit_note_id,
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['name'], size=11, font_family='PPM', color='grey'),
                                            self.edit_student
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['sequence'], size=11, font_family='PPM', color='grey'),
                                            self.edit_sequence
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['subject'], size=11, font_family='PPM', color='grey'),
                                            self.edit_subject_name
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['note'], size=11, font_family='PPM', color='grey'),
                                            self.edit_note
                                        ], spacing=2
                                    ),
                                    ft.Container(
                                        padding=10, content=MyButton(
                                            languages[lang]['valid'], 'check_circle', 200,
                                            self.valider_edit_note
                                        ),
                                    )
                                ], spacing=10
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # export xls window...
        self.exp_class = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.ROOFING, width=200, menu_height=200,
            on_change=self.on_export_class_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.exp_subject = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.BOOK_OUTLINED, width=400, menu_height=200,
            on_change=self.on_export_subject_change, options=[
                ft.dropdown.Option(key=' ', text=f"{languages[lang]['select option']}")
            ], value=' '
        )
        self.exp_sequence = ft.TextField(
            **cool_style, value=f"{languages[lang][self.cp.active_sequence.data]}",
            data=self.cp.active_sequence.data,
            prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED, width=170, read_only=True
        )
        self.exp_coefficient = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.ONETWOTHREE, width=80, read_only=True
        )
        self.exp_class_name = ft.Text(visible=False)

        self.export_xls_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=550, height=350,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['export template'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_export_xls_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, spacing=10, controls=[
                                    self.exp_class_name,
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['class'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.exp_class
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['sequence'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.exp_sequence
                                                ], spacing=2
                                            )
                                        ]
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['subject'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.exp_subject
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['coefficient'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.exp_coefficient
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Container(
                                        padding=10, content=ft.Row(
                                            controls=[
                                                MyButton(
                                                    languages[lang]["valid"], 'check_circle',
                                                    200, self.exporter_template_file
                                                )
                                            ]
                                        )
                                    )
                                ]
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # import_window...
        self.imp_verif_bar = ft.ProgressBar(
            border_radius=16, height=10, value=0, color=BASE_COLOR, bgcolor='#f0f0f6', width=150
        )
        self.imp_verif_text = ft.Text('0%', size=14, font_family='PPM')
        self.imp_insert_bar = ft.ProgressBar(
            border_radius=16, height=10, value=0, color=BASE_COLOR, bgcolor='#f0f0f6', width=150
        )
        self.imp_insert_text = ft.Text('0%', size=14, font_family='PPM')

        self.total_lines_of_file = ft.Text('0', size=14, font_family='PPM')
        self.total_errors = ft.Text('0', size=14, font_family='PPM')
        self.table_errors = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(languages[lang]['line'])),
                ft.DataColumn(ft.Text(languages[lang]['error type']))
            ],
        )
        self.msg_error = ft.Text(languages[self.lang]['correct import errors'], size=14, font_family='PPB', color='red')

        self.bloc_table = ft.Column(
            visible=False, expand=True,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[lang]['errors table'].upper(), size=13,
                                font_family="PPB"),
                        ft.Divider(height=1, thickness=1)
                    ], spacing=0
                ),
                ft.ListView(expand=True, controls=[self.table_errors]),
                self.msg_error
            ]
        )
        self.bloc_import = ft.Column(
            visible=False,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[lang]['import lines'], size=13, font_family="PPB"),
                        ft.Divider(height=1, thickness=1)
                    ], spacing=0
                ),
                ft.Row(
                    controls=[
                        ft.Text(languages[lang]['import'], size=12, font_family='PPI', color='grey'),
                        ft.Row(controls=[self.imp_insert_bar, self.imp_insert_text])
                    ]
                )
            ]
        )

        self.cp.fp_import_notes.on_result = self.importer_notes

        self.import_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=700, height=750,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['import notes'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_import_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, spacing=10,
                                controls=[
                                    MyButton(
                                        languages[lang]['import notes'], ft.Icons.DOWNLOAD_DONE, None,
                                        lambda _: self.cp.fp_import_notes.pick_files(
                                            allowed_extensions=['xls', 'xlsx']),
                                    ),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['file checking'].upper(), size=13, font_family="PPB"),
                                            ft.Divider(height=1, thickness=1)
                                        ], spacing=0
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['total number of lines'], size=12,
                                                            font_family='PPI'),
                                                    self.total_lines_of_file
                                                ]
                                            ),
                                            ft.Row(controls=[self.imp_verif_bar, self.imp_verif_text]),
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text(languages[lang]['nb errors'], size=12, font_family='PPM'),
                                            self.total_errors
                                        ]
                                    ),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    self.bloc_table,
                                    ft.Divider(height=1, thickness=1),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    self.bloc_import
                                ]
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # statistics window ________________
        self.stats_class = ft.Dropdown(
            **drop_style, prefix_icon='roofing', label=languages[lang]['class'], options=[
                ft.dropdown.Option(key=' ', text=languages[lang]['select option'])
            ], value=' ', on_change=self.on_stats_class_change, expand=True, menu_height=200
        )
        self.stats_subject = ft.Dropdown(
            **drop_style, prefix_icon='book_outlined', label=languages[lang]['subject'], options=[
                ft.dropdown.Option(key=' ', text=languages[lang]['select option'])
            ], value=' ', on_change=self.on_stats_subject_change, expand=True, menu_height=200
        )
        self.stats_sequence = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.BOOK_OUTLINED, expand=True, menu_height=200,
            options=[
                ft.dropdown.Option(
                    key='sequence 1', text=f"{languages[lang]['sequence 1']}"
                ),
                ft.dropdown.Option(
                    key='sequence 2', text=f"{languages[lang]['sequence 2']}"
                ), ft.dropdown.Option(
                    key='sequence 3', text=f"{languages[lang]['sequence 3']}"
                ), ft.dropdown.Option(
                    key='sequence 4', text=f"{languages[lang]['sequence 4']}"
                ),
                ft.dropdown.Option(
                    key='sequence 5', text=f"{languages[lang]['sequence 5']}"
                ), ft.dropdown.Option(
                    key='sequence 6', text=f"{languages[lang]['sequence 6']}"
                ),
                ft.dropdown.Option(
                    key=' ', text=f"{languages[lang]['select option']}"
                )
            ], value=' '
        )
        self.stats_success_rate = ft.Text('-', size=16, font_family='PPM')
        self.stats_nb_students = ft.Text('-', size=16, font_family='PPM')
        self.stats_nb_success = ft.Text('-', size=16, font_family='PPM')
        self.stats_nb_boys_success = ft.Text('-', size=16, font_family='PPM')
        self.stats_nb_girls_success = ft.Text('-', size=16, font_family='PPM')


        self.statistics_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=450, height=700,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['statistics window'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_statistics_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, spacing=10, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    self.stats_class, self.stats_sequence,
                                    self.stats_subject,
                                    ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                                    ft.Column(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['statistics'], size=14, font_family='PPB', color='red'),
                                                    ft.Icon(ft.Icons.MULTILINE_CHART, size=20, color='red'),
                                                ], alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            ft.Divider(height=1, thickness=1),
                                        ], spacing=0
                                    ),
                                    ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.GROUP_OUTLINED, size=16, color='black'),
                                                    ft.Text(languages[lang]['nb students'].upper(), size=12,
                                                            font_family='PPM'),
                                                ]
                                            ),
                                            self.stats_nb_students
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.BAR_CHART_OUTLINED, size=16, color='black'),
                                                    ft.Text(languages[lang]['nb > 10'].upper(), size=12,
                                                            font_family='PPM')
                                                ]
                                            ),
                                            self.stats_nb_success
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.PIE_CHART_OUTLINE_OUTLINED, size=16, color='black'),
                                                    ft.Text(languages[lang]['success rate'].upper(), size=12,
                                                            font_family='PPM'),
                                                ]
                                            ),
                                            self.stats_success_rate
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.MAN_OUTLINED, size=16, color='blue'),
                                                    ft.Text(languages[lang]['boys > 10'].upper(), size=12,
                                                            font_family='PPM'),
                                                ]
                                            ),
                                            self.stats_nb_boys_success
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Icon(ft.Icons.WOMAN_OUTLINED, size=16, color='pink'),
                                                    ft.Text(languages[lang]['girls > 10'].upper(), size=12,
                                                            font_family='PPM'),
                                                ]
                                            ),
                                            self.stats_nb_girls_success
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                ]
                            )
                        )
                    ], spacing=0
                )
            )
        )

        self.content = ft.Stack(
            expand=True,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(languages[self.lang]['loading screen'], size=14, font_family='PPM'),
                        ft.ProgressRing(color=BASE_COLOR)
                    ], spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )

            ], alignment=ft.alignment.center
        )
        self.on_mount()

    async def build_main_view(self):
        self.content.controls.clear()

        for widget in (
                self.main_window, self.filter_window, self.new_note_window, self.edit_note_window,
                self.export_xls_window, self.import_window, self.statistics_window
        ):
            self.content.controls.append(widget)

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

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_datas(self):
        # Avribale à utiliser ...
        global page_number
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        # toutes les classes...
        details_classe = await get_all_classes_basic_info(access_token)
        for any_classe in details_classe:
            self.search_class.options.append(
                ft.dropdown.Option(
                    key=any_classe['id'], text=f"{any_classe['code']}"
                )
            )

        # Detail des notes paginées
        page_number = 1
        details_notes = await get_all_notes(
            access_token=access_token, year_id=year_id, page_number=page_number
        )
        self.page_number.value = f"page {page_number}"
        self.nb_result_search.value = f"Résultats de {page_number} à {page_number*100}"
        self.back_bt.disabled = True

        if not details_notes:
            pass
        else:
            self.table.rows.clear()
            for item in details_notes:
                self.table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item['class_code'])),
                            ft.DataCell(ft.Text(f"{item['student_name']} {item['student_surname']}".upper())),
                            ft.DataCell(ft.Text(item['sequence'])),
                            ft.DataCell(ft.Text(item['subject_short_name'])),
                            ft.DataCell(ft.Text(item['value'])),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        MyMiniIcon(
                                            'edit_outlined', languages[self.lang]['edit'], 'blue',
                                            item, self.open_edit_note_window
                                        ),
                                        MyMiniIcon(
                                            'delete_outlined', languages[self.lang]['delete'], 'red',
                                            item, None
                                        ),
                                    ], spacing=0
                                )
                            )
                        ]
                    )
                )


        await self.build_main_view()

    async def load_click_forward(self, e):
        # Avribale à utiliser ...
        global page_number
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id
        page_number += 1
        self.forward_bt.disabled = False

        details_notes = await get_all_notes(
            access_token=access_token, year_id=year_id, page_number=page_number
        )
        self.page_number.value = f"page {page_number}"
        step = 100
        start = (page_number - 1) * 100 + 1
        end = start + step - 1
        self.nb_result_search.value = f"Résultats de {start} à {end}"
        self.back_bt.disabled = True

        if not details_notes:
            pass
        else:
            self.table.rows.clear()
            for item in details_notes:
                self.table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item['class_code'])),
                            ft.DataCell(ft.Text(f"{item['student_name']} {item['student_surname']}".upper())),
                            ft.DataCell(ft.Text(item['sequence'])),
                            ft.DataCell(ft.Text(item['subject_short_name'])),
                            ft.DataCell(ft.Text(item['value'])),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        MyMiniIcon(
                                            'edit_outlined', languages[self.lang]['edit'], 'blue',
                                            item, self.open_edit_note_window
                                        ),
                                        MyMiniIcon(
                                            'delete_outlined', languages[self.lang]['delete'], 'red',
                                            item, None
                                        ),
                                    ], spacing=0
                                )
                            )
                        ]
                    )
                )

            self.back_bt.disabled = False
            self.cp.page.update()

    def click_forward(self, e):
        self.run_async_in_thread(self.load_click_forward(e))

    async def load_click_back(self, e):
        # Avribale à utiliser ...
        global page_number
        page_number -= 1
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        details_notes = await get_all_notes(
            access_token=access_token, year_id=year_id, page_number=page_number
        )
        self.page_number.value = f"page {page_number}"
        step = 100
        start = (page_number - 1) * 100 + 1
        end = start + step - 1
        self.nb_result_search.value = f"Résultats de {start} à {end}"
        self.back_bt.disabled = True

        if not details_notes:
            pass
        else:
            self.table.rows.clear()
            for item in details_notes:
                self.table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item['class_code'])),
                            ft.DataCell(ft.Text(f"{item['student_name']} {item['student_surname']}".upper())),
                            ft.DataCell(ft.Text(item['sequence'])),
                            ft.DataCell(ft.Text(item['subject_short_name'])),
                            ft.DataCell(ft.Text(item['value'])),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        MyMiniIcon(
                                            'edit_outlined', languages[self.lang]['edit'], 'blue',
                                            item, self.open_edit_note_window
                                        ),
                                        MyMiniIcon(
                                            'delete_outlined', languages[self.lang]['delete'], 'red',
                                            item, None
                                        ),
                                    ], spacing=0
                                )
                            )
                        ]
                    )
                )

            if page_number == 1:
                self.back_bt.disabled = True
            else:
                self.back_bt.disabled = False

            self.cp.page.update()

    def click_back(self, e):
        self.run_async_in_thread(self.load_click_back(e))

    async def filter_datas(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        my_class = self.search_class.value
        my_subject = self.search_subject.value
        my_sequence = self.search_sequence.value

        if not my_class or not my_sequence or not my_subject:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error msg']
            self.cp.box.open = True
            self.cp.box.update()

        else:
            filtered_datas = await get_all_notes_with_details(
                access_token, year_id, my_subject, my_class, my_sequence
            )

            if not filtered_datas:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.box.content.value = languages[self.lang]['no data']
                self.cp.box.open = True
                self.cp.box.update()
            else:
                self.table.rows.clear()
                for item in filtered_datas:
                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(item['class_code'])),
                                ft.DataCell(ft.Text(f"{item['student_name']} {item['student_surname']}".upper())),
                                ft.DataCell(ft.Text(item['sequence'])),
                                ft.DataCell(ft.Text(item['subject_short_name'])),
                                ft.DataCell(ft.Text(item['value'])),
                                ft.DataCell(
                                    ft.Row(
                                        controls=[
                                            MyMiniIcon(
                                                'edit_outlined', languages[self.lang]['edit'], 'blue',
                                                item, self.open_edit_note_window
                                            ),
                                            MyMiniIcon(
                                                'delete_outlined', languages[self.lang]['delete'], 'red',
                                                item, None
                                            ),
                                        ], spacing=0
                                    )
                                )
                            ]
                        )
                    )

                self.page_number.value = f"page 1"

                self.nb_result_search.value = f"Résultats de 1 à {len(filtered_datas)}"
                self.back_bt.disabled = True
                self.forward_bt.disabled = True

                self.cp.page.update()

    def valid_filters(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    def supp_filters(self, e):
        self.run_async_in_thread(self.load_datas())

    async def load_subject_filter(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        subjects = await get_subjects_by_class_id(access_token, self.search_class.value)

        self.search_subject.options.clear()
        self.search_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.search_subject.value = ' '
        self.search_subject.update()

        for item in subjects:
            self.search_subject.options.append(
                ft.dropdown.Option(
                    key=item['subject_id'], text=f"{item['subject_name']}".upper()
                )
            )

        self.cp.page.update()

    def on_filter_class_change(self, e):
        self.run_async_in_thread(self.load_subject_filter(e))

    def open_filter_window(self, e):
        self.show_one_window(self.filter_window)

    def close_filter_window(self, e):
        self.hide_one_window(self.filter_window)

    async def load_new_notes_data(self, e):
        role = self.cp.page.client_storage.get('role')
        access_token = self.cp.page.client_storage.get('access_token')
        user_id = self.cp.user_id

        if role != 'professeur':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.show_one_window(self.new_note_window)

            self.new_class.options.clear()
            self.new_class.options.append(
                ft.dropdown.Option(
                    key=' ', text=f"{languages[self.lang]['select option']}"
                )
            )
            self.new_class.value = ' '

            all_teacher_classes = await get_teacher_classes(access_token, user_id)
            for item in all_teacher_classes:
                self.new_class.options.append(
                    ft.dropdown.Option(
                        key=item['class_id'], text=f"{item['class_code']}"
                    )
                )
            self.cp.page.update()

    async def load_subjects_teacher(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        user_id = self.cp.user_id
        subjects = await get_teacher_subjects_for_class(access_token, user_id, self.new_class.value)

        self.new_subject.options.clear()
        self.new_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.new_subject.value = ' '

        for item in subjects:
            self.new_subject.options.append(
                ft.dropdown.Option(
                    key=item['subject_id'], text=f"{item['subject_name']}".upper()
                )
            )

        self.cp.page.update()

    def on_new_class_change(self, e):
        self.run_async_in_thread(self.load_subjects_teacher(e))

    def open_new_note_window(self, e):
        self.run_async_in_thread(self.load_new_notes_data(e))

    def close_new_note_window(self, e):
        self.new_class.value = ' '
        self.new_coefficient.value = None
        self.new_table.controls.clear()
        self.new_subject.value = ' '

        self.hide_one_window(self.new_note_window)

    async def load_students(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        self.new_coefficient.value = await get_subject_coefficient(access_token, self.new_subject.value)

        students = await get_students_without_note_for_subject(
            access_token, self.new_class.value, self.new_sequence.data, self.new_subject.value, self.cp.year_id
        )
        self.new_table.controls.clear()

        if students:
            for item in students:
                self.new_table.controls.append(BoxStudentNote(item))

            self.nb_students.value = len(students)
            self.nb_students.visible = True
            self.no_data.visible = False

        else:
            self.nb_students.value = len(students)
            self.nb_students.visible = False
            self.no_data.visible = True

        self.cp.page.update()

    def on_new_subject_change(self, e):
        self.run_async_in_thread(self.load_students(e))

    def valider_notes(self, e):
        datas_to_insert = []
        for item in self.new_table.controls:
            total_errors = 0
            if item.check.name == 'close':
                total_errors += 1
            elif item.check.name is None:
                pass
            else:
                datas_to_insert.append(
                    {'year_id': self.cp.year_id, 'student_id': item.infos['student_id'],
                     'class_id': self.new_class.value, 'sequence': self.new_sequence.data,
                     'subject_id': self.new_subject.value, 'value': float(item.my_note.value),
                     'coefficient': int(self.new_coefficient.value), 'author': self.cp.user_id}
                )

        if total_errors > 0:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error notes']
            self.cp.box.open = True
            self.cp.box.update()

        else:
            total = len(datas_to_insert)

            for i, data in enumerate(datas_to_insert):
                supabase_client.table('notes').insert(data).execute()
                self.new_progress_bar.value = (i + 1) / total

                self.cp.page.update()

            self.new_table.controls.clear()

            self.new_class.value = ' '
            self.new_coefficient.value = None
            self.new_table.controls.clear()
            self.new_subject.value = ' '

            self.hide_one_window(self.new_note_window)

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.box.content.value = languages[self.lang]['notes added']
            self.cp.box.open = True
            self.cp.box.update()

    def open_edit_note_window(self, e):
        role = self.cp.page.client_storage.get('role')
        user_id = self.cp.user_id
        print('user id: ', user_id)
        print('author: ', e.control.data['author'])

        if role != 'professeur':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()

        else:
            if e.control.data['author'] != user_id:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.box.content.value = languages[self.lang]['bad teacher error']
                self.cp.box.open = True
                self.cp.box.update()

            else:
                self.edit_note_id.value = e.control.data['note_id']
                self.edit_student.value = f"{e.control.data['student_name']} {e.control.data['student_surname']}".upper()
                self.edit_sequence.value = e.control.data['sequence']
                self.edit_subject_name.value = e.control.data['subject_name']
                self.edit_note.value = e.control.data['valeur']

                self.show_one_window(self.edit_note_window)

    def close_edit_note_window(self, e):
        self.hide_one_window(self.edit_note_window)

    def valider_edit_note(self, e):
        if self.edit_note.vaue is None:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['missing note']
            self.cp.box.open = True
            self.cp.box.update()

        else:
            if self.edit_sequence.value != self.cp.active_sequence.data:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.box.content.value = languages[self.lang]['error invalid sequence']
                self.cp.box.open = True
                self.cp.box.update()

            else:
                datas = {'value': float(self.edit_note.value)}
                edited_datas = {
                    'note_id': int(self.edit_note_id.value), 'value': float(self.edit_note.value),
                    'author': self.cp.user_id
                }
                supabase_client.table('notes').update(datas).eq('id', self.edit_note_id.value).execute()
                supabase_client.table('edited_notes').insert(edited_datas).execute()

                self.hide_one_window(self.edit_note_window)

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.box.content.value = languages[self.lang]['note edited']
                self.cp.box.open = True
                self.cp.box.update()

    async def load_export_datas(self, e):
        role = self.cp.page.client_storage.get('role')
        access_token = self.cp.page.client_storage.get('access_token')
        user_id = self.cp.user_id

        if role != 'professeur':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.show_one_window(self.export_xls_window)

            self.exp_class.options.clear()

            all_teacher_classes = await get_teacher_classes(access_token, user_id)
            for item in all_teacher_classes:
                self.exp_class.options.append(
                    ft.dropdown.Option(
                        key=item['class_id'], text=f"{item['class_code']}"
                    )
                )
            self.cp.page.update()

    def open_export_xls_window(self, e):
        self.run_async_in_thread(self.load_export_datas(e))

    def close_export_xls_window(self, e):
        self.exp_class.value = ' '
        self.exp_sequence.value = ' '
        self.exp_coefficient.value = None
        self.exp_subject.value = ' '

        self.hide_one_window(self.export_xls_window)

    async def load_export_subjects(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        user_id = self.cp.user_id
        subjects = await get_teacher_subjects_for_class(access_token, user_id, self.exp_class.value)

        classe_details = await get_class_details(access_token, self.exp_class.value)
        self.exp_class_name.value = classe_details['code']

        self.exp_subject.options.clear()
        self.exp_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.exp_subject.value = ' '
        self.exp_subject.update()

        for item in subjects:
            self.exp_subject.options.append(
                ft.dropdown.Option(
                    key=item['subject_id'], text=f"{item['subject_name']}".upper()
                )
            )

        self.cp.page.update()

    def on_export_class_change(self, e):
        self.run_async_in_thread(self.load_export_subjects(e))

    async def load_export_coefficient(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        self.exp_coefficient.value = await get_subject_coefficient(access_token, self.exp_subject.value)

        self.cp.page.update()

    def on_export_subject_change(self, e):
        self.run_async_in_thread(self.load_export_coefficient(e))

    async def load_export_students_without_note(self, e):
        if self.exp_subject.value is not None or self.exp_subject.value != ' ':
            datas_to_export = []

            access_token = self.cp.page.client_storage.get('access_token')

            subject_details = await get_subject_details(access_token, self.exp_subject.value)
            subject_name = subject_details['name']

            students: list[dict] = await get_students_without_note_for_subject(
                access_token, self.exp_class.value, self.exp_sequence.data, self.exp_subject.value, self.cp.year_id
            )

            if students:
                for item in students:
                    dico = {
                        'student_id': item['student_id'],
                        'student_name': f"{item['name']} {item['surname']}",
                        'class_id': self.exp_class.value,
                        'class_code': self.exp_class_name.value,
                        'sequence': self.exp_sequence.data,
                        'subject_id': self.exp_subject.value,
                        'subject_name': subject_name,
                        'coefficient': self.exp_coefficient.value,
                        'value': '',
                    }
                    datas_to_export.append(dico)

                # Étape 1 : Création du fichier Excel en mémoire (méthode robuste)
                df = pd.DataFrame(datas_to_export)
                output_buffer = BytesIO()

                with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Élèves')
                file_bytes = output_buffer.getvalue()

                # Générer un nom de fichier unique pour le stockage
                unique_filename = f"templates/template_{uuid.uuid4().hex}.xlsx"

                # Étape 2 : Upload vers Supabase avec httpx (méthode directe et fiable)
                headers = {
                    "apikey": key,
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                }
                upload_url = f"{url}/storage/v1/object/{DOCUMENTS_BUCKET}/{unique_filename}"

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        upload_url,
                        headers=headers,
                        content=file_bytes
                    )

                if response.status_code not in [200, 201]:
                    print("❌ Erreur pendant l'upload avec httpx:", response.text)
                    # Afficher une erreur à l'utilisateur ici
                    return

                # Étape 3 : Création de l'URL signée (en utilisant le client supabase, c'est fiable pour ça)
                signed_url_response = supabase_client.storage.from_(DOCUMENTS_BUCKET).create_signed_url(
                    path=unique_filename,
                    expires_in=3600  # 1 heure
                )
                signed_url = signed_url_response.get("signedURL")
                self.cp.page.launch_url(signed_url)

            else:
                self.cp.box.title.value = languages[self.lang]['error']
                self.cp.box.content.value = languages[self.lang]['no data']
                self.cp.box.open = True
                self.cp.box.update()
        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['select subject first']
            self.cp.box.open = True
            self.cp.box.update()

    def exporter_template_file(self, e):
        self.run_async_in_thread(self.load_export_students_without_note(e))

    async def load_import_file(self, e: ft.FilePickerResultEvent):
        if e.files:
            # on met toutes les données du fichier excel dans une liste
            file = e.files[0]
            absolute_path = os.path.abspath(file.path)
            workbook = openpyxl.load_workbook(absolute_path)
            sheet = workbook.active
            valeurs = list(sheet.values)
            header = valeurs[0]  # on definit la ligne d'entêtes
            valeurs.remove(header)  # on retire la ligne d'entêtes

            self.total_lines_of_file.value = len(valeurs)

            errors = []  # liste qui va contenir les éventuelles erreurs

            counter_verif = 0
            counter_import = 0
            nb_erreurs = 0
            nb_success = 0

            access_token = self.cp.page.client_storage.get('access_token')

            try:
                # on itère sur chaque ligne du fichier pour les vérifications
                for i, item in enumerate(valeurs):

                    # 1. variable pour savoir si la note existe...
                    is_note_exists = await note_exists(
                        access_token=access_token, student_id=item[0], year_id=self.cp.year_id,
                        subject_id=item[5], sequence=item[4]
                    )

                    # 2. liste des classes et listes des matières du professeur...
                    teacher_classes = await get_teacher_classes(
                        access_token=access_token, teacher_id=self.cp.user_id)
                    classes_id = [element['class_id'] for element in teacher_classes]

                    teacher_subjects_class = await get_teacher_subjects_for_class(
                        access_token, self.cp.user_id, item[2]
                    )
                    teacher_subj_ids = [row['subject_id'] for row in teacher_subjects_class]

                    print(item[8], type(item[8]))

                    # 3. On check toutes les potentielles erreurs
                    if isinstance(item[8], str):
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['note is number']}
                        )
                        nb_erreurs += 1
                        print('verif instance')

                    elif item[8] is None:
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['missing note']}
                        )
                        nb_erreurs += 1
                        print('verif missing note')

                    # CORRECTION : On combine la vérification du type ET de la valeur dans un seul elif
                    elif (isinstance(item[8], float) or isinstance(item[8], int)) and item[8] > 20:
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['note > 20']}
                        )
                        nb_erreurs += 1
                        print('verif note > 20')

                    elif item[2] not in classes_id or item[5] not in teacher_subj_ids:
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['bad teacher error']}
                        )
                        nb_erreurs += 1
                        print('verif bad teacher error')

                    elif is_note_exists:
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['note already exists']}
                        )
                        nb_erreurs += 1

                    elif item[0] is None or item[0] == '' or item[2] is None or item[2] == '' or item[5] is None or \
                            item[5] == '':
                        errors.append(
                            {'ligne': f"ligne {i + 1}", "nature": languages[self.lang]['missing data']}
                        )
                        nb_erreurs += 1
                        print('verif note exists')

                    else:
                        # Maintenant, ce bloc sera atteint pour les lignes valides !
                        nb_success += 1
                        print(f"success: ligne {i + 1}")

                    # Mettez à jour les compteurs à l'extérieur de la boucle if/elif/else
                    self.total_errors.value = nb_erreurs
                    counter_verif += 1
                    self.imp_verif_bar.value = counter_verif / len(valeurs)
                    self.imp_verif_text.value = f"{(counter_verif * 100 / len(valeurs)):.0f}%"
                    self.cp.page.update()

            except Exception as ex:
                print(f"❌ Erreur pendant l’analyse de item[8] : {type(e).__name__} - {e}")

            print('counter verif: ', counter_verif)
            print('erreurs', nb_erreurs)
            print('success', nb_success)
            self.total_errors.value = len(errors)
            self.cp.page.update()

            # si le nombre d'erreurs est non nul on affiche la fenêtre des erreurs sinon on importe les données
            if len(errors) > 0:
                self.bloc_table.visible = True
                self.total_errors.color = 'red'

                for error in errors:
                    self.table_errors.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(error['ligne'])),
                                ft.DataCell(ft.Text(error['nature']))
                            ]
                        )
                    )

                self.msg_error.visible = True
                self.cp.page.update()

            else:
                self.bloc_import.visible = True

                for item in valeurs:
                    datas = {
                        'year_id': self.cp.year_id, 'student_id': item[0],
                        'class_id': item[2], 'sequence': self.cp.active_sequence.data,
                        'subject_id': item[5], 'value': float(item[8]),
                        'coefficient': item[7], 'author': self.cp.user_id
                    }
                    await insert_note(access_token=access_token, note_data=datas)
                    counter_import += 1

                    self.imp_insert_text.value = f"{int(counter_import * 100 / len(valeurs))}%"
                    self.imp_insert_bar.value = counter_import / len(valeurs)
                    self.cp.page.update()

                self.cp.box.title.value = languages[self.lang]['success']
                self.cp.box.content.value = languages[self.lang]['file imported']
                self.cp.box.open = True
                self.cp.box.update()
                self.on_mount()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['no file selected']
            self.cp.box.open = True
            self.cp.box.update()

    def importer_notes(self, e):
        self.run_async_in_thread(self.load_import_file(e))

    def open_import_window(self, e):
        role = self.cp.page.client_storage.get('role')

        if role != 'professeur':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.show_one_window(self.import_window)

    def close_import_window(self, e):
        self.hide_one_window(self.import_window)

    async def load_statistics_datas(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        all_classes  = await get_all_classes_basic_info(access_token)

        for item in all_classes:
            self.stats_class.options.append(
                ft.dropdown.Option(
                    key=item['id'], text=item['code']
                )
            )

        self.show_one_window(self.statistics_window)

    def open_statistics_window(self, e):
        self.run_async_in_thread(self.load_statistics_datas(e))

    def close_statistics_window(self, e):
        self.stats_class.options.clear()
        self.stats_class.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.stats_class.value = ' '
        self.stats_subject.options.clear()
        self.stats_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        self.stats_subject.value = ' '
        self.stats_nb_students.value = '-'
        self.stats_success_rate.value = '-'
        self.stats_nb_success.value = '-'
        self.stats_nb_girls_success.value = '-'
        self.stats_nb_boys_success.value = '-'
        self.hide_one_window(self.statistics_window)

    async def load_stats_subject(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        subjects = await get_subjects_by_class_id(access_token, self.stats_class.value)

        self.stats_subject.options.clear()
        self.stats_subject.options.append(
            ft.dropdown.Option(
                key=' ', text=languages[self.lang]['select option']
            )
        )
        for item in subjects:
            self.stats_subject.options.append(
                ft.dropdown.Option(
                    key=item['subject_id'], text=item['subject_name'].upper()
                )
            )

        self.cp.page.update()

    def on_stats_class_change(self, e):
        self.run_async_in_thread(self.load_stats_subject(e))

    async def load_all_statistics(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        stats = await get_statistics_by_class_subject(
            access_token, year_id, self.stats_class.value, self.stats_subject.value, self.stats_sequence.value
        )
        print(stats)
        self.stats_nb_students.value = stats['total_notes']
        self.stats_success_rate.value = f"{stats['success_rate_percent']:.2f} %"
        self.stats_nb_success.value = stats['notes_ge_10']
        self.stats_nb_girls_success.value = stats['girls_above_10']
        self.stats_nb_boys_success.value = stats['boys_above_10']
        self.cp.page.update()

    def on_stats_subject_change(self, e):
        self.run_async_in_thread(self.load_all_statistics(e))







