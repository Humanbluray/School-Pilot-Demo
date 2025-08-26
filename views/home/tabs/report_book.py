from components import MyButton, MyIconButton, MyMiniIcon, ColoredIcon, ColoredButton, BoxStudentNote
from utils.styles import *
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading, openpyxl, uuid
import pandas as pd
from utils.useful_functions import convertir_date, write_number
import io, requests, uuid
from services.async_functions.report_book_functions import *
from utils.useful_functions import add_separator, get_rating
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

DOCUMENTS_BUCKET = 'documents'


class ReportBook(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center
        )

        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # Kpi...
        self.nb_success = ft.Text('-', size=28, font_family='PPM', weight=ft.FontWeight.BOLD)
        self.nb_fails = ft.Text('-', size=28, font_family='PPM', weight=ft.FontWeight.BOLD)
        self.success_rate = ft.Text('-', size=28, font_family='PPM', weight=ft.FontWeight.BOLD)

        self.ct_success = ft.Container(
            width=170, height=120, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'indigo', 'indigo50'),
                            ft.Text(languages[lang]['nb > 10'].upper(), size=12,
                                    font_family='PPI',
                                    color='indigo')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.nb_success,
                            ft.Text(languages[lang]['success 2'], size=11, font_family='PPI',
                                    color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_fails = ft.Container(
            width=170, height=120, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'teal', 'teal50'),
                            ft.Text(languages[lang]['nb < 10'].upper(), size=12,
                                    font_family='PPI',
                                    color='teal')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.nb_fails,
                            ft.Text(languages[lang]['fails'], size=11, font_family='PPI',
                                    color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_rate = ft.Container(
            width=170, height=120, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'deeporange', 'deeporange50'),
                            ft.Text(languages[lang]['rate > 10'].upper(), size=12,
                                    font_family='PPI',
                                    color='deeporange')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.success_rate,
                            ft.Text(languages[lang]['success rate'], size=11, font_family='PPI',
                                    color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        # Main window...
        self.search = ft.TextField(
            **cool_style, width=250, prefix_icon=ft.Icons.SEARCH, on_change=self.on_search_change
        )
        self.table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[lang]['name'], languages[lang]['class'], languages[lang]['sequence'],
                    languages[lang]['points'], languages[lang]['coefficient'], languages[lang]['average'],
                    languages[lang]['status'], languages[lang]['rank'], 'Actions'
                ]
            ]
        )
        self.main_window = ft.Container(
            expand=True, content=ft.Column(
                controls=[
                    # kpi...
                    ft.Row(
                        controls=[
                            self.ct_success, ft.VerticalDivider(),
                            self.ct_fails, ft.VerticalDivider(),
                            self.ct_rate
                        ]
                    ),
                    ft.Row(
                        expand=True,
                        controls=[
                            ft.Container(
                                bgcolor='white', border_radius=16, padding=0, expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Container(
                                            padding=20,
                                            content=ft.Row(
                                                controls=[
                                                    ft.Row(
                                                        controls=[
                                                            ColoredButton(
                                                                languages[lang]['quarterly reports'],
                                                                ft.Icons.FOLDER_OPEN,
                                                                None
                                                            ),
                                                            ColoredButton(
                                                                languages[lang]['annual reports'], ft.Icons.RULE_FOLDER_OUTLINED,
                                                                None
                                                            ),
                                                            ColoredButton(
                                                                languages[lang]['class print'],
                                                                ft.Icons.PRINT_ROUNDED,
                                                                self.open_pr_window
                                                            )
                                                        ]
                                                    ),
                                                    self.search
                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            )
                                        ),
                                        ft.ListView(expand=True, controls=[self.table]),
                                        ft.Container(
                                            padding=20,
                                            content=ft.Row(
                                                controls=[
                                                    ft.Row(
                                                        controls=[
                                                            ft.Icon(
                                                                ft.Icons.DOWNLOAD_DONE, size=20, color="black87"
                                                            ),
                                                            ft.Text(languages[lang]['data extraction'].upper(), size=12,
                                                                    font_family='PPB'),
                                                        ]
                                                    ),
                                                    ft.Row(
                                                        controls=[
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
                                                    )
                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            )
                                        ),
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        )

        # details window...
        self.det_table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[lang]['subject'], languages[lang]['note'], languages[lang]['coefficient'],
                    languages[lang]['total'], languages[lang]['rating'],
                ]
            ]
        )
        self.det_name = ft.Text('-', size=16, font_family='PPB')
        self.det_surname = ft.Text('-', size=12, color='grey', font_family='PPM')
        self.det_image = ft.CircleAvatar(radius=30)
        self.det_bg = ft.CircleAvatar(radius=33, bgcolor=BASE_COLOR)
        self.det_zone = ft.Stack(
            alignment=ft.alignment.center, controls=[self.det_bg, self.det_image]
        )
        self.det_sequence = ft.Text(size=16, font_family="PPM")
        self.det_class = ft.Text(size=16, font_family="PPM")
        self.det_moyenne = ft.Text(size=16, font_family="PPM")
        self.det_rang = ft.Text(size=16, font_family="PPM")
        self.det_rating = ft.Text(size=16, font_family="PPM")
        self.bt_print_report = MyMiniIcon(
            ft.Icons.PRINT, languages[lang]['print'], 'black', None, self.download_report_book_second_cycle
        )
        self.bt_print_report.visible = False
        self.load_bar = ft.ProgressBar(
            width=150, height=5, border_radius=16, color=BASE_COLOR, bgcolor='#f0f0f6'
        )
        self.load_text = ft.Text(
            languages[lang]['data loading'], size=12, font_family='PPM', color="grey"
        )

        self.details_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=800, height=750,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['note details'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_details_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    self.det_zone,
                                                    ft.Column([self.det_name, self.det_surname], spacing=0)
                                                ]
                                            ),
                                            ft.Row(
                                                controls=[
                                                    self.bt_print_report, self.load_bar, self.load_text
                                                ]
                                            )
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(
                                        padding=10, border_radius=16, bgcolor='grey50',
                                        content=ft.Row(
                                            controls=[
                                                # class...
                                                ft.Row(
                                                    controls=[
                                                        ft.Row(
                                                            controls=[
                                                                ft.Icon('roofing', color='black', size=16),
                                                                ft.Text(languages[lang]['class'], size=12,
                                                                        font_family='PPM', color='black')
                                                            ]
                                                        ), self.det_class

                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon('calendar_month_outlined', color='black', size=16),
                                                        self.det_sequence
                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Row(
                                                            controls=[
                                                                ft.Icon(ft.Icons.BAR_CHART_OUTLINED, color='black', size=16),
                                                                ft.Text(languages[lang]['average'], size=12,
                                                                        font_family='PPM', color='black')
                                                            ]
                                                        ), self.det_moyenne

                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Row(
                                                            controls=[
                                                                ft.Icon(ft.Icons.PIE_CHART_SHARP, color='black', size=16),
                                                                ft.Text(languages[lang]['rank'], size=12,
                                                                        font_family='PPM', color='black')
                                                            ]
                                                        ), self.det_rang
                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Row(
                                                            controls=[
                                                                ft.Icon(ft.Icons.REQUEST_QUOTE, color='black', size=16),
                                                                ft.Text(languages[lang]['rating'], size=12,
                                                                        font_family='PPM', color='black')
                                                            ]
                                                        ), self.det_rating

                                                    ]
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    ),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.ListView(
                                        expand=True, controls=[self.det_table]
                                    )
                                ]

                            )
                        )
                    ], spacing=0
                )
            )
        )

        # fenêtre impression classes...
        self.pr_class = ft.Dropdown(
            **drop_style, prefix_icon='roofing', menu_height=200,
            expand=True, text_align=ft.TextAlign.CENTER,
            options=[
                ft.dropdown.Option(
                    key=' ', text=f"{languages[lang]['select option']}"
                )
            ], value=" "
        )
        self.pr_type = ft.Dropdown(
            **drop_style, expand=True, text_align=ft.TextAlign.CENTER,
            prefix_icon=ft.Icons.LABEL_OUTLINED,
            options=[
                ft.dropdown.Option(key=" ", text=languages[lang]['select option']),
                ft.dropdown.Option(key="monthly", text=languages[lang]['monthly']),
                ft.dropdown.Option(key="quarterly", text=languages[lang]['quarterly']),
                ft.dropdown.Option(key="annual", text=languages[lang]['annual']),
            ], on_change=self.on_changing_type, value=" "

        )
        self.pr_quarter = ft.Dropdown(
            **drop_style, expand=True, text_align=ft.TextAlign.CENTER,
            prefix_icon=ft.Icons.CALENDAR_MONTH_SHARP,
            menu_height=200, visible=False, label=languages[lang]['quarter'],
            options=[
                ft.dropdown.Option(key=" ", text=languages[lang]['select option']),
                ft.dropdown.Option(key="quarter 1", text=languages[lang]['quarter 1']),
                ft.dropdown.Option(key="quarter 2", text=languages[lang]['quarter 2']),
                ft.dropdown.Option(key="quarter 3", text=languages[lang]['quarter 3']),
            ], value=" "
        )
        self.pr_sequence = ft.Dropdown(
            **drop_style, expand=True, text_align=ft.TextAlign.CENTER,
            prefix_icon=ft.Icons.CALENDAR_MONTH_SHARP, menu_height=200,
            label=languages[lang]['sequence'],
            visible=False,
            options=[
                ft.dropdown.Option(key=" ", text=languages[lang]['select option']),
                ft.dropdown.Option(key="sequence 1", text=languages[lang]['sequence 1']),
                ft.dropdown.Option(key="sequence 2", text=languages[lang]['sequence 2']),
                ft.dropdown.Option(key="sequence 3", text=languages[lang]['sequence 3']),
                ft.dropdown.Option(key="sequence 4", text=languages[lang]['sequence 4']),
                ft.dropdown.Option(key="sequence 5", text=languages[lang]['sequence 5']),
                ft.dropdown.Option(key="sequence 6", text=languages[lang]['sequence 6']),
            ], value=" "
        )
        self.pr_print_class_bt = MyButton(
            languages[lang]['valid'], 'check_circle', None, self.build_report_file
        )
        self.pr_download_report_bt = MyButton(
            languages[lang]['download'], 'check_circle', None, None
        )
        self.pr_download_report_bt.visible = False
        self.pr_ring = ft.ProgressRing(color=BASE_COLOR, visible=False)
        self.pr_text = ft.Text(size=12, font_family='PPM')
        self.pr_construction = ft.Text(languages[lang]['generating file'], size=16, font_family="PPB", visible=False)

        self.pr_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=600, height=600,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['class print'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_pr_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['report type'], size=11, color='grey'),
                                            self.pr_type,
                                        ], spacing=2
                                    ),
                                    ft.Row(controls=[self.pr_sequence, self.pr_quarter]),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['class'], size=11, color='grey'),
                                            self.pr_class
                                        ], spacing=2
                                    ),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    self.pr_print_class_bt,
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.Row([self.pr_construction], alignment=ft.MainAxisAlignment.CENTER),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.Row([self.pr_text], alignment=ft.MainAxisAlignment.CENTER),
                                    ft.Row(
                                        expand=True,
                                        controls=[
                                            ft.Stack(
                                                alignment=ft.alignment.center, expand=True,
                                                controls=[self.pr_ring, self.pr_download_report_bt]
                                            )
                                        ], alignment=ft.MainAxisAlignment.CENTER
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

        self.on_mount()

    @staticmethod
    def create_pdf_fonts():
        pdfmetrics.registerFont(TTFont('vinci sans medium', "assets/fonts/vinci_sans_medium.ttf"))
        pdfmetrics.registerFont(TTFont('vinci sans regular', "assets/fonts/vinci_sans_regular.ttf"))
        pdfmetrics.registerFont(TTFont('vinci sans bold', "assets/fonts/vinci_sans_bold.ttf"))
        pdfmetrics.registerFont(TTFont('calibri', "assets/fonts/vinci_sans_regular.ttf"))
        pdfmetrics.registerFont(TTFont('calibri italic', "assets/fonts/vinci_sans_italic.ttf"))
        pdfmetrics.registerFont(TTFont('calibri bold', "assets/fonts/vinci_sans_bold.ttf"))
        pdfmetrics.registerFont(TTFont('calibri z', "assets/fonts/vinci_sans_regular.ttf"))
        # pdfmetrics.registerFont(TTFont('Poppins SemiBold', "assets/fonts/Poppins-SemiBold.ttf"))
        # pdfmetrics.registerFont(TTFont('Poppins Bold', "assets/fonts/Poppins-Bold.ttf"))

    async def build_main_view(self):
        self.content.controls.clear()
        for widget in (self.main_window, self.details_window, self.pr_window):
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
        year_id = self.cp.year_id
        access_token = self.cp.page.client_storage.get('access_token')

        # others...
        classes = await get_all_classes_basic_info(access_token)
        for item in classes:
            self.pr_class.options.append(
                ft.dropdown.Option(
                    key=item['id'], text=item['code']
                )
            )

        # Datatable...
        datas = await get_sequence_averages_with_details(access_token, year_id)

        nb_success = 0
        nb_fails = 0

        self.table.rows.clear()

        for i, item in enumerate(datas):
            # if i == 0:
            #     for clef in item.keys():
            #         print(f"{clef}: {item[clef]}")

            if item['value'] >= 10:
                status_icon = ColoredIcon(ft.Icons.CHECK_CIRCLE, 'teal', 'teal50')
                nb_success += 1
            else:
                status_icon = ColoredIcon(ft.Icons.CLOSE, 'red', 'red50')
                nb_fails += 1

            count_sup = 0
            for element in datas:
                if element['class_code'] == item['class_code'] and element['sequence'] == item['sequence']:
                    if element['value'] > item['value']:
                        count_sup += 1

            rang = count_sup + 1

            new_data: dict = {'rang': rang}
            for clef in item.keys():
                new_data[clef] = item[clef]

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item['student_name']} {item['student_surname']}".upper())),
                        ft.DataCell(ft.Text(f"{item['class_code']}")),
                        ft.DataCell(ft.Text(f"{item['sequence']}")),
                        ft.DataCell(ft.Text(f"{item['points']}")),
                        ft.DataCell(ft.Text(f"{item['total_coefficient']}")),
                        ft.DataCell(ft.Text(f"{item['value']:.2f}")),
                        ft.DataCell(status_icon),
                        ft.DataCell(ft.Text(f"{rang}")),
                        ft.DataCell(
                            MyMiniIcon(
                                ft.Icons.FORMAT_LIST_BULLETED_OUTLINED,
                                languages[self.lang]['details'], 'grey', new_data, self.open_details_window
                            )
                        )
                    ]
                )
            )

        self.nb_success.value = add_separator(nb_success)
        self.nb_fails.value = add_separator(nb_fails)

        if nb_success / len(datas) < 1:
            self.success_rate.value = f"{(nb_success * 100 / len(datas)):.2f} %"
        else:
            self.success_rate.value = f"{(nb_success * 100 / len(datas)):.0f} %"

        await self.build_main_view()

    async def filter_datas(self, e):
        year_id = self.cp.year_id
        access_token = self.cp.page.client_storage.get('access_token')
        datas = await get_sequence_averages_with_details(access_token, year_id)

        nb_success = 0
        nb_fails = 0

        search = self.search.value.lower() if self.search.value else ''
        filtered_datas = list(filter(
            lambda x: search in x['student_name'].lower() or
                      search in x['student_surname'].lower() or
                      search in x['class_code'].lower(), datas
        ))
        self.table.rows.clear()

        for item in filtered_datas:

            if item['value'] >= 10:
                status_icon = ColoredIcon(ft.Icons.CHECK_CIRCLE, 'teal', 'teal50')
                nb_success += 1
            else:
                status_icon = ColoredIcon(ft.Icons.CLOSE, 'red', 'red50')
                nb_fails += 1

            count_sup = 0
            for element in datas:
                if element['class_code'] == item['class_code']:
                    if element['value'] > item['value']:
                        count_sup += 1

            rang = count_sup + 1

            new_data: dict = {'rang': rang}
            for clef in item.keys():
                new_data[clef] = item[clef]

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item['student_name']} {item['student_surname']}".upper())),
                        ft.DataCell(ft.Text(f"{item['class_code']}")),
                        ft.DataCell(ft.Text(f"{item['sequence']}")),
                        ft.DataCell(ft.Text(f"{item['points']}")),
                        ft.DataCell(ft.Text(f"{item['total_coefficient']}")),
                        ft.DataCell(ft.Text(f"{item['value']:.2f}")),
                        ft.DataCell(status_icon),
                        ft.DataCell(ft.Text(f"{rang}")),
                        ft.DataCell(
                            MyMiniIcon(
                                ft.Icons.FORMAT_LIST_BULLETED_OUTLINED,
                                languages[self.lang]['details'], 'grey', new_data, self.open_details_window
                            )
                        )
                    ]
                )
            )

        self.cp.page.update()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    async def load_details_by_student(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        self.det_image.foreground_image_src = e.control.data['student_image']
        self.det_name.value = e.control.data['student_name']
        self.det_surname.value = e.control.data['student_surname']
        self.det_sequence.value = languages[self.lang][e.control.data['sequence']]
        self.det_rang.value = e.control.data['rang']
        self.det_class.value = e.control.data['class_code']
        self.det_rating.value = get_rating(e.control.data['value'])
        self.det_moyenne.value = f"{e.control.data['value']:.2f}"
        self.cp.page.update()

        self.show_one_window(self.details_window)

        details_notes = await get_student_subject_stats(
            access_token, e.control.data['student_id'], e.control.data['sequence'], year_id
        )

        # on met sur le bouton les différentes data à imprimer
        print_dico_data: dict = dict()

        other_datas = await get_student_sequence_detail(
            access_token, e.control.data['student_id'], e.control.data['sequence'], year_id
        )

        print_dico_data['other datas'] = other_datas  # un dictionnaire
        print_dico_data['details notes'] = details_notes  # liste de dictionnaires
        self.bt_print_report.data = print_dico_data


        # on remplit la table des notes...
        self.det_table.rows.clear()
        for item in details_notes:

            if item['student_note'] >= 15:
                status_color= ft.Colors.LIGHT_GREEN
                status_icon = ft.Icons.RECOMMEND_ROUNDED
            elif item['student_note'] <= 7:
                status_color = 'red'
                status_icon = ft.Icons.MOOD_BAD_ROUNDED
            else:
                status_color = None
                status_icon = None

            self.det_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item['subject_short_name']}")),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.Text(f"{item['student_note']}"),
                                    ft.Icon(status_icon, color=status_color, size=16)
                                ], spacing=3
                            )
                        ),
                        ft.DataCell(ft.Text(f"{item['subject_coefficient']}")),
                        ft.DataCell(ft.Text(f"{item['total_score']:.2f}")),
                        ft.DataCell(ft.Text(f"{item['rating']}")),
                    ]
                )
            )

        self.bt_print_report.visible = True
        self.load_text.visible = False
        self.load_bar.visible = False
        self.cp.page.update()

    def open_details_window(self, e):
        self.run_async_in_thread(self.load_details_by_student(e))

    def close_details_window(self, e):
        self.det_table.rows.clear()
        self.bt_print_report.visible = False
        self.load_bar.visible = True
        self.load_text.visible = True
        self.hide_one_window(self.details_window)

    def download_report_book_second_cycle(self, e):
        buffer = io.BytesIO()
        can = Canvas(buffer, pagesize=A4)

        gauche, droite, y = 4.25, 17.25, 28

        self.create_pdf_fonts()
        other_datas = e.control.data['other datas']
        details_notes: list = e.control.data['details notes']
        year_short = self.cp.year_short

        def draw_headers():
            # on commence par les entêtes du bulletin...
            def draw_headers_left():
                # A gauche
                can.setFillColorRGB(0, 0, 0)
                can.setFont("calibri bold", 10)
                can.drawCentredString(gauche * cm, 28.5 * cm, school_republic_fr.upper())
                can.setFont("calibri z", 9)
                can.drawCentredString(gauche * cm, 28.1 * cm, national_devise_fr.upper())
                can.setFont("calibri", 9)
                can.drawCentredString(gauche * cm, 27.7 * cm, "*************")
                can.setFont("calibri", 9)
                can.drawCentredString(gauche * cm, 27.3 * cm, school_delegation_fr.upper())
                can.setFont("calibri", 9)
                can.drawCentredString(gauche * cm, 26.9 * cm, school_name_fr.upper())

            def draw_headers_right():
                # droite
                can.setFillColorRGB(0, 0, 0)
                can.setFont("calibri bold", 10)
                can.drawCentredString(droite * cm, 28.5 * cm, school_republic_en.upper())
                can.setFont("calibri z", 9)
                can.drawCentredString(droite * cm, 28.1 * cm, national_devise_en.upper())
                can.setFont("calibri", 9)
                can.drawCentredString(droite * cm, 27.7 * cm, "*************")
                can.setFont("calibri", 9)
                can.drawCentredString(droite * cm, 27.3 * cm, school_delegation_en.upper())
                can.setFont("calibri", 9)
                can.drawCentredString(droite * cm, 26.9 * cm, school_name_en.upper())

            def draw_school_logo():
                logo_response = requests.get(logo_url)
                image = ImageReader(io.BytesIO(logo_response.content))
                image_width, image_height = 3.5 * cm, 3.5 * cm
                can.drawImage(image, 9 * cm, 26 * cm, width=image_width, height=image_height)

            def draw_year_and_sequence():
                can.setFont("calibri bold", 15)
                can.setFillColorRGB(0, 0, 0)
                can.drawCentredString(
                    10.5 * cm, 25.6 * cm,
                    f"{languages[self.lang]['report card']} - {other_datas['sequence_name']}".upper()
                )

                can.setFont("calibri", 12)
                can.setFillColorRGB(0, 0, 0)
                can.drawCentredString(
                    10.5 * cm, 25.1 * cm,
                    f"{languages[self.lang]['academic year']} {year_short - 1} / {year_short}"
                )

            # on execute les fonctions...
            draw_headers_left()
            draw_headers_right()
            draw_school_logo()
            draw_year_and_sequence()

            # infos sur l'élève ...
            def draw_student_lines():
                # Lignes horizontales
                # 1ere ligne
                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                can.line(4 * cm, 24.6 * cm, 20 * cm, 24.6 * cm)

                # Lignes du milieu
                can.line(4 * cm, 23.9 * cm, 20 * cm, 23.9 * cm)
                can.line(4 * cm, 23.2 * cm, 20 * cm, 23.2 * cm)
                can.line(4 * cm, 22.5 * cm, 16 * cm, 22.5 * cm)

                # Dernière ligne
                can.line(4 * cm, 21.3 * cm, 20 * cm, 21.3 * cm)

                # Lignes verticales
                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                # 1ere ligne
                can.line(4 * cm, 24.6 * cm, 4 * cm, 21.3 * cm)

                can.line(11 * cm, 23.2 * cm, 11 * cm, 22.5 * cm)
                can.line(13.5 * cm, 23.9 * cm, 13.5 * cm, 23.2 * cm)
                can.line(16 * cm, 24.6 * cm, 16 * cm, 21.3 * cm)

                # Dernière ligne
                can.line(20 * cm, 24.6 * cm, 20 * cm, 21.3 * cm)

            def draw_student_informations():
                def draw_student_image():
                    if other_datas['image_url']:
                        image_response = requests.get(other_datas['image_url'])
                        image = ImageReader(io.BytesIO(image_response.content))
                        image_width, image_height = 2.5 * cm, 2.5 * cm
                        can.drawImage(image, 1 * cm, 22 * cm, width=image_width, height=image_height)

                draw_student_image()

                # champs d'informations
                can.setFont("calibri", 10)
                can.drawString(4.2 * cm, 24.1 * cm, "Nom de l'élève:")
                can.drawString(16.2 * cm, 24.1 * cm, "Classe:")
                can.drawString(4.2 * cm, 23.4 * cm, "Date et lieu de naissance:")
                can.drawString(13.8 * cm, 23.4 * cm, "Genre:")
                can.drawString(16.2 * cm, 23.4 * cm, "Effectif:")
                can.setFillColorRGB(1, 0, 0)
                can.drawString(4.2 * cm, 22.7 * cm, "Identifiant unique:")
                can.setFillColorRGB(0, 0, 0)
                can.drawString(11.2 * cm, 22.7 * cm, "Redoublant: oui          non")
                can.drawString(16.2 * cm, 22.7 * cm, "Professeur principal:")
                can.setFillColorRGB(0, 0, 0)
                can.drawString(4.2 * cm, 22 * cm, "Noms et contact des parents/tuteurs:")

                # remplissage des informations
                can.setFont("calibri bold", 11)
                can.setFillColorRGB(0, 0, 0)
                can.drawString(6.7 * cm, 24.1 * cm, f"{other_datas['student_name']} {other_datas['student_surname'].capitalize()}")  # Nom et prénom élève...
                can.drawString(17.4 * cm, 24.1 * cm, f"{other_datas['class_code']}")  # classe...
                can.drawString(8 * cm, 23.4 * cm, f"{convertir_date(str(other_datas['birth_date']))} à {other_datas['birth_place']}")  # Date et lieu de naissance
                can.drawString(15.2 * cm, 23.4 * cm, f"{other_datas['student_gender']}")  # sexe
                can.drawString(17.8 * cm, 23.4 * cm, f"{other_datas['class_size']}")  # Effectif
                can.drawString(4.2 * cm, 21.5 * cm, f"{other_datas['father'].capitalize()} / {other_datas['contact']}")  # Contact parents
                #on trouve le prof titulaire...
                can.drawString(16.2 * cm, 22.3 * cm, f"{other_datas['head_teacher_name']}")  # Nom professeur...
                can.drawString(16.2 * cm, 21.9 * cm, f"{other_datas['head_teacher_surname']}")  # prénom Professeur...

            draw_student_lines()
            draw_student_informations()

        def draw_footer():
            # Pied de page
            foot = (f"Bulletin / {year_short - 1}-{year_short} / {other_datas['sequence_name']} / " 
                    f"{other_datas['student_name']} {other_datas['student_surname']}"
            ).upper()
            can.setFont("calibri", 8)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(10.5 * cm, 0.5 * cm, foot)

        # on exécute les fonctions...
        draw_headers()
        draw_footer()

        # divisions pour les lignes horizontales
        b1, b2, b3, b4, b5, b6, b7, b8, = 1, 10, 11.5, 12.5, 14, 15, 17, 20

        # divisions pour les lignes verticales
        m1 = (b1 + b2) / 2
        m2 = (b2 + b3) / 2
        m3 = (b3 + b4) / 2
        m4 = (b4 + b5) / 2
        m5 = (b5 + b6) / 2
        m6 = (b6 + b7) / 2
        m7 = (b7 + b8) / 2

        def draw_titles():
            can.setStrokeColorRGB(0.3, 0.3, 0.3)

            # Lignes horizontales
            can.line(1 * cm, 21 * cm, 20 * cm, 21 * cm)
            can.line(1 * cm, 20.4 * cm, 20 * cm, 20.4 * cm)

            # Lignes verticales
            can.line(b1 * cm, 20.4 * cm, b1 * cm, 21 * cm)
            can.line(b2 * cm, 20.4 * cm, b2 * cm, 21 * cm)
            can.line(b3 * cm, 20.4 * cm, b3 * cm, 21 * cm)
            can.line(b4 * cm, 20.4 * cm, b4 * cm, 21 * cm)
            can.line(b5 * cm, 20.4 * cm, b5 * cm, 21 * cm)
            can.line(b6 * cm, 20.4 * cm, b6 * cm, 21 * cm)
            can.line(b7 * cm, 20.4 * cm, b7 * cm, 21 * cm)
            can.line(b8 * cm, 20.4 * cm, b8 * cm, 21 * cm)

            can.setFont("calibri bold", 10)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(m1 * cm, 20.6 * cm, "Matière")
            can.drawCentredString(m2 * cm, 20.6 * cm, "M/20")
            can.drawCentredString(m3 * cm, 20.6 * cm, "Coef")
            can.drawCentredString(m4 * cm, 20.6 * cm, "M x coef")
            can.drawCentredString(m5 * cm, 20.6 * cm, "Cote")

            can.setFillColorRGB(1, 0, 0)
            can.drawCentredString(m6 * cm, 20.6 * cm, "Min-Max")
            can.drawCentredString(m7 * cm, 20.6 * cm, "Appreciation")
            can.setFillColorRGB(0, 0, 0)

        draw_titles()

        y = 20.6

        group1, group2, group3 = [], [], []
        general_points = 0
        general_coefficients = 0

        # Remplissage des matières dans les groupes
        for row in details_notes:
            if row['subject_group'] == "g1":
                group1.append(
                    {
                        "subject_name": row['subject_name'], "coefficient": row['subject_coefficient'], "student_note": row['student_note'],
                        "total": row['total_score'], "rating": row['rating'], "min_note": row['min_note'],
                        "max_note": row['max_note'],
                    }
                )
            elif row['subject_group'] == 'g2':
                group2.append(
                    {
                        "subject_name": row['subject_name'], "coefficient": row['subject_coefficient'], "student_note": row['student_note'],
                        "total": row['total_score'], "rating": row['rating'], "min_note": row['min_note'],
                        "max_note": row['max_note'],
                    }
                )
            elif row['subject_group'] == 'g3':
                group3.append(
                    {
                        "subject_name": row['subject_name'], "coefficient": row['subject_coefficient'], "student_note": row['student_note'],
                        "total": row['total_score'], "rating": row['rating'], "min_note": row['min_note'],
                        "max_note": row['max_note'],
                    }
                )
            else:
                pass

        subject_groups = []
        group_names = ["1er groupe", "2e groupe", "3e groupe"]

        for i, item in enumerate((group1, group2, group3)):
            if item:
                subject_groups.append(
                    {
                        "group name": group_names[i], "group datas": item
                    }
                )

        # dans le cas où les matières sont divisées en groupe...
        if subject_groups:
            for group in subject_groups:
                print(f"group : {group}")  # group is a dict...
                total_coefficients = 0
                total_points = 0
                moyenne_groupe = 0

                for data in group['group datas']:  # data is a list...
                    print(data)
                    can.setFillColorRGB(0, 0, 0)
                    can.setFont("calibri", 10)
                    can.drawCentredString(m1 * cm, (y - 0.6) * cm, f"{data['subject_name']}")
                    can.drawCentredString(m3 * cm, (y - 0.6) * cm, f"{data['coefficient']}")
                    can.drawCentredString(m4 * cm, (y - 0.6) * cm, f"{write_number(data['total'])}")

                    if "D" in data['rating']:
                        can.setFillColorRGB(1, 0, 0)
                    elif "A" in data['rating']:
                        can.setFillColorRGB(0, 0.48, 0.22)
                    else:
                        can.setFillColorRGB(0, 0, 0)

                    can.drawCentredString(m5 * cm, (y - 0.6) * cm, f"{data['rating']}")
                    can.drawCentredString(m2 * cm, (y - 0.6) * cm, f"{write_number(data['student_note'])}")
                    can.setFillColorRGB(0, 0, 0)
                    can.drawCentredString(m6 * cm, (y - 0.6) * cm,
                                          f"{write_number(data['min_note'])} - {write_number(data['max_note'])}")

                    can.setStrokeColorRGB(0.3, 0.3, 0.3)
                    can.line(1 * cm, (y - 0.8) * cm, 20 * cm, (y - 0.8) * cm)
                    total_points += data['total']
                    total_coefficients += data['coefficient']

                    # Lignes verticales
                    can.line(b1 * cm, (y - 0.7) * cm, b1 * cm, (y - 0) * cm)
                    can.line(b2 * cm, (y - 0.7) * cm, b2 * cm, (y - 0) * cm)
                    can.line(b3 * cm, (y - 0.7) * cm, b3 * cm, (y - 0) * cm)
                    can.line(b4 * cm, (y - 0.7) * cm, b4 * cm, (y - 0) * cm)
                    can.line(b5 * cm, (y - 0.7) * cm, b5 * cm, (y - 0) * cm)
                    can.line(b6 * cm, (y - 0.7) * cm, b6 * cm, (y - 0) * cm)
                    can.line(b7 * cm, (y - 0.7) * cm, b7 * cm, (y - 0) * cm)
                    can.line(b8 * cm, (y - 0.7) * cm, b8 * cm, (y - 0) * cm)

                    y -= 0.7

                print(group['group name'])
                print(total_points)
                print(total_coefficients)

                can.setFont("calibri bold", 10)
                can.setFillColorRGB(0, 0, 0)
                can.drawCentredString(m1 * cm, (y - 0.6) * cm, f"Total {group['group name']}")

                can.setFont("calibri bold", 10)
                can.setFillColorRGB(0, 0, 0)
                can.drawCentredString(m3 * cm, (y - 0.6) * cm, f"{total_coefficients}")
                can.drawCentredString(m4 * cm, (y - 0.6) * cm, f"{write_number(total_points)}")

                moyenne_groupe = write_number(total_points / total_coefficients)
                can.setFillColorRGB(0, 0, 0)
                can.drawCentredString(m7 * cm, (y - 0.6) * cm, f"{moyenne_groupe}/20")

                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                can.line(1 * cm, (y - 0.8) * cm, 20 * cm, (y - 0.8) * cm)

                can.line(b1 * cm, (y - 0.8) * cm, b1 * cm, (y - 0) * cm)
                can.line(b2 * cm, (y - 0.8) * cm, b2 * cm, (y - 0) * cm)
                can.line(b3 * cm, (y - 0.8) * cm, b3 * cm, (y - 0) * cm)
                can.line(b4 * cm, (y - 0.8) * cm, b4 * cm, (y - 0) * cm)
                can.line(b5 * cm, (y - 0.8) * cm, b5 * cm, (y - 0) * cm)
                can.line(b6 * cm, (y - 0.8) * cm, b6 * cm, (y - 0) * cm)
                can.line(b7 * cm, (y - 0.8) * cm, b7 * cm, (y - 0) * cm)
                can.line(b8 * cm, (y - 0.8) * cm, b8 * cm, (y - 0) * cm)

                y -= 0.7

        # Dans le cas contraire...
        else:
            for subject in details_notes:
                can.setFont("calibri", 10)
                can.drawCentredString(m1 * cm, (y - 0.6) * cm, f"{subject['subject_name']}")
                can.drawCentredString(m3 * cm, (y - 0.6) * cm, f"{subject['subject_coefficient']}")
                can.drawCentredString(m4 * cm, (y - 0.6) * cm, f"{write_number(subject['total_score'])}")

                if "D" in subject['rating']:
                    can.setFillColorRGB(1, 0, 0)
                elif "A" in subject['rating']:
                    can.setFillColorRGB(0, 0.48, 0.22)
                else:
                    can.setFillColorRGB(0, 0, 0)

                can.drawCentredString(m5 * cm, (y - 0.6) * cm, f"{subject['rating']}")
                can.drawCentredString(m2 * cm, (y - 0.6) * cm, f"{write_number(subject['student_note'])}")
                can.setFillColorRGB(0, 0, 0)
                can.drawCentredString(m6 * cm, (y - 0.6) * cm,
                                      f"{write_number(subject['min_note'])} - {write_number(subject['max_note'])}")

                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                can.line(1 * cm, (y - 0.8) * cm, 20 * cm, (y - 0.8) * cm)

                # Lignes verticales
                can.line(b1 * cm, (y - 0.7) * cm, b1 * cm, (y - 0) * cm)
                can.line(b2 * cm, (y - 0.7) * cm, b2 * cm, (y - 0) * cm)
                can.line(b3 * cm, (y - 0.7) * cm, b3 * cm, (y - 0) * cm)
                can.line(b4 * cm, (y - 0.7) * cm, b4 * cm, (y - 0) * cm)
                can.line(b5 * cm, (y - 0.7) * cm, b5 * cm, (y - 0) * cm)
                can.line(b6 * cm, (y - 0.7) * cm, b6 * cm, (y - 0) * cm)
                can.line(b7 * cm, (y - 0.7) * cm, b7 * cm, (y - 0) * cm)
                can.line(b8 * cm, (y - 0.7) * cm, b8 * cm, (y - 0) * cm)

                y -= 0.7


        # Finalisation des statistiques
        y = y - 1

        # Statistiques de l'élève au bas des notes...
        def draw_recap():
            can.setStrokeColorRGB(0.3, 0.3, 0.3)
            can.line(1 * cm, (y + 0.1) * cm, 20 * cm, (y + 0.1) * cm)
            can.line(b1 * cm, (y + 1) * cm, b1 * cm, (y + 0.1) * cm)
            can.line(b3 * cm, (y + 1) * cm, b3 * cm, (y + 0.1) * cm)
            can.line(b4 * cm, (y + 1) * cm, b4 * cm, (y + 0.1) * cm)
            can.line(b5 * cm, (y + 1) * cm, b5 * cm, (y + 0.1) * cm)
            can.line(b7 * cm, (y + 1) * cm, b7 * cm, (y + 0.1) * cm)
            can.line(b8 * cm, (y + 1) * cm, b8 * cm, (y + 0.1) * cm)

            can.setFont("calibri bold", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawRightString((b3 - 0.2) * cm, (y + 0.4) * cm, "TOTAL")
            can.drawRightString((b7 - 0.2) * cm, (y + 0.4) * cm, "MOYENNE")
            can.drawCentredString(m3 * cm, (y + 0.4) * cm, f"{other_datas['student_total_coefficient']}")
            can.drawCentredString(m4 * cm, (y + 0.4) * cm, f"{other_datas['student_points']}")
            can.drawCentredString(m7 * cm, (y + 0.4) * cm, f"{write_number(other_datas['student_average'])}")

        draw_recap()

        # Statistiques
        def draw_cadre_stats():

            # lignes horizontales
            def draw_contours():
                can.setFillColorRGB(0.75, 0.75, 0.75)
                can.line(1 * cm, (y - 0.3) * cm, 20 * cm, (y - 0.3) * cm)
                can.line(1 * cm, (y - 0.9) * cm, 20 * cm, (y - 0.9) * cm)

                # Lignes verticales
                can.line(1 * cm, (y - 0.3) * cm, 1 * cm, (y - 0.9) * cm)
                can.line(7.3 * cm, (y - 0.3) * cm, 7.3 * cm, (y - 0.9) * cm)
                can.line(13.6 * cm, (y - 0.3) * cm, 13.6 * cm, (y - 0.9) * cm)
                can.line(20 * cm, (y - 0.3) * cm, 20 * cm, (y - 0.9) * cm)

                # cadre stats divisons principales
                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                can.line(1 * cm, (y - 0.3) * cm, 1 * cm, (y - 6) * cm)
                can.line(7.3 * cm, (y - 0.3) * cm, 7.3 * cm, (y - 6) * cm)
                can.line(13.6 * cm, (y - 0.3) * cm, 13.6 * cm, (y - 6) * cm)
                can.line(20 * cm, (y - 0.3) * cm, 20 * cm, (y - 6) * cm)
                can.line(1 * cm, (y - 4) * cm, 20 * cm, (y - 4) * cm)
                can.line(1 * cm, (y - 6) * cm, 20 * cm, (y - 6) * cm)

                # divisons verticales secondaires
                # Discipline
                can.line(3.15 * cm, (y - 0.9) * cm, 3.15 * cm, (y - 4) * cm)
                can.line(4.15 * cm, (y - 0.9) * cm, 4.15 * cm, (y - 4) * cm)
                can.line(6.3 * cm, (y - 0.9) * cm, 6.3 * cm, (y - 4) * cm)
                # Travail de l'élève
                can.line(9.3 * cm, (y - 0.9) * cm, 9.3 * cm, (y - 4) * cm)
                can.line(10.8 * cm, (y - 0.9) * cm, 10.8 * cm, (y - 4) * cm)
                can.line(12.8 * cm, (y - 1.675) * cm, 12.8 * cm, (y - 4) * cm)
                can.line(12.8 * cm, (y - 1.675) * cm, 12.8 * cm, (y - 4) * cm)
                # Profil
                can.line(17 * cm, (y - 0.9) * cm, 17 * cm, (y - 4) * cm)

                # divisions horizontales secondaire
                can.line(1 * cm, (y - 1.675) * cm, 20 * cm, (y - 1.675) * cm)
                can.line(1 * cm, (y - 2.45) * cm, 20 * cm, (y - 2.45) * cm)
                can.line(1 * cm, (y - 3.225) * cm, 20 * cm, (y - 3.225) * cm)

                can.line(10.8 * cm, (y - 2.0125) * cm, 13.6 * cm, (y - 2.0125) * cm)
                can.line(10.8 * cm, (y - 2.7875) * cm, 13.6 * cm, (y - 2.7875) * cm)

                # divisons horizontales tertiares

                can.setFont("calibri", 9)
                can.setFillColorRGB(0, 0, 0)
                can.drawString(1.2 * cm, (y - 1.375) * cm, "Abs non J.")
                can.drawString(1.2 * cm, (y - 1.375) * cm, "Abs non J. (h)")
                can.drawString(1.2 * cm, (y - 2.15) * cm, "Abs just. (h)")
                can.drawString(1.2 * cm, (y - 2.925) * cm, "Retards (nb) ")
                can.drawString(1.2 * cm, (y - 3.7) * cm, "Consignes (h) ")
                can.drawString(4.21 * cm, (y - 1.375) * cm, "Avertissement")
                can.drawString(4.21 * cm, (y - 2.15) * cm, "Blâme")
                can.drawString(4.21 * cm, (y - 2.925) * cm, f"Exclusions (j)")
                can.drawString(4.21 * cm, (y - 3.7) * cm, f"Exclusion (def)")

            draw_contours()

            # remplissage sanctions...
            can.setFont("calibri bold", 10)
            abs_nj = other_datas['unjustified_absence_count']
            abs_jus = other_datas['justified_absence_count']
            avert = other_datas['warning_count']
            blame = other_datas['reprimand_count']
            consigne = other_datas['detention_count']
            exclusion = other_datas['ban_count']
            exclu_def = other_datas['permanent_ban_count']
            retard = other_datas['late_count']

            can.drawCentredString(3.65 * cm, (y - 1.375) * cm, f"{abs_nj}")
            can.drawCentredString(3.65 * cm, (y - 2.15) * cm, f"{abs_jus}")
            can.drawCentredString(3.65 * cm, (y - 2.925) * cm, f"{retard}")
            can.drawCentredString(3.65 * cm, (y - 3.7) * cm, f"{consigne}")
            can.drawCentredString(6.8 * cm, (y - 1.375) * cm, f"{avert}")
            can.drawCentredString(6.8 * cm, (y - 2.15) * cm, f"{blame}")
            can.drawCentredString(6.8 * cm, (y - 2.925) * cm, f"{exclusion}")
            can.drawCentredString(6.8 * cm, (y - 3.7) * cm, f"{exclu_def}")

            # travail de l'élève
            can.setFont("calibri", 10)
            can.drawString(7.5 * cm, (y - 1.375) * cm, "Total Gén.".upper())
            can.drawString(7.5 * cm, (y - 2.15) * cm, "Coef".upper())
            can.drawString(7.5 * cm, (y - 2.925) * cm, "Moyenne".upper())
            can.drawString(7.5 * cm, (y - 3.7) * cm, f"Cote".upper())

            can.setFont("calibri bold", 10)
            can.drawString(11 * cm, (y - 1.375) * cm, "appreciations.".upper())
            can.setFont("calibri", 8)
            can.drawString(11 * cm, (y - 1.9625) * cm, "CTBA")
            can.drawString(11 * cm, (y - 2.35) * cm, "CBA")
            can.drawString(11 * cm, (y - 2.7375) * cm, "CA")
            can.drawString(11 * cm, (y - 3.125) * cm, "CMA")
            can.drawString(11 * cm, (y - 3.8125) * cm, "CNA")

            # Remplissage du travail de l'élève
            can.setFont("calibri bold", 11)
            can.drawCentredString(10.05 * cm, (y - 1.375) * cm, f"{write_number(other_datas['student_points'])}")
            can.drawCentredString(10.05 * cm, (y - 2.15) * cm, f"{other_datas['student_total_coefficient']}")
            can.drawCentredString(10.05 * cm, (y - 2.925) * cm, f"{write_number(other_datas['student_average'])}")
            can.drawCentredString(10.05 * cm, (y - 3.7) * cm, f"{get_rating(other_datas['student_average'])}")

            # Profil de la classe
            can.setFont("calibri", 10)
            can.drawString(13.8 * cm, (y - 1.375) * cm, "Moyenne générale")
            can.setFillColorRGB(1, 0, 0)
            can.setFont("calibri bold", 10)
            can.drawString(13.8 * cm, (y - 2.15) * cm, "[Min-Max]")
            can.setFont("calibri", 10)
            can.setFillColorRGB(0, 0, 0)
            can.drawString(13.8 * cm, (y - 2.925) * cm, "Nb de moyennes")
            can.drawString(13.8 * cm, (y - 3.7) * cm, f"Taux de réussite")

            # Remplissage profil
            can.setFont("calibri bold", 11)
            can.drawCentredString(18.5 * cm, (y - 1.375) * cm, f"{write_number(other_datas['class_general_average'])}")
            can.drawCentredString(
                18.5 * cm, (y - 2.15) * cm,
                f"{write_number(other_datas['class_min_average'])} - {write_number(other_datas['class_max_average'])}"
            )
            can.drawCentredString(18.5 * cm, (y - 2.925) * cm, f"{other_datas['class_nb_success']}")
            can.drawCentredString(18.5 * cm, (y - 3.7) * cm, f"{write_number(other_datas['class_success_rate'])} %")

        draw_cadre_stats()

        # Entêtes des stats
        def draw_observations():
            can.setFont("calibri bold", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(4.15 * cm, (y - 0.7) * cm, "Discipline")
            can.drawCentredString(10.45 * cm, (y - 0.7) * cm, "Travail de l'élève")
            can.drawCentredString(17.3 * cm, (y - 0.7) * cm, "Profil de la classe")

            can.setFont("calibri", 9)
            can.drawCentredString(4.15 * cm, (y - 4.4) * cm, "Appréciation du travail de l'élève")
            can.drawCentredString(4.15 * cm, (y - 4.8) * cm, "(Points forts et points à améliorer)")

            can.drawCentredString(8.8 * cm, (y - 4.4) * cm, "Visa du parent /")
            can.drawCentredString(8.8 * cm, (y - 4.8) * cm, "tuteur")

            can.drawCentredString(11.95 * cm, (y - 4.4) * cm, "Nom et visa du")
            can.drawCentredString(11.95 * cm, (y - 4.8) * cm, "professeur titulaire")

            can.drawCentredString(17.3 * cm, (y - 4.4) * cm, "Le chef d'établissement")

        draw_observations()


        # on enregistre le document
        can.save()
        buffer.seek(0)

        # Upload Supabase
        file_path = f"Bulletin_{other_datas['student_name']}_{other_datas['student_surname']}_{other_datas['sequence_name']}_{uuid.uuid4().hex[:6]}.pdf"
        supabase_client.storage.from_(DOCUMENTS_BUCKET).upload(
            path=file_path,
            file=buffer.getvalue(),
            file_options={"content-type": "application/pdf"}
        )
        signed_url_response = supabase_client.storage.from_(DOCUMENTS_BUCKET).create_signed_url(
            file_path, 3600 * 24 * 365
        )
        signed_url = signed_url_response.get("signedURL")
        self.cp.page.launch_url(signed_url)

    def open_pr_window(self, e):
        self.show_one_window(self.pr_window)

    def close_pr_window(self, e):
        self.pr_type.value = " "
        self.pr_class.value = " "
        self.pr_quarter.visible = False
        self.pr_sequence.visible = False
        self.pr_download_report_bt.visible = False
        self.pr_ring.visible = False
        self.pr_text.value = ""
        self.pr_construction.visible = False
        self.hide_one_window(self.pr_window)

    def on_changing_type(self, e):
        if self.pr_type.value == "annual":
            self.pr_quarter.visible = False
            self.pr_sequence.visible = False
            self.cp.page.update()

        elif self.pr_type.value == "quarterly":
            self.pr_quarter.visible = True
            self.pr_sequence.visible = False
            self.cp.page.update()

        elif  self.pr_type.value == "monthly":
            self.pr_quarter.visible = False
            self.pr_sequence.visible = True
            self.cp.page.update()

        else:
            self.pr_quarter.visible = False
            self.pr_sequence.visible = False
            self.cp.page.update()

    async def load_report_file(self, e):

        # Variables utiles
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id
        year_short = self.cp.year_short

        # si le type de bulletin est non nul...
        if self.pr_type.value != " ":
            print(f"cas 1: --- Type est non nul ---")
            # Bulletin mensuel...
            if self.pr_type.value == "monthly":
                print(f"cas 1.1: --- types est égal à monthly ---")
                if self.pr_sequence.value != " ":
                    print(f"cas 1.1.1: ---sequence est non nul ---")
                    selected_class = self.pr_class.value
                    selected_sequence = self.pr_sequence.value

                    # on trouve tous les id des élèves de la classe...
                    all_student_ids = await get_all_students_id_by_class(access_token, selected_class, year_id)

                    # Création du fichier pdf...
                    buffer = io.BytesIO()
                    can = Canvas(buffer, pagesize=A4)

                    self.create_pdf_fonts()

                    self.pr_construction.visible = True
                    self.pr_construction.update()
                    # on affiche le ring...
                    self.pr_ring.visible = True
                    self.pr_ring.update()
                    count = 0

                    for row in all_student_ids:
                        details_notes = await get_student_subject_stats(
                            access_token, row['student_id'], selected_sequence, year_id
                        )
                        other_datas = await get_student_sequence_detail(
                            access_token, row['student_id'], selected_sequence, year_id
                        )
                        gauche, droite, y = 4.25, 17.25, 28

                        # Affichage du dialogue
                        count += 1
                        self.pr_text.value = f"{count}/{len(all_student_ids)} Construction du bulletin de {other_datas['student_name']} {other_datas['student_surname']}"
                        self.pr_text.update()

                        def draw_headers():
                            # on commence par les entêtes du bulletin...
                            def draw_headers_left():
                                # A gauche
                                can.setFillColorRGB(0, 0, 0)
                                can.setFont("calibri bold", 10)
                                can.drawCentredString(gauche * cm, 28.5 * cm, school_republic_fr.upper())
                                can.setFont("calibri z", 9)
                                can.drawCentredString(gauche * cm, 28.1 * cm, national_devise_fr.upper())
                                can.setFont("calibri", 9)
                                can.drawCentredString(gauche * cm, 27.7 * cm, "*************")
                                can.setFont("calibri", 9)
                                can.drawCentredString(gauche * cm, 27.3 * cm, school_delegation_fr.upper())
                                can.setFont("calibri", 9)
                                can.drawCentredString(gauche * cm, 26.9 * cm, school_name_fr.upper())

                            def draw_headers_right():
                                # droite
                                can.setFillColorRGB(0, 0, 0)
                                can.setFont("calibri bold", 10)
                                can.drawCentredString(droite * cm, 28.5 * cm, school_republic_en.upper())
                                can.setFont("calibri z", 9)
                                can.drawCentredString(droite * cm, 28.1 * cm, national_devise_en.upper())
                                can.setFont("calibri", 9)
                                can.drawCentredString(droite * cm, 27.7 * cm, "*************")
                                can.setFont("calibri", 9)
                                can.drawCentredString(droite * cm, 27.3 * cm, school_delegation_en.upper())
                                can.setFont("calibri", 9)
                                can.drawCentredString(droite * cm, 26.9 * cm, school_name_en.upper())

                            def draw_school_logo():
                                logo_response = requests.get(logo_url)
                                image = ImageReader(io.BytesIO(logo_response.content))
                                image_width, image_height = 3.5 * cm, 3.5 * cm
                                can.drawImage(image, 9 * cm, 26 * cm, width=image_width, height=image_height)

                            def draw_year_and_sequence():
                                can.setFont("calibri bold", 15)
                                can.setFillColorRGB(0, 0, 0)
                                can.drawCentredString(
                                    10.5 * cm, 25.6 * cm,
                                    f"{languages[self.lang]['report card']} - {other_datas['sequence_name']}".upper()
                                )

                                can.setFont("calibri", 12)
                                can.setFillColorRGB(0, 0, 0)
                                can.drawCentredString(
                                    10.5 * cm, 25.1 * cm,
                                    f"{languages[self.lang]['academic year']} {year_short - 1} / {year_short}"
                                )

                            # on execute les fonctions...
                            draw_headers_left()
                            draw_headers_right()
                            draw_school_logo()
                            draw_year_and_sequence()

                            # infos sur l'élève ...
                            def draw_student_lines():
                                # Lignes horizontales
                                # 1ere ligne
                                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                                can.line(4 * cm, 24.6 * cm, 20 * cm, 24.6 * cm)

                                # Lignes du milieu
                                can.line(4 * cm, 23.9 * cm, 20 * cm, 23.9 * cm)
                                can.line(4 * cm, 23.2 * cm, 20 * cm, 23.2 * cm)
                                can.line(4 * cm, 22.5 * cm, 16 * cm, 22.5 * cm)

                                # Dernière ligne
                                can.line(4 * cm, 21.3 * cm, 20 * cm, 21.3 * cm)

                                # Lignes verticales
                                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                                # 1ere ligne
                                can.line(4 * cm, 24.6 * cm, 4 * cm, 21.3 * cm)

                                can.line(11 * cm, 23.2 * cm, 11 * cm, 22.5 * cm)
                                can.line(13.5 * cm, 23.9 * cm, 13.5 * cm, 23.2 * cm)
                                can.line(16 * cm, 24.6 * cm, 16 * cm, 21.3 * cm)

                                # Dernière ligne
                                can.line(20 * cm, 24.6 * cm, 20 * cm, 21.3 * cm)

                            def draw_student_informations():
                                def draw_student_image():
                                    if other_datas['image_url']:
                                        image_response = requests.get(other_datas['image_url'])
                                        image = ImageReader(io.BytesIO(image_response.content))
                                        image_width, image_height = 2.5 * cm, 2.5 * cm
                                        can.drawImage(image, 1 * cm, 22 * cm, width=image_width, height=image_height)

                                draw_student_image()

                                # champs d'informations
                                can.setFont("calibri", 10)
                                can.drawString(4.2 * cm, 24.1 * cm, "Nom de l'élève:")
                                can.drawString(16.2 * cm, 24.1 * cm, "Classe:")
                                can.drawString(4.2 * cm, 23.4 * cm, "Date et lieu de naissance:")
                                can.drawString(13.8 * cm, 23.4 * cm, "Genre:")
                                can.drawString(16.2 * cm, 23.4 * cm, "Effectif:")
                                can.setFillColorRGB(1, 0, 0)
                                can.drawString(4.2 * cm, 22.7 * cm, "Identifiant unique:")
                                can.setFillColorRGB(0, 0, 0)
                                can.drawString(11.2 * cm, 22.7 * cm, "Redoublant: oui          non")
                                can.drawString(16.2 * cm, 22.7 * cm, "Professeur principal:")
                                can.setFillColorRGB(0, 0, 0)
                                can.drawString(4.2 * cm, 22 * cm, "Noms et contact des parents/tuteurs:")

                                # remplissage des informations
                                can.setFont("calibri bold", 11)
                                can.setFillColorRGB(0, 0, 0)
                                can.drawString(6.7 * cm, 24.1 * cm,
                                               f"{other_datas['student_name']} {other_datas['student_surname'].capitalize()}")  # Nom et prénom élève...
                                can.drawString(17.4 * cm, 24.1 * cm, f"{other_datas['class_code']}")  # classe...
                                can.drawString(8 * cm, 23.4 * cm,
                                               f"{convertir_date(str(other_datas['birth_date']))} à {other_datas['birth_place']}")  # Date et lieu de naissance
                                can.drawString(15.2 * cm, 23.4 * cm, f"{other_datas['student_gender']}")  # sexe
                                can.drawString(17.8 * cm, 23.4 * cm, f"{other_datas['class_size']}")  # Effectif
                                can.drawString(4.2 * cm, 21.5 * cm,
                                               f"{other_datas['father'].capitalize()} / {other_datas['contact']}")  # Contact parents
                                # on trouve le prof titulaire...
                                can.drawString(16.2 * cm, 22.3 * cm,
                                               f"{other_datas['head_teacher_name']}")  # Nom professeur...
                                can.drawString(16.2 * cm, 21.9 * cm,
                                               f"{other_datas['head_teacher_surname']}")  # prénom Professeur...

                            draw_student_lines()
                            draw_student_informations()

                        def draw_footer():
                            # Pied de page
                            foot = (f"Bulletin / {year_short - 1}-{year_short} / {other_datas['sequence_name']} / "
                                    f"{other_datas['student_name']} {other_datas['student_surname']}"
                                    ).upper()
                            can.setFont("calibri", 8)
                            can.setFillColorRGB(0, 0, 0)
                            can.drawCentredString(10.5 * cm, 0.5 * cm, foot)

                        # on exécute les fonctions...
                        draw_headers()
                        draw_footer()

                        # divisions pour les lignes horizontales
                        b1, b2, b3, b4, b5, b6, b7, b8, = 1, 10, 11.5, 12.5, 14, 15, 17, 20

                        # divisions pour les lignes verticales
                        m1 = (b1 + b2) / 2
                        m2 = (b2 + b3) / 2
                        m3 = (b3 + b4) / 2
                        m4 = (b4 + b5) / 2
                        m5 = (b5 + b6) / 2
                        m6 = (b6 + b7) / 2
                        m7 = (b7 + b8) / 2

                        def draw_titles():
                            can.setStrokeColorRGB(0.3, 0.3, 0.3)

                            # Lignes horizontales
                            can.line(1 * cm, 21 * cm, 20 * cm, 21 * cm)
                            can.line(1 * cm, 20.4 * cm, 20 * cm, 20.4 * cm)

                            # Lignes verticales
                            can.line(b1 * cm, 20.4 * cm, b1 * cm, 21 * cm)
                            can.line(b2 * cm, 20.4 * cm, b2 * cm, 21 * cm)
                            can.line(b3 * cm, 20.4 * cm, b3 * cm, 21 * cm)
                            can.line(b4 * cm, 20.4 * cm, b4 * cm, 21 * cm)
                            can.line(b5 * cm, 20.4 * cm, b5 * cm, 21 * cm)
                            can.line(b6 * cm, 20.4 * cm, b6 * cm, 21 * cm)
                            can.line(b7 * cm, 20.4 * cm, b7 * cm, 21 * cm)
                            can.line(b8 * cm, 20.4 * cm, b8 * cm, 21 * cm)

                            can.setFont("calibri bold", 10)
                            can.setFillColorRGB(0, 0, 0)
                            can.drawCentredString(m1 * cm, 20.6 * cm, "Matière")
                            can.drawCentredString(m2 * cm, 20.6 * cm, "M/20")
                            can.drawCentredString(m3 * cm, 20.6 * cm, "Coef")
                            can.drawCentredString(m4 * cm, 20.6 * cm, "M x coef")
                            can.drawCentredString(m5 * cm, 20.6 * cm, "Cote")

                            can.setFillColorRGB(1, 0, 0)
                            can.drawCentredString(m6 * cm, 20.6 * cm, "Min-Max")
                            can.drawCentredString(m7 * cm, 20.6 * cm, "Appreciation")
                            can.setFillColorRGB(0, 0, 0)

                        draw_titles()

                        y = 20.6

                        group1, group2, group3 = [], [], []
                        general_points = 0
                        general_coefficients = 0

                        # Remplissage des matières dans les groupes
                        for row in details_notes:
                            if row['subject_group'] == "g1":
                                group1.append(
                                    {
                                        "subject_name": row['subject_name'], "coefficient": row['subject_coefficient'],
                                        "student_note": row['student_note'],
                                        "total": row['total_score'], "rating": row['rating'],
                                        "min_note": row['min_note'],
                                        "max_note": row['max_note'],
                                    }
                                )
                            elif row['subject_group'] == 'g2':
                                group2.append(
                                    {
                                        "subject_name": row['subject_name'], "coefficient": row['subject_coefficient'],
                                        "student_note": row['student_note'],
                                        "total": row['total_score'], "rating": row['rating'],
                                        "min_note": row['min_note'],
                                        "max_note": row['max_note'],
                                    }
                                )
                            elif row['subject_group'] == 'g3':
                                group3.append(
                                    {
                                        "subject_name": row['subject_name'], "coefficient": row['subject_coefficient'],
                                        "student_note": row['student_note'],
                                        "total": row['total_score'], "rating": row['rating'],
                                        "min_note": row['min_note'],
                                        "max_note": row['max_note'],
                                    }
                                )
                            else:
                                pass

                        subject_groups = []
                        group_names = ["1er groupe", "2e groupe", "3e groupe"]

                        for i, item in enumerate((group1, group2, group3)):
                            if item:
                                subject_groups.append(
                                    {
                                        "group name": group_names[i], "group datas": item
                                    }
                                )

                        # dans le cas où les matières sont divisées en groupe...
                        if subject_groups:
                            for group in subject_groups:
                                print(f"group : {group}")  # group is a dict...
                                total_coefficients = 0
                                total_points = 0
                                moyenne_groupe = 0

                                for data in group['group datas']:  # data is a list...
                                    print(data)
                                    can.setFillColorRGB(0, 0, 0)
                                    can.setFont("calibri", 10)
                                    can.drawCentredString(m1 * cm, (y - 0.6) * cm, f"{data['subject_name']}")
                                    can.drawCentredString(m3 * cm, (y - 0.6) * cm, f"{data['coefficient']}")
                                    can.drawCentredString(m4 * cm, (y - 0.6) * cm, f"{write_number(data['total'])}")

                                    if "D" in data['rating']:
                                        can.setFillColorRGB(1, 0, 0)
                                    elif "A" in data['rating']:
                                        can.setFillColorRGB(0, 0.48, 0.22)
                                    else:
                                        can.setFillColorRGB(0, 0, 0)

                                    can.drawCentredString(m5 * cm, (y - 0.6) * cm, f"{data['rating']}")
                                    can.drawCentredString(m2 * cm, (y - 0.6) * cm,
                                                          f"{write_number(data['student_note'])}")
                                    can.setFillColorRGB(0, 0, 0)
                                    can.drawCentredString(m6 * cm, (y - 0.6) * cm,
                                                          f"{write_number(data['min_note'])} - {write_number(data['max_note'])}")

                                    can.setStrokeColorRGB(0.3, 0.3, 0.3)
                                    can.line(1 * cm, (y - 0.8) * cm, 20 * cm, (y - 0.8) * cm)
                                    total_points += data['total']
                                    total_coefficients += data['coefficient']

                                    # Lignes verticales
                                    can.line(b1 * cm, (y - 0.7) * cm, b1 * cm, (y - 0) * cm)
                                    can.line(b2 * cm, (y - 0.7) * cm, b2 * cm, (y - 0) * cm)
                                    can.line(b3 * cm, (y - 0.7) * cm, b3 * cm, (y - 0) * cm)
                                    can.line(b4 * cm, (y - 0.7) * cm, b4 * cm, (y - 0) * cm)
                                    can.line(b5 * cm, (y - 0.7) * cm, b5 * cm, (y - 0) * cm)
                                    can.line(b6 * cm, (y - 0.7) * cm, b6 * cm, (y - 0) * cm)
                                    can.line(b7 * cm, (y - 0.7) * cm, b7 * cm, (y - 0) * cm)
                                    can.line(b8 * cm, (y - 0.7) * cm, b8 * cm, (y - 0) * cm)

                                    y -= 0.7

                                print(group['group name'])
                                print(total_points)
                                print(total_coefficients)

                                can.setFont("calibri bold", 10)
                                can.setFillColorRGB(0, 0, 0)
                                can.drawCentredString(m1 * cm, (y - 0.6) * cm, f"Total {group['group name']}")

                                can.setFont("calibri bold", 10)
                                can.setFillColorRGB(0, 0, 0)
                                can.drawCentredString(m3 * cm, (y - 0.6) * cm, f"{total_coefficients}")
                                can.drawCentredString(m4 * cm, (y - 0.6) * cm, f"{write_number(total_points)}")

                                moyenne_groupe = write_number(total_points / total_coefficients)
                                can.setFillColorRGB(0, 0, 0)
                                can.drawCentredString(m7 * cm, (y - 0.6) * cm, f"{moyenne_groupe}/20")

                                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                                can.line(1 * cm, (y - 0.8) * cm, 20 * cm, (y - 0.8) * cm)

                                can.line(b1 * cm, (y - 0.8) * cm, b1 * cm, (y - 0) * cm)
                                can.line(b2 * cm, (y - 0.8) * cm, b2 * cm, (y - 0) * cm)
                                can.line(b3 * cm, (y - 0.8) * cm, b3 * cm, (y - 0) * cm)
                                can.line(b4 * cm, (y - 0.8) * cm, b4 * cm, (y - 0) * cm)
                                can.line(b5 * cm, (y - 0.8) * cm, b5 * cm, (y - 0) * cm)
                                can.line(b6 * cm, (y - 0.8) * cm, b6 * cm, (y - 0) * cm)
                                can.line(b7 * cm, (y - 0.8) * cm, b7 * cm, (y - 0) * cm)
                                can.line(b8 * cm, (y - 0.8) * cm, b8 * cm, (y - 0) * cm)

                                y -= 0.7

                        # Dans le cas contraire...
                        else:
                            for subject in details_notes:
                                can.setFont("calibri", 10)
                                can.drawCentredString(m1 * cm, (y - 0.6) * cm, f"{subject['subject_name']}")
                                can.drawCentredString(m3 * cm, (y - 0.6) * cm, f"{subject['subject_coefficient']}")
                                can.drawCentredString(m4 * cm, (y - 0.6) * cm,
                                                      f"{write_number(subject['total_score'])}")

                                if "D" in subject['rating']:
                                    can.setFillColorRGB(1, 0, 0)
                                elif "A" in subject['rating']:
                                    can.setFillColorRGB(0, 0.48, 0.22)
                                else:
                                    can.setFillColorRGB(0, 0, 0)

                                can.drawCentredString(m5 * cm, (y - 0.6) * cm, f"{subject['rating']}")
                                can.drawCentredString(m2 * cm, (y - 0.6) * cm,
                                                      f"{write_number(subject['student_note'])}")
                                can.setFillColorRGB(0, 0, 0)
                                can.drawCentredString(m6 * cm, (y - 0.6) * cm,
                                                      f"{write_number(subject['min_note'])} - {write_number(subject['max_note'])}")

                                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                                can.line(1 * cm, (y - 0.8) * cm, 20 * cm, (y - 0.8) * cm)

                                # Lignes verticales
                                can.line(b1 * cm, (y - 0.7) * cm, b1 * cm, (y - 0) * cm)
                                can.line(b2 * cm, (y - 0.7) * cm, b2 * cm, (y - 0) * cm)
                                can.line(b3 * cm, (y - 0.7) * cm, b3 * cm, (y - 0) * cm)
                                can.line(b4 * cm, (y - 0.7) * cm, b4 * cm, (y - 0) * cm)
                                can.line(b5 * cm, (y - 0.7) * cm, b5 * cm, (y - 0) * cm)
                                can.line(b6 * cm, (y - 0.7) * cm, b6 * cm, (y - 0) * cm)
                                can.line(b7 * cm, (y - 0.7) * cm, b7 * cm, (y - 0) * cm)
                                can.line(b8 * cm, (y - 0.7) * cm, b8 * cm, (y - 0) * cm)

                                y -= 0.7

                        # Finalisation des statistiques
                        y = y - 1

                        # Statistiques de l'élève au bas des notes...
                        def draw_recap():
                            can.setStrokeColorRGB(0.3, 0.3, 0.3)
                            can.line(1 * cm, (y + 0.1) * cm, 20 * cm, (y + 0.1) * cm)
                            can.line(b1 * cm, (y + 1) * cm, b1 * cm, (y + 0.1) * cm)
                            can.line(b3 * cm, (y + 1) * cm, b3 * cm, (y + 0.1) * cm)
                            can.line(b4 * cm, (y + 1) * cm, b4 * cm, (y + 0.1) * cm)
                            can.line(b5 * cm, (y + 1) * cm, b5 * cm, (y + 0.1) * cm)
                            can.line(b7 * cm, (y + 1) * cm, b7 * cm, (y + 0.1) * cm)
                            can.line(b8 * cm, (y + 1) * cm, b8 * cm, (y + 0.1) * cm)

                            can.setFont("calibri bold", 11)
                            can.setFillColorRGB(0, 0, 0)
                            can.drawRightString((b3 - 0.2) * cm, (y + 0.4) * cm, "TOTAL")
                            can.drawRightString((b7 - 0.2) * cm, (y + 0.4) * cm, "MOYENNE")
                            can.drawCentredString(m3 * cm, (y + 0.4) * cm,
                                                  f"{other_datas['student_total_coefficient']}")
                            can.drawCentredString(m4 * cm, (y + 0.4) * cm, f"{other_datas['student_points']}")
                            can.drawCentredString(m7 * cm, (y + 0.4) * cm,
                                                  f"{write_number(other_datas['student_average'])}")

                        draw_recap()

                        # Statistiques
                        def draw_cadre_stats():

                            # lignes horizontales
                            def draw_contours():
                                can.setFillColorRGB(0.75, 0.75, 0.75)
                                can.line(1 * cm, (y - 0.3) * cm, 20 * cm, (y - 0.3) * cm)
                                can.line(1 * cm, (y - 0.9) * cm, 20 * cm, (y - 0.9) * cm)

                                # Lignes verticales
                                can.line(1 * cm, (y - 0.3) * cm, 1 * cm, (y - 0.9) * cm)
                                can.line(7.3 * cm, (y - 0.3) * cm, 7.3 * cm, (y - 0.9) * cm)
                                can.line(13.6 * cm, (y - 0.3) * cm, 13.6 * cm, (y - 0.9) * cm)
                                can.line(20 * cm, (y - 0.3) * cm, 20 * cm, (y - 0.9) * cm)

                                # cadre stats divisons principales
                                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                                can.line(1 * cm, (y - 0.3) * cm, 1 * cm, (y - 6) * cm)
                                can.line(7.3 * cm, (y - 0.3) * cm, 7.3 * cm, (y - 6) * cm)
                                can.line(13.6 * cm, (y - 0.3) * cm, 13.6 * cm, (y - 6) * cm)
                                can.line(20 * cm, (y - 0.3) * cm, 20 * cm, (y - 6) * cm)
                                can.line(1 * cm, (y - 4) * cm, 20 * cm, (y - 4) * cm)
                                can.line(1 * cm, (y - 6) * cm, 20 * cm, (y - 6) * cm)

                                # divisons verticales secondaires
                                # Discipline
                                can.line(3.15 * cm, (y - 0.9) * cm, 3.15 * cm, (y - 4) * cm)
                                can.line(4.15 * cm, (y - 0.9) * cm, 4.15 * cm, (y - 4) * cm)
                                can.line(6.3 * cm, (y - 0.9) * cm, 6.3 * cm, (y - 4) * cm)
                                # Travail de l'élève
                                can.line(9.3 * cm, (y - 0.9) * cm, 9.3 * cm, (y - 4) * cm)
                                can.line(10.8 * cm, (y - 0.9) * cm, 10.8 * cm, (y - 4) * cm)
                                can.line(12.8 * cm, (y - 1.675) * cm, 12.8 * cm, (y - 4) * cm)
                                can.line(12.8 * cm, (y - 1.675) * cm, 12.8 * cm, (y - 4) * cm)
                                # Profil
                                can.line(17 * cm, (y - 0.9) * cm, 17 * cm, (y - 4) * cm)

                                # divisions horizontales secondaire
                                can.line(1 * cm, (y - 1.675) * cm, 20 * cm, (y - 1.675) * cm)
                                can.line(1 * cm, (y - 2.45) * cm, 20 * cm, (y - 2.45) * cm)
                                can.line(1 * cm, (y - 3.225) * cm, 20 * cm, (y - 3.225) * cm)

                                can.line(10.8 * cm, (y - 2.0125) * cm, 13.6 * cm, (y - 2.0125) * cm)
                                can.line(10.8 * cm, (y - 2.7875) * cm, 13.6 * cm, (y - 2.7875) * cm)

                                # divisons horizontales tertiares

                                can.setFont("calibri", 9)
                                can.setFillColorRGB(0, 0, 0)
                                can.drawString(1.2 * cm, (y - 1.375) * cm, "Abs non J.")
                                can.drawString(1.2 * cm, (y - 1.375) * cm, "Abs non J. (h)")
                                can.drawString(1.2 * cm, (y - 2.15) * cm, "Abs just. (h)")
                                can.drawString(1.2 * cm, (y - 2.925) * cm, "Retards (nb) ")
                                can.drawString(1.2 * cm, (y - 3.7) * cm, "Consignes (h) ")
                                can.drawString(4.21 * cm, (y - 1.375) * cm, "Avertissement")
                                can.drawString(4.21 * cm, (y - 2.15) * cm, "Blâme")
                                can.drawString(4.21 * cm, (y - 2.925) * cm, f"Exclusions (j)")
                                can.drawString(4.21 * cm, (y - 3.7) * cm, f"Exclusion (def)")

                            draw_contours()

                            # remplissage sanctions...
                            can.setFont("calibri bold", 10)
                            abs_nj = other_datas['unjustified_absence_count']
                            abs_jus = other_datas['justified_absence_count']
                            avert = other_datas['warning_count']
                            blame = other_datas['reprimand_count']
                            consigne = other_datas['detention_count']
                            exclusion = other_datas['ban_count']
                            exclu_def = other_datas['permanent_ban_count']
                            retard = other_datas['late_count']

                            can.drawCentredString(3.65 * cm, (y - 1.375) * cm, f"{abs_nj}")
                            can.drawCentredString(3.65 * cm, (y - 2.15) * cm, f"{abs_jus}")
                            can.drawCentredString(3.65 * cm, (y - 2.925) * cm, f"{retard}")
                            can.drawCentredString(3.65 * cm, (y - 3.7) * cm, f"{consigne}")
                            can.drawCentredString(6.8 * cm, (y - 1.375) * cm, f"{avert}")
                            can.drawCentredString(6.8 * cm, (y - 2.15) * cm, f"{blame}")
                            can.drawCentredString(6.8 * cm, (y - 2.925) * cm, f"{exclusion}")
                            can.drawCentredString(6.8 * cm, (y - 3.7) * cm, f"{exclu_def}")

                            # travail de l'élève
                            can.setFont("calibri", 10)
                            can.drawString(7.5 * cm, (y - 1.375) * cm, "Total Gén.".upper())
                            can.drawString(7.5 * cm, (y - 2.15) * cm, "Coef".upper())
                            can.drawString(7.5 * cm, (y - 2.925) * cm, "Moyenne".upper())
                            can.drawString(7.5 * cm, (y - 3.7) * cm, f"Cote".upper())

                            can.setFont("calibri bold", 10)
                            can.drawString(11 * cm, (y - 1.375) * cm, "appreciations.".upper())
                            can.setFont("calibri", 8)
                            can.drawString(11 * cm, (y - 1.9625) * cm, "CTBA")
                            can.drawString(11 * cm, (y - 2.35) * cm, "CBA")
                            can.drawString(11 * cm, (y - 2.7375) * cm, "CA")
                            can.drawString(11 * cm, (y - 3.125) * cm, "CMA")
                            can.drawString(11 * cm, (y - 3.8125) * cm, "CNA")

                            # Remplissage du travail de l'élève
                            can.setFont("calibri bold", 11)
                            can.drawCentredString(10.05 * cm, (y - 1.375) * cm,
                                                  f"{write_number(other_datas['student_points'])}")
                            can.drawCentredString(10.05 * cm, (y - 2.15) * cm,
                                                  f"{other_datas['student_total_coefficient']}")
                            can.drawCentredString(10.05 * cm, (y - 2.925) * cm,
                                                  f"{write_number(other_datas['student_average'])}")
                            can.drawCentredString(10.05 * cm, (y - 3.7) * cm,
                                                  f"{get_rating(other_datas['student_average'])}")

                            # Profil de la classe
                            can.setFont("calibri", 10)
                            can.drawString(13.8 * cm, (y - 1.375) * cm, "Moyenne générale")
                            can.setFillColorRGB(1, 0, 0)
                            can.setFont("calibri bold", 10)
                            can.drawString(13.8 * cm, (y - 2.15) * cm, "[Min-Max]")
                            can.setFont("calibri", 10)
                            can.setFillColorRGB(0, 0, 0)
                            can.drawString(13.8 * cm, (y - 2.925) * cm, "Nb de moyennes")
                            can.drawString(13.8 * cm, (y - 3.7) * cm, f"Taux de réussite")

                            # Remplissage profil
                            can.setFont("calibri bold", 11)
                            can.drawCentredString(18.5 * cm, (y - 1.375) * cm,
                                                  f"{write_number(other_datas['class_general_average'])}")
                            can.drawCentredString(
                                18.5 * cm, (y - 2.15) * cm,
                                f"{write_number(other_datas['class_min_average'])} - {write_number(other_datas['class_max_average'])}"
                            )
                            can.drawCentredString(18.5 * cm, (y - 2.925) * cm, f"{other_datas['class_nb_success']}")
                            can.drawCentredString(18.5 * cm, (y - 3.7) * cm,
                                                  f"{write_number(other_datas['class_success_rate'])} %")

                        draw_cadre_stats()

                        # Entêtes des stats
                        def draw_observations():
                            can.setFont("calibri bold", 11)
                            can.setFillColorRGB(0, 0, 0)
                            can.drawCentredString(4.15 * cm, (y - 0.7) * cm, "Discipline")
                            can.drawCentredString(10.45 * cm, (y - 0.7) * cm, "Travail de l'élève")
                            can.drawCentredString(17.3 * cm, (y - 0.7) * cm, "Profil de la classe")

                            can.setFont("calibri", 9)
                            can.drawCentredString(4.15 * cm, (y - 4.4) * cm, "Appréciation du travail de l'élève")
                            can.drawCentredString(4.15 * cm, (y - 4.8) * cm, "(Points forts et points à améliorer)")

                            can.drawCentredString(8.8 * cm, (y - 4.4) * cm, "Visa du parent /")
                            can.drawCentredString(8.8 * cm, (y - 4.8) * cm, "tuteur")

                            can.drawCentredString(11.95 * cm, (y - 4.4) * cm, "Nom et visa du")
                            can.drawCentredString(11.95 * cm, (y - 4.8) * cm, "professeur titulaire")

                            can.drawCentredString(17.3 * cm, (y - 4.4) * cm, "Le chef d'établissement")

                        draw_observations()

                        can.showPage()

                    # sauvegarde du fichier....
                    can.save()
                    buffer.seek(0)

                    # Upload Supabase
                    file_path = f"Bulletin_{selected_class}_{selected_sequence}_{uuid.uuid4().hex[:6]}.pdf"
                    supabase_client.storage.from_(DOCUMENTS_BUCKET).upload(
                        path=file_path,
                        file=buffer.getvalue(),
                        file_options={"content-type": "application/pdf"}
                    )
                    signed_url_response = supabase_client.storage.from_(DOCUMENTS_BUCKET).create_signed_url(
                        file_path, 3600 * 24 * 365
                    )
                    signed_url = signed_url_response.get("signedURL")

                    self.pr_ring.visible = False
                    self.pr_download_report_bt.visible = True
                    self.pr_download_report_bt.url = signed_url

                    self.pr_text.value = 'Ficher disponible. cliquez sur télécharger'
                    self.pr_construction.visible = False
                    self.cp.page.update()

                # si aucune sequence n'est sélectionnée
                else:
                    print(f"cas 1.2: ---sequence est nul ---")
                    self.cp.box.title.value = languages[self.lang]['error']
                    self.cp.box.content.value = languages[self.lang]['sequence missing']
                    self.cp.box.open = True
                    self.cp.box.update()


            #Bulletins trimestriels...
            elif self.pr_type.value == "quarterly":
                if self.pr_quarter.value != "":
                    selected_class = self.pr_class.value
                    selected_quarter = self.pr_quarter.value

                # si aucune quarter n'est sélectionnée
                else:
                    self.cp.box.title.value = languages[self.lang]['error']
                    self.cp.box.content.value = languages[self.lang]['quarter missing']
                    self.cp.box.open = True
                    self.cp.box.update()

            # Bulletin annuel...
            else:
                pass

        # Si aucun type n'est sélectionné
        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['report type missing']
            self.cp.box.open = True
            self.cp.box.update()

    def build_report_file(self, e):
        self.run_async_in_thread(self.load_report_file(e))




