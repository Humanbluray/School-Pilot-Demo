from components import MyButton, ColoredIconButton, ColoredButton, MyMiniIcon, SingleOption, EditSingleOption, ColoredIcon
from utils.styles import drop_style, datatable_style, numeric_style, cool_style
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading, json
from services.async_functions.teachers_functions import *
from services.async_functions.students_functions import get_current_year_label, get_current_year_id
from utils.useful_functions import add_separator, format_number


class Teachers(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center
        )
        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # KPI __________________________________________________________________________________
        self.nb_teachers = ft.Text(size=18, font_family="PPB")
        self.nb_absences = ft.Text(size=18, font_family="PPB")

        # Main window __________________________________________________________________________
        self.search = ft.TextField(
            **cool_style, prefix_icon="search", width=300,
            on_change=self.on_search_change
        )
        self.table = ft.DataTable(
            **datatable_style, expand=True,
            columns=[
                ft.DataColumn(ft.Text('')),
                ft.DataColumn(
                    ft.Text(languages[lang]['name'].capitalize())
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['gender'].capitalize())
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['contact'].capitalize())
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['hourly pay'].capitalize())
                ),
                ft.DataColumn(
                    ft.Text('Actions')
                ),
            ]
        )
        self.current_year_label = ft.Text(f"{get_current_year_label()}", size=11, color='indigo', font_family="PPM")
        self.current_year_id = ft.Text(f'{get_current_year_id()}')

        # KPI...
        self.nb_teachers = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.rate_per_hours = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.nb_hours_affected = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.cost_per_hours = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)

        self.main_window = ft.Container(
            expand=True, content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(languages[lang]['teachers'].capitalize(), size=16, font_family='PPB'),
                    ft.Row(
                        expand=True,
                        controls=[
                            # Datas _______________________________________________________________________________
                            ft.Container(
                                expand=True, bgcolor='white', border_radius=16, padding=0,
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
                                                                languages[lang]['new teacher'], 'person_add',
                                                                self.open_new_teacher_window
                                                            ),
                                                            ColoredButton(
                                                                languages[lang]['assign head'], 'assignment_ind',
                                                                self.open_head_teacher_window
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
                                                    self.search,
                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            ),
                                        ),
                                        ft.Divider(color=ft.Colors.TRANSPARENT, height=1),
                                        ft.ListView(expand=True, controls=[self.table]),
                                        ft.Container(
                                            padding=10

                                        ),
                                    ]
                                )
                            ),
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
                                                        ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'indigo', 'indigo50'),
                                                        ft.Text(languages[lang]['teachers'].upper(), size=12,
                                                                font_family='PPI',
                                                                color='indigo')
                                                    ], alignment=ft.MainAxisAlignment.START
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        self.nb_teachers,
                                                        ft.Text(languages[lang]['nb teachers'], size=11,
                                                                font_family='PPI',
                                                                color='grey')
                                                    ], spacing=0
                                                )
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),
                                    ft.VerticalDivider(color=ft.Colors.TRANSPARENT),
                                    ft.Container(
                                        width=170, height=120, padding=10, border_radius=24,
                                        border=ft.border.all(1, 'white'),
                                        bgcolor='white',
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'teal', 'teal50'),
                                                        ft.Text(languages[lang]['rate'].upper(), size=12,
                                                                font_family='PPI',
                                                                color='teal')
                                                    ], alignment=ft.MainAxisAlignment.START
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        self.rate_per_hours,
                                                        ft.Text(languages[lang]['rate per hour'], size=11,
                                                                font_family='PPI',
                                                                color='grey')
                                                    ], spacing=0
                                                )
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),
                                    ft.VerticalDivider(color=ft.Colors.TRANSPARENT),
                                    ft.Container(
                                        width=170, height=120, padding=10, border_radius=24,
                                        border=ft.border.all(1, 'white'),
                                        bgcolor='white',
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'deeporange',
                                                                    'deeporange50'),
                                                        ft.Text(languages[lang]['hours'].upper(), size=12,
                                                                font_family='PPI',
                                                                color='deeporange')
                                                    ], alignment=ft.MainAxisAlignment.START
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        self.nb_hours_affected,
                                                        ft.Text(languages[lang]['nb hours affected'], size=11,
                                                                font_family='PPI',
                                                                color='grey')
                                                    ], spacing=0
                                                )
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),
                                    ft.VerticalDivider(color=ft.Colors.TRANSPARENT),
                                    ft.Container(
                                        width=170, height=120, padding=10, border_radius=24,
                                        border=ft.border.all(1, 'white'),
                                        bgcolor='white',
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'green', 'green50'),
                                                        ft.Text(languages[lang]['total'].upper(), size=12,
                                                                font_family='PPI',
                                                                color='green')
                                                    ], alignment=ft.MainAxisAlignment.START
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        self.cost_per_hours,
                                                        ft.Text(languages[lang]['cost per week'], size=11,
                                                                font_family='PPI',
                                                                color='grey')
                                                    ], spacing=0
                                                )
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ),

                                ],
                            ),
                        ]
                    ),
                ]
            )
        )

        # New teacher window ____________________________________________________________________
        self.new_uid = ft.TextField(
            **cool_style, width=500, prefix_icon=ft.Icons.CREDIT_CARD
        )
        self.new_name = ft.TextField(
            **cool_style, prefix_icon="person_outlined", width=300,
        )
        self.new_surname = ft.TextField(
            **cool_style, prefix_icon="person_outlined", width=300,
        )
        self.new_gender = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.WC_OUTLINED, options=[
                ft.dropdown.Option(gender) for gender in ['M', 'F']
            ], width=180
        )
        self.new_pay = ft.TextField(
            **numeric_style, width=180, prefix_icon='monetization_on_outlined', value='0', read_only=True
        )
        self.new_contact = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200, prefix_text="+237 ",
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.new_subjects = ft.GridView(
            expand=True,
            max_extent=120,  # largeur max par cellule (laisser assez pour le padding)
            child_aspect_ratio=4,  # largeur / hauteur
            spacing=10,
            run_spacing=10,
        )
        self.count_subject = ft.Text('0', size=13, font_family='PPB')
        self.new_teacher_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=700, height=700,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new teacher'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_new_teacher_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text("uid", size=11, color='grey', font_family='PPM'),
                                            self.new_uid
                                        ], spacing=2
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['name'], size=11, color='grey', font_family='PPM'),
                                                    self.new_name
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['surname'], size=11, color='grey',
                                                            font_family='PPM'),
                                                    self.new_surname
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Row(
                                        controls=[
                                            self.new_gender,
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['contact'], size=11, color='grey',
                                                            font_family='PPM'),
                                                    self.new_contact
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['hourly pay'], size=11, color='grey',
                                                            font_family='PPM'),
                                                    self.new_pay
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['subjects taught'].upper(), size=13,
                                                            font_family='PPB'),
                                                    ft.Text(f"({languages[lang]['click to select']})", size=13,
                                                            font_family='PPI', color='grey'),
                                                ]
                                            ),
                                            self.count_subject
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(
                                        padding=10, expand=True, height=220,
                                        border_radius=10, border=ft.border.all(1, '#f0f0f6'),
                                        alignment=ft.alignment.center,
                                        content=self.new_subjects
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row([MyButton(languages[lang]['valid'], 'check', 180, self.add_teacher)])
                                ], spacing=10, expand=True
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # Schedule window...
        self.table_schedule = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=16, color='grey'),
                            ft.Text(languages[lang]['day'])
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.TIMER_OUTLINED, size=16, color='grey'),
                            ft.Text(languages[lang]['slot'])
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ROOFING_OUTLINED, size=16, color='grey'),
                            ft.Text(languages[lang]['class'])
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.BOOK_OUTLINED, size=16, color='grey'),
                            ft.Text(languages[lang]['subject'])
                        ]
                    )
                )
            ]
        )
        self.no_data = ft.Text(languages[lang]['no data'], size=13, font_family="PPB", color='red', visible=False)
        self.nb_hours = ft.TextField(**cool_style, width=150, text_align=ft.TextAlign.RIGHT, prefix_icon='timer_outlined', read_only=True)
        self.sc_head_class = ft.TextField(**cool_style, width=170, prefix_icon='roofing', read_only=True)
        self.nb_classes = ft.TextField(**cool_style, width=150, text_align=ft.TextAlign.RIGHT, prefix_icon='roofing', read_only=True)
        self.schedule_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16), expand=True,
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=800, height=700,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.CALENDAR_MONTH, size=24, color='black'),
                                            ft.Text(languages[lang]['schedule'], size=16, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_schedule_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(
                                                        languages[lang]['head class'], size=11, font_family='PPM', color='grey'
                                                    ),
                                                    self.sc_head_class
                                                ], spacing=2
                                            ),
                                            ft.Container(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Column(
                                                            controls=[
                                                                ft.Text(languages[lang]['hourly load'], size=11,
                                                                        font_family='PPM', color='grey'),
                                                                self.nb_hours,
                                                            ], spacing=2
                                                        ),
                                                        ft.Column(
                                                            controls=[
                                                                ft.Text(languages[lang]['count classes'], size=11,
                                                                        font_family='PPM', color='grey'),
                                                                self.nb_classes,
                                                            ], spacing=2
                                                        )
                                                    ]
                                                )
                                            )
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.ListView([self.table_schedule], expand=True),
                                    ft.Row([self.no_data], alignment=ft.MainAxisAlignment.CENTER)
                                ], spacing=10, expand=True
                            )
                        )
                    ], spacing=0,
                )
            )
        )

        # edit teacher window___________________________________________
        self.edit_uid = ft.TextField(**cool_style, width=400, prefix_icon='credit_card', visible=False)
        self.edit_name = ft.TextField(
            **cool_style, prefix_icon="person_outlined", width=350,
        )
        self.edit_surname = ft.TextField(
            **cool_style, prefix_icon="person_outlined", width=350,
        )
        self.edit_gender = ft.TextField(
            **cool_style, prefix_icon='wc', width=100,
        )
        self.edit_pay = ft.TextField(
            **cool_style, width=150, prefix_icon='monetization_on_outlined', input_filter=ft.NumbersOnlyInputFilter(),
            read_only=True if self.cp.page.client_storage.get('role') != 'principal' else False
        )
        self.edit_contact = ft.TextField(
            **cool_style, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, width=200,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.edit_subject = ft.TextField(
            **cool_style, expand=True, prefix_icon=ft.Icons.BOOK_OUTLINED
        )
        self.edit_select_subjects = ft.GridView(
            expand=True,
            max_extent=120,  # largeur max par cellule (laisser assez pour le padding)
            child_aspect_ratio=4,  # largeur / hauteur
            spacing=10,
            run_spacing=10,
        )
        self.edit_count_subject = ft.Text('0', size=13, font_family='PPB')
        self.edit_teacher_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=750, height=700,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['edit teacher'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_edit_teacher_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text('uid', size=11, font_family='PPM', color='grey'),
                                            self.edit_uid,
                                        ], spacing=2, visible=False
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['name'], size=11, font_family='PPM', color='grey'),
                                                    self.edit_name,
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['surname'], size=11, font_family='PPM', color='grey'),
                                                    self.edit_surname,
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['gender'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.edit_gender,
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['contact'], size=11,
                                                            font_family='PPM', color='grey'),
                                                    self.edit_contact
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['hourly pay'], size=11,
                                                            font_family='PPM', color='grey'),
                                                    self.edit_pay,
                                                ], spacing=2
                                            ),
                                        ]
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['subjects'], size=11, font_family='PPM',
                                                    color='grey'),
                                            self.edit_subject,
                                        ], spacing=2
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['subjects taught'].upper(), size=13,
                                                            font_family='PPB'),
                                                    ft.Text(f"({languages[lang]['click to select']})", size=13,
                                                            font_family='PPI', color='grey'),
                                                ]
                                            ),
                                            self.edit_count_subject
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(
                                        padding=10, expand=True, height=220,
                                        border_radius=10, border=ft.border.all(1, '#f0f0f6'),
                                        alignment=ft.alignment.center,
                                        content=self.edit_select_subjects
                                    ),
                                    ft.Container(
                                        padding=ft.padding.only(10,0,10,0),
                                        content=ft.Row(
                                            [
                                                MyButton(
                                                    languages[lang]['valid'], 'check_circle', 180,
                                                    self.edit_teacher
                                                )
                                            ]
                                        )
                                    )
                                ], spacing=10, expand=True
                            )
                        )
                    ], spacing=0
                )
            )
        )
        self.head_teacher_name = ft.Dropdown(
            **drop_style, expand=True, prefix_icon='person_outlined',
            options=[ft.dropdown.Option(key=' ', text=languages[lang]['select option'])],
            menu_height=200, value=' '
        )
        self.head_class_name = ft.Dropdown(
            **drop_style, expand=True, prefix_icon='roofing',
            options=[ft.dropdown.Option(key=' ', text=languages[lang]['select option'])],
            menu_height=200, value=' '
        )
        self.head_teacher_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=400, height=350,
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
                                            ft.Icon(ft.Icons.ASSIGNMENT_IND, size=24, color='black'),
                                            ft.Text(languages[lang]['assign head'], size=16, font_family='PPB'),
                                        ]
                                    ),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_head_teacher_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['teacher'], size=11, font_family='PPM', color='grey'),
                                            self.head_teacher_name,
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['class'], size=11, font_family='PPM',
                                                    color='grey'),
                                            self.head_class_name,
                                        ], spacing=2
                                    ),
                                    ft.Container(
                                        padding=10,
                                        content=ft.Row(
                                            [
                                                MyButton(
                                                    languages[lang]['valid'], 'check_circle', 330,
                                                    self.valid_assignment
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

        # content ______________________________________________________________
        # self.content = ft.Stack(
        #     expand=True, controls=[
        #         self.main_window, self.new_teacher_window, self.schedule_window, self.edit_teacher_window,
        #         self.head_teacher_window
        #     ], alignment=ft.alignment.center
        # )

        self.on_mount()

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

    async def build_main_view(self):
        self.content.controls.clear()

        for widget in (
                self.main_window, self.new_teacher_window, self.schedule_window, self.edit_teacher_window,
                self.head_teacher_window
        ):
            self.content.controls.append(widget)

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
        access_token = self.cp.page.client_storage.get('access_token')
        self.table.rows.clear()
        details = await get_all_teachers(access_token)

        total_pay = 0
        total_hours = 0

        for detail in details:
            if detail['is_head_teacher']:
                icone = ft.Icons.ASSIGNMENT_IND
            else:
                icone = None

            if detail['gender'] == 'M':
                gender_color = "blue"
            else:
                gender_color = 'pink'

            if detail['pay'] is None:
                pay = '*****'
            else:
                pay = add_separator(detail['pay'])
                total_pay += detail['pay']

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Icon(icone, size=20, color='black')),
                        ft.DataCell(ft.Text(f"{detail['name']} {detail['surname']}".upper())),
                        ft.DataCell(ft.Icon('person_outlined', size=18, color=gender_color)),
                        ft.DataCell(ft.Text(f"{detail['contact']}")),
                        ft.DataCell(ft.Text(pay)),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    MyMiniIcon(
                                        'edit_outlined', languages[self.lang]['edit'], 'grey', detail,
                                        self.open_edit_teacher_window
                                    ),
                                    MyMiniIcon(
                                        'calendar_month_outlined', languages[self.lang]['menu time table'],
                                        'grey', detail, self.open_schedule_window
                                    ),
                                ], spacing=0
                            )
                        )
                    ]
                )
            )

        await self.build_main_view()

        short_names = await get_all_distinct_subject_short_names(access_token)
        for name in short_names:
            self.edit_select_subjects.controls.append(
                EditSingleOption(self, name)
            )

        for name in short_names:
            self.new_subjects.controls.append(
                SingleOption(self, name)
            )

        self.nb_teachers.value = len(details)
        self.rate_per_hours.value = f"{add_separator(int(total_pay / len(details)))}"

        affectations = await  get_all_affectations_details(access_token)
        for affectation in affectations:
            if affectation['status']:
                total_hours += 1

        self.nb_hours_affected.value = total_hours
        self.cost_per_hours.value = f"{format_number(total_pay / len(details) * total_hours)}"
        self.cp.page.update()

    async def filter_datas(self, e):
        details = await get_all_teachers(self.cp.page.client_storage.get('access_token'))
        search = self.search.value.lower() if self.search.value else ''
        filtered_datas = list(filter(lambda x: search in x['name'].lower() or search in x['surname'].lower(), details))

        self.table.rows.clear()
        for detail in filtered_datas:
            if detail['is_head_teacher']:
                icone = ft.Icons.ASSIGNMENT_IND
            else:
                icone = None

            if detail['gender'] == 'M':
                gender_color = "blue"
            else:
                gender_color = 'pink'

            if detail['pay'] is None:
                pay = '*****'
            else:
                pay = add_separator(detail['pay'])

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Icon(icone, size=20, color='black')),
                        ft.DataCell(ft.Text(f"{detail['name']} {detail['surname']}".upper())),
                        ft.DataCell(ft.Icon('person_outlined', size=18, color=gender_color)),
                        ft.DataCell(ft.Text(f"{detail['contact']}")),
                        ft.DataCell(ft.Text(pay)),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    MyMiniIcon('edit_outlined', languages[self.lang]['edit'], 'grey', detail, self.open_edit_teacher_window),
                                    MyMiniIcon('calendar_month_outlined', languages[self.lang]['menu time table'],
                                               'grey', detail, self.open_schedule_window),
                                ], spacing=0
                            )
                        )
                    ]
                )
            )

        self.cp.page.update()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    def open_new_teacher_window(self, e):
        role = self.cp.page.client_storage.get('role')
        if role != 'admin':
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.show_one_window(self.new_teacher_window)

    def close_new_teacher_window(self, e):
        self.hide_one_window(self.new_teacher_window)

    def add_teacher(self, e):
        count = 0

        for widget in (self.new_name, self.new_surname, self.new_pay, self.new_gender, self.new_contact, self.new_uid):
            if widget.value is None:
                count += 1

        if count == 0 and self.count_subject.value != '0' :
            subjects_selected = []

            for widget in self.new_subjects.controls[:]:
                if widget.selected:
                    subjects_selected.append(widget.name)

            supabase_client.table('teachers').insert(
                {
                    "name": self.new_name.value, 'surname': self.new_surname.value, 'gender': self.new_gender.value,
                    "pay": int(self.new_pay.value), "contact": self.new_contact.value,
                    "subjects": subjects_selected, 'id': self.new_uid.value
                }
            ).execute()

            for widget in (self.new_name, self.new_surname, self.new_pay, self.new_gender, self.new_contact):
                widget.value = None
                widget.update()

            self.count_subject.value = '0'
            self.count_subject.update()

            for widget in self.new_subjects.controls[:]:
                widget.set_initial()

            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.box.content.value = languages[self.lang]['teacher registered']
            self.cp.box.open = True
            self.cp.box.update()

            self.on_mount()
            self.cp.page.update()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error msg']
            self.cp.box.open = True
            self.cp.box.update()

    async def load_schedule(self, e):
        self.table_schedule.rows.clear()
        self.cp.page.update()
        self.show_one_window(self.schedule_window)

        access_token = self.cp.page.client_storage.get('access_token')
        time_table = await get_teacher_affectations(e.control.data['id'], access_token)

        count_classes: set = set()
        for item in time_table:
            count_classes.add(item['class_code'])

        self.nb_classes.value = len(count_classes)
        self.sc_head_class.value = await get_head_class_code_by_teacher_id(
            access_token, e.control.data['id'], self.cp.year_id
        )
        self.nb_hours.value = len(time_table)

        if not time_table:
            self.no_data.visible = True
            self.no_data.update()

        else:
            self.no_data.visible = False
            self.no_data.update()

            for data in time_table:
                self.table_schedule.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(languages[self.lang][data['day']])),
                            ft.DataCell(ft.Text(data['slot'])),
                            ft.DataCell(ft.Text(data['class_code'])),
                            ft.DataCell(ft.Text(data['subject_name'].upper()))
                        ]
                    )
                )

        self.cp.page.update()

    def open_schedule_window(self, e):
        self.run_async_in_thread(self.load_schedule(e))

    def close_schedule_window(self, e):
        self.hide_one_window(self.schedule_window)

    def open_edit_teacher_window(self, e):

        role = self.cp.page.client_storage.get('role')

        if role not in ['admin', 'principal']:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()
        else:
            self.edit_name.value = e.control.data['name']
            self.edit_gender.value = e.control.data['gender']
            self.edit_surname.value = e.control.data['surname']
            self.edit_uid.value = e.control.data['id']
            self.edit_pay.value = e.control.data['pay']  if role == 'principal' else '*****'
            self.edit_pay.read_only = True if role == 'admin' else False
            self.edit_contact.value = e.control.data['contact']
            self.edit_count_subject.value = len(e.control.data['subjects']) if e.control.data['subjects'] else '0'

            if not e.control.data['subjects']:
                pass
            else:
                for item, subject in enumerate(e.control.data['subjects']):
                    if item == 0:
                        self.edit_subject.value = self.edit_subject.value + f"{subject}"
                    else:
                        self.edit_subject.value = self.edit_subject.value + '; ' + f"{subject}"

                for item in self.edit_select_subjects.controls[:]:
                    if item.name in e.control.data['subjects']:
                        item.set_selected()

            self.show_one_window(self.edit_teacher_window)

    def close_edit_teacher_window(self, e):
        for item in self.edit_select_subjects.controls[:]:
            item.set_initial()

        self.edit_name.value = None
        self.edit_surname.value = None
        self.edit_uid.value = None
        self.edit_pay.value = None
        self.edit_pay.read_only = None
        self.edit_contact.value = None
        self.edit_count_subject.value = None
        self.edit_subject.value = None

        self.hide_one_window(self.edit_teacher_window)

    def edit_teacher(self, e):
        role = self.cp.page.client_storage.get('role')

        if role == 'principal':
            count = 0

            for widget in (self.edit_name, self.edit_surname, self.edit_pay, self.edit_gender, self.edit_contact):
                if widget.value is None:
                    count += 1

            if count == 0 and self.edit_count_subject.value != '0':
                subjects_selected = []

                for widget in self.edit_select_subjects.controls[:]:
                    if widget.selected:
                        subjects_selected.append(widget.name)

                for item in subjects_selected:
                    print(item)

                supabase_client.table('teachers').update(
                    {'name': self.edit_name.value, 'surname': self.edit_surname.value, 'contact': self.edit_contact.value,
                     'pay': int(self.edit_pay.value), "gender": self.edit_gender.value,
                     "subjects": subjects_selected}
                ).eq('id', self.edit_uid.value).execute()

        else:
            count = 0

            for widget in (self.edit_name, self.edit_surname, self.edit_pay, self.edit_gender, self.edit_contact):
                if widget.value is None:
                    count += 1

            if count == 0 and self.edit_count_subject.value != '0':
                subjects_selected = []

                for widget in self.edit_select_subjects.controls[:]:
                    if widget.selected:
                        subjects_selected.append(widget.name)

                for item in subjects_selected:
                    print(item)

                supabase_client.table('teachers').update(
                    {'name': self.edit_name.value, 'surname': self.edit_surname.value, 'contact': self.edit_contact.value,
                     "gender": self.edit_gender.value, "subjects": subjects_selected}
                ).eq('id', self.edit_uid.value).execute()

        self.on_mount()
        self.hide_one_window(self.edit_teacher_window)

        for item in self.edit_select_subjects.controls[:]:
            item.set_initial()

        self.edit_select_subjects.controls.clear()

        self.edit_name.value = None
        self.edit_surname.value = None
        self.edit_uid.value = None
        self.edit_pay.value = None
        self.edit_pay.read_only = None
        self.edit_contact.value = None
        self.edit_count_subject.value = None
        self.edit_subject.value = None

        self.cp.box.title.value = languages[self.lang]['success']
        self.cp.box.content.value = languages[self.lang]['teacher edited']
        self.cp.box.open = True
        self.cp.box.update()

    async def load_head_teacher_datas(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        non_head_teachers = await get_non_head_teachers(access_token, self.cp.year_id)

        for item in non_head_teachers:
            self.head_teacher_name.options.append(
                ft.dropdown.Option(
                    key=item['id'], text=f"{item['name']} {item['surname']}".upper()
                )
            )

        classes_without_head_teacher = await get_classes_without_head_teacher(
            access_token, self.cp.year_id
        )
        for item in classes_without_head_teacher:
            self.head_class_name.options.append(
                ft.dropdown.Option(
                    key=item['id'], text=f"{item['code']}"
                )
            )

        self.show_one_window(self.head_teacher_window)

    def open_head_teacher_window(self, e):
        self.run_async_in_thread(self.load_head_teacher_datas(e))

    def close_head_teacher_window(self, e):
        for widget in (self.head_teacher_name, self.head_class_name):
            widget.options.clear()
            widget.options.append(
                ft.dropdown.Option(
                    key=' ', text=languages[self.lang]['select option']
                )
            )
            widget.value = ' '
            widget.update()

        self.hide_one_window(self.head_teacher_window)

    def valid_assignment(self, e):
        if self.head_class_name.value != ' ' and self.head_teacher_name.value != ' ':
            datas = {
                "class_id": self.head_class_name.value,
                "teacher_id": self.head_teacher_name.value,
                'year_id': self.cp.year_id
            }
            supabase_client.table('head_teachers').insert(datas).execute()
            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.box.content.value = languages[self.lang]['head teacher assigned']
            self.cp.box.open = True
            self.cp.box.update()

            for widget in (self.head_teacher_name, self.head_class_name):
                widget.options.clear()
                widget.options.append(
                    ft.dropdown.Option(
                        key=' ', text=languages[self.lang]['select option']
                    )
                )
                widget.value = ' '
                widget.update()

            self.on_mount()
            self.hide_one_window(self.head_teacher_window)

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error msg']
            self.cp.box.open = True
            self.cp.box.update()



