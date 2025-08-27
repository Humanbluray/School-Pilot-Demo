import threading
from components import MyMiniIcon, ColoredIcon, ColoredButton, ColoredIconButton
from services.async_functions.fees_functions import *
from translations.translations import languages
from utils.couleurs import *
from utils.styles import drop_style, datatable_style
from utils.useful_functions import format_number, add_separator


class SchoolFees(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center
        )
        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # main window ______________________________________________________________

        # Kpi
        self.expected_amount = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.amount_collected = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.amount_stayed = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.recovery_rate = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)

        self.ct_expected = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.BAR_CHART_ROUNDED, 'indigo', 'indigo50'),
                            ft.Text(languages[lang]['expected'].upper(), size=12, font_family='PPI', color='indigo')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.expected_amount,
                            ft.Text(languages[lang]['expected amount'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_collected = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.RECEIPT_SHARP, 'teal', 'teal50'),
                            ft.Text(languages[lang]['received'].upper(), size=12, font_family='PPI', color='teal')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.amount_collected,
                            ft.Text(languages[lang]['collected amount'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_remaining = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.REAL_ESTATE_AGENT, 'deeporange', 'deeporange50'),
                            ft.Text(languages[lang]['remaining'].upper(), size=12, font_family='PPI', color='deeporange')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.amount_stayed,
                            ft.Text(languages[lang]['remaining balance'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_rate = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'green', 'green50'),
                            ft.Text(languages[lang]['rate'].upper(), size=12, font_family='PPI', color='green')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.recovery_rate,
                            ft.Text(languages[lang]['recovery rate'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        # widget
        self.search_class = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.ROOFING, label=languages[lang]['class'], width=180,
            on_change=None, menu_height=200,
            options=[ft.dropdown.Option(key=" ", text=f"global")], value=" "
        )
        self.search_tranche = ft.Dropdown(
            **drop_style, width=160, label=languages[lang]['fees part'], value='tout',
            options=[
                ft.dropdown.Option(
                    key=choice['clé'], text=f"{choice['valeur']}"
                )
                for choice in [
                    {'clé': 'fees part 1', 'valeur': languages[lang]['fees part 1']},
                    {'clé': 'fees part 2', 'valeur': languages[lang]['fees part 2']},
                    {'clé': 'fees part 3', 'valeur': languages[lang]['fees part 3']},
                    {'clé': 'tout', 'valeur': 'global'},
                ]
            ]
        )
        self.table = ft.DataTable(
            **datatable_style, expand=True,
            columns=[
                ft.DataColumn(
                    ft.Text(languages[lang]['name']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['class']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['amount paid']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['total to pay']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['remaining balance']),
                ),
                ft.DataColumn(
                    ft.Text(languages[lang]['status']),
                )
            ]
        )
        self.main_window = ft.Container(
            expand=True, content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.ct_expected, ft.VerticalDivider(),
                            self.ct_collected, ft.VerticalDivider(),
                            self.ct_rate, ft.VerticalDivider(),
                            self.ct_remaining, ft.VerticalDivider(),
                        ]
                    ),
                    ft.Row(
                        expand=True,
                        controls=[
                            ft.Container(
                                padding=0, border_radius=16, border=ft.border.all(1, 'white'),
                                expand=True, bgcolor='white', content=ft.Column(
                                    controls=[
                                        ft.Container(
                                            padding=20, border=ft.border.all(1, "#f0f0f6"),
                                            content=ft.Row(
                                                controls=[
                                                    ft.Row(
                                                        controls=[
                                                            ColoredButton(
                                                                languages[lang]['make a payment'],
                                                                ft.Icons.ADD_CARD_OUTLINED, None
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
                                                            self.search_class, self.search_tranche,
                                                            MyMiniIcon(
                                                                ft.Icons.FILTER_ALT_OUTLINED, languages[lang]['filter'], 'black', None,
                                                                self.click_on_filter
                                                            ),
                                                            MyMiniIcon(
                                                                ft.Icons.FILTER_ALT_OFF_OUTLINED, '',
                                                                'black', None, self.delete_filter
                                                            )
                                                        ]
                                                    )
                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            )
                                        ),
                                        ft.Divider(color=ft.Colors.TRANSPARENT),
                                        ft.ListView(expand=True, controls=[self.table]),
                                        ft.Container(
                                            padding=10
                                        )
                                    ]
                                )
                            ),
                        ]
                    )
                ]
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

    async def build_main_view(self):
        self.content.controls.clear()
        self.content.controls.append(self.main_window)
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
        access_token = self.cp.page.client_storage.get("access_token")
        all_classes = await get_all_classes_basic_info(access_token)

        print(all_classes)

        for one_classe in all_classes:
            self.search_class.options.append(
                ft.dropdown.Option(
                    key=one_classe['id'], text=f"{one_classe['code']}"
                )
            )

        self.cp.page.update()

        datas = await get_student_fees_summary(access_token, self.cp.year_id)
        self.table.rows.clear()

        # Variables pour calculer les indicateurs...
        paid = 0
        total_expected = 0
        remaining = 0

        for data in datas:
            paid += data['total_paid']
            total_expected += data['total_to_pay']
            remaining += data['reste_a_payer']

            if data['reste_a_payer'] == 0:
                status_color = 'teal'
                status_bgcolor = 'teal50'
                status_icone = ft.Icons.CHECK
                status_text = languages[self.lang]['sold out']
            else:
                status_color = 'red'
                status_bgcolor = 'red50'
                status_icone = ft.Icons.INDETERMINATE_CHECK_BOX_ROUNDED
                status_text = languages[self.lang]['on going']

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                        ),
                        ft.DataCell(ft.Text(data['class_code'])),
                        ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                        ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                        ft.DataCell(ft.Text(f"{add_separator(data['reste_a_payer'])}")),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=status_bgcolor, border_radius=12, padding=5, width=95,
                                border=ft.border.all(1, status_color),
                                content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(status_icone, size=14, color=status_color),
                                                ft.Text(status_text, size=11, font_family='PPM', color=status_color)
                                            ], spacing=3
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                )
                            )
                        ),
                    ]
                )
            )

        self.expected_amount.value = format_number(total_expected)
        self.amount_collected.value = format_number(paid)
        self.amount_stayed.value = format_number(remaining)
        self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

        await self.build_main_view()

    async def filter_datas(self, e):
        access_token = self.cp.page.client_storage.get("access_token")

        # cas du rapport global...
        if self.search_tranche.value == 'tout':

            # if class field is empty...
            if self.search_class.value == " ":
                datas = await get_student_fees_summary(access_token, self.cp.year_id)
                self.table.rows.clear()

                # Variables pour calculer les indicateurs...
                paid = 0
                total_expected = 0
                remaining = 0

                for data in datas:
                    paid += data['total_paid']
                    total_expected += data['total_to_pay']
                    remaining += data['reste_a_payer']

                    if data['reste_a_payer'] == 0:
                        status_color = 'teal'
                        status_bgcolor = 'teal50'
                        status_icone = ft.Icons.CHECK
                        status_text = languages[self.lang]['sold out']
                    else:
                        status_color = 'red'
                        status_bgcolor = 'red50'
                        status_icone = ft.Icons.CHECK
                        status_text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                                ),
                                ft.DataCell(ft.Text(data['class_code'])),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['reste_a_payer'])}")),
                                ft.DataCell(
                                    ft.Container(
                                        bgcolor=status_bgcolor, border_radius=12, padding=5, width=95,
                                        border=ft.border.all(1, status_color),
                                        content=ft.Row(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(status_icone, size=14, color=status_color),
                                                        ft.Text(status_text, size=11, font_family='PPM',
                                                                color=status_color)
                                                    ], spacing=3
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        )
                                    )
                                ),
                            ]
                        )
                    )

                self.expected_amount.value = format_number(total_expected)
                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(remaining)
                self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

                self.cp.page.update()

            # if class filed is filled
            else:
                class_filtered = self.search_class.value if self.search_class.value else ""
                datas = await get_student_fees_summary(access_token, self.cp.year_id)
                self.table.rows.clear()

                filtered_datas = list(filter(lambda x: class_filtered in x['class_id'], datas))

                # Variables pour calculer les indicateurs...
                paid = 0
                total_expected = 0
                remaining = 0

                for data in filtered_datas:
                    paid += data['total_paid']
                    total_expected += data['total_to_pay']
                    remaining += data['reste_a_payer']

                    if data['reste_a_payer'] == 0:
                        status_color = 'teal'
                        status_bgcolor = 'teal50'
                        status_icone = ft.Icons.CHECK
                        status_text = languages[self.lang]['sold out']
                    else:
                        status_color = 'red'
                        status_bgcolor = 'red50'
                        status_icone = ft.Icons.INDETERMINATE_CHECK_BOX_ROUNDED
                        status_text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                                ),
                                ft.DataCell(ft.Text(data['class_code'])),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['reste_a_payer'])}")),
                                ft.DataCell(
                                    ft.Container(
                                        bgcolor=status_bgcolor, border_radius=12, padding=5, width=95,
                                        border=ft.border.all(1, status_color),
                                        content=ft.Row(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(status_icone, size=14, color=status_color),
                                                        ft.Text(status_text, size=11, font_family='PPM', color=status_color)
                                                    ], spacing=3
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        )
                                    )
                                ),
                            ]
                        )
                    )

                self.expected_amount.value = format_number(total_expected)
                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(remaining)
                self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

                self.cp.page.update()

        #  cas du rapport par tranche...
        else:
            # if class filed is empty...
            if self.search_class.value is None:
                datas = await get_student_fees_summary_by_part(
                    access_token, self.search_tranche.value, self.cp.year_id
                )
                self.table.rows.clear()

                # Variables pour calculer les indicateurs...
                paid = 0
                total_expected = 0
                remaining = 0

                for data in datas:
                    paid += data['total_paid']
                    total_expected += data['total_to_pay']
                    remaining += data['reste_a_payer']

                    if data['reste_a_payer'] == 0:
                        status_color = 'teal'
                        status_bgcolor = 'teal50'
                        status_icone = ft.Icons.CHECK
                        status_text = languages[self.lang]['sold out']
                    else:
                        status_color = 'red'
                        status_bgcolor = 'red50'
                        status_icone = ft.Icons.INDETERMINATE_CHECK_BOX_ROUNDED
                        status_text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                                ),
                                ft.DataCell(ft.Text(data['class_code'])),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['reste_a_payer'])}")),
                                ft.DataCell(
                                    ft.Container(
                                        bgcolor=status_bgcolor, border_radius=12, padding=5, width=95,
                                        border=ft.border.all(1, status_color),
                                        content=ft.Row(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(status_icone, size=14, color=status_color),
                                                        ft.Text(status_text, size=11, font_family='PPM',
                                                                color=status_color)
                                                    ], spacing=3
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        )
                                    )
                                ),
                            ]
                        )
                    )

                self.expected_amount.value = format_number(total_expected)
                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(remaining)
                self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

                self.cp.page.update()

            # if class field is filled ...
            else:
                sc = self.search_class.value
                datas = await get_student_fees_summary_by_part(access_token, self.search_tranche.value, self.cp.year_id)
                self.table.rows.clear()

                filtered_datas = list(filter(lambda x: sc in x['class_id'], datas))

                # Variables pour calculer les indicateurs...
                paid = 0
                total_expected = 0
                remaining = 0

                for data in filtered_datas:
                    paid += data['total_paid']
                    total_expected += data['total_to_pay']
                    remaining += data['reste_a_payer']
                    print(f"paid {paid}")
                    print(f"total_expected {total_expected}")
                    print(f"remaining {remaining}")

                    if data['reste_a_payer'] == 0:
                        status_color = 'teal'
                        status_bgcolor = 'teal50'
                        status_icone = ft.Icons.CHECK
                        status_text = languages[self.lang]['sold out']
                    else:
                        status_color = 'red'
                        status_bgcolor = 'red50'
                        status_icone = ft.Icons.INDETERMINATE_CHECK_BOX_ROUNDED
                        status_text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                                ),
                                ft.DataCell(ft.Text(data['class_code'])),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['reste_a_payer'])}")),
                                ft.DataCell(
                                    ft.Container(
                                        bgcolor=status_bgcolor, border_radius=12, padding=5, width=95,
                                        border=ft.border.all(1, status_color),
                                        content=ft.Row(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(status_icone, size=14, color=status_color),
                                                        ft.Text(status_text, size=11, font_family='PPM',
                                                                color=status_color)
                                                    ], spacing=3
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        )
                                    )
                                ),
                            ]
                        )
                    )

                self.expected_amount.value = format_number(total_expected)
                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(remaining)
                self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%" if total_expected > 0 else '0 %'

                self.cp.page.update()

    def click_on_filter(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    async def supp_filter(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        datas = await get_student_fees_summary(access_token, self.cp.year_id)
        self.table.rows.clear()

        # Variables pour calculer les indicateurs...
        paid = 0
        total_expected = 0
        remaining = 0

        for data in datas:
            paid += data['total_paid']
            total_expected += data['total_to_pay']
            remaining += data['reste_a_payer']

            if data['reste_a_payer'] == 0:
                status_color = 'teal'
                status_bgcolor = 'teal50'
                status_icone = ft.Icons.CHECK
                status_text = languages[self.lang]['sold out']
            else:
                status_color = 'red'
                status_bgcolor = 'red50'
                status_icone = ft.Icons.INDETERMINATE_CHECK_BOX_ROUNDED
                status_text = languages[self.lang]['on going']

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(f"{data['student_name']} {data['student_surname']}".upper())
                        ),
                        ft.DataCell(ft.Text(data['class_code'])),
                        ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                        ft.DataCell(ft.Text(f"{add_separator(data['total_to_pay'])}")),
                        ft.DataCell(ft.Text(f"{add_separator(data['reste_a_payer'])}")),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=status_bgcolor, border_radius=12, padding=5, width=95,
                                border=ft.border.all(1, status_color),
                                content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(status_icone, size=14, color=status_color),
                                                ft.Text(status_text, size=11, font_family='PPM', color=status_color)
                                            ], spacing=3
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                )
                            )
                        ),
                    ]
                )
            )

        self.expected_amount.value = format_number(total_expected)
        self.amount_collected.value = format_number(paid)
        self.amount_stayed.value = format_number(remaining)
        self.recovery_rate.value = f"{(paid * 100 / total_expected):.2f}%"

        self.search_class.value = " "
        self.search_tranche.value = 'tout'

        self.cp.page.update()

    def delete_filter(self, e):
        self.run_async_in_thread(self.supp_filter(e))