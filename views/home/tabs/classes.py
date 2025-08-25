import flet as ft
from components import MyButton, FlatButton, MyMiniIcon, ColoredButton, ColoredIconButton, ColoredIcon, BarGraphic
from utils.styles import search_style, drop_style, login_style, other_style, datatable_style, cool_style
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading, time
from services.async_functions.class_functions import *
from services.async_functions.students_functions import get_current_year_label


class Classes(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center
        )
        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # KPI __________________________________________________________________________________
        self.nb_classes = ft.Text(size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.fill_rate = ft.Text(size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.max_capacity = ft.Text(size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.actual_capacity = ft.Text(size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.nb_active_class = ft.Text(size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.pb_rate = ft.ProgressBar(
            color='orange', bgcolor='orange50', height=10, border_radius=10, width=150
        )
        self.nb_franco = ft.Text('-', size=28, font_family='PPL')
        self.nb_anglo = ft.Text('-', size=28, font_family='PPL')
        self.exam_classes = ft.Text('-', size=28, font_family='PPL')
        self.fill_rate_container = ft.Container(
            width=170, height=120, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'indigo', 'indigo50'),
                            ft.Text(languages[lang]['fr'].upper(), size=12, font_family='PPI', color='indigo')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.fill_rate,
                            ft.Text(languages[lang]['fill rate'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.max_cap_container = ft.Container(
            width=170, height=120, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.AREA_CHART, 'teal', 'teal50'),
                            ft.Text(languages[lang]['mc'].upper(), size=12, font_family='PPI', color='teal')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.max_capacity,
                            ft.Text(languages[lang]['max capacity'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.cap_actu_container = ft.Container(
            width=170, height=120, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.BAR_CHART_ROUNDED, 'deeporange', 'deeporange50'),
                            ft.Text('CAP', size=12, font_family='PPI', color='deeporange')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.actual_capacity,
                            ft.Text(languages[lang]['current staffing'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.anglo_franco_container = ft.Container(
            width=350, height=260, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.BAR_CHART_ROUNDED, 'green', 'green50'),
                            ft.Text('CLASSES', size=12, font_family='PPI', color='green')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.current_year_label = ft.Text(f"{get_current_year_label()}", size=11, color='indigo', font_family="PPM")

        # Main window __________________________________________________________________________
        self.search = ft.TextField(
            **cool_style, width=300, label=f"{languages[lang]['search']}", prefix_icon='search', on_change=self.on_search_change
        )
        self.table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LABEL, size=20, color='black45'),
                            ft.Text('Code')
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_BOX_OUTLINED, size=20, color='black45'),
                            ft.Text(languages[lang]['status'].capitalize())
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.GROUPS, size=20, color='black45'),
                            ft.Text(languages[lang]['capacity'].capitalize())
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.GROUP, size=20, color='black45'),
                            ft.Text(languages[lang]['head count'].capitalize())
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FORMAT_LIST_BULLETED_OUTLINED, size=20, color='black45'),
                            ft.Text('Actions')
                        ]
                    )
                ),
            ]
        )

        self.main_window = ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Container(
                        content=ft.Row(
                            [
                                self.fill_rate_container,
                                ft.VerticalDivider(color=ft.Colors.TRANSPARENT),
                                self.max_cap_container,
                                ft.VerticalDivider(color=ft.Colors.TRANSPARENT),
                                self.cap_actu_container
                            ]
                        ),
                    ),
                    ft.Row(
                        expand=True,
                        controls=[
                            # Datas _______________________________________________________________________________
                            ft.Container(
                                padding=0, border_radius=16, border=ft.border.all(1, 'white'),
                                expand=True, bgcolor='white',
                                content=ft.Column(
                                    expand=True,
                                    controls=[
                                        ft.Container(
                                            padding=20, content=ft.Row(
                                                controls=[
                                                    ft.Row(
                                                        controls=[
                                                            ColoredButton(
                                                                languages[lang]['new class'], ft.Icons.ADD_HOME_OUTLINED,
                                                                self.open_new_class_window
                                                            )
                                                        ]
                                                    ),
                                                    self.search

                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            ),
                                        ),
                                        ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
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
                            ),
                            ft.Column(
                                controls=[
                                    self.anglo_franco_container
                                ]
                            )
                        ], vertical_alignment=ft.CrossAxisAlignment.START
                    ),
                ]
            )
        )

        # new class window _______________________________________________________________________________
        self.new_code = ft.TextField(
            **login_style, prefix_icon=ft.Icons.ROOFING, width=170
        )
        self.new_level = ft.Dropdown(
            **drop_style, prefix_icon=ft.Icons.ACCOUNT_BALANCE_OUTLINED, width=200,
            menu_height=200
        )
        self.new_capacity = ft.TextField(
            **login_style, prefix_icon=ft.Icons.GROUPS_3_OUTLINED, width=150,
            text_align=ft.TextAlign.RIGHT, input_filter=ft.NumbersOnlyInputFilter()
        )
        self.new_progression_text = ft.Text("0 %", size=13, font_family="PPB", color='white')
        self.new_progression_container = ft.Container(
            padding=5, border_radius=8, bgcolor="black",
            content=ft.Row([self.new_progression_text], alignment=ft.MainAxisAlignment.CENTER)
        )
        self.new_bar = ft.ProgressBar(
            width=200, height=10, border_radius=10, color=ft.Colors.LIGHT_GREEN, bgcolor='#f0f0f6', value=0,
            expand=True
        )
        self.new_check = ft.Icon(
            'check_circle', color=ft.Colors.LIGHT_GREEN, size=24,
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN)
        )
        self.new_class_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16), expand=True,
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16,  width=500, height=470, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=16, top_right=16),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new class'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor='#f0f0f6', scale=0.7,
                                        on_click=self.close_new_class_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=16, bottom_right=16),
                            content=ft.Column(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['level'], size=11, color='grey', font_family='PPM'),
                                            self.new_level,
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text('code', size=11, color='grey', font_family='PPM'),
                                            self.new_code,
                                        ], spacing=2
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['capacity'], size=11, color='grey', font_family='PPM'),
                                            self.new_capacity,
                                        ], spacing=2
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Divider(height=1, thickness=1),
                                    ft.Text(languages[lang]['slots generation'], size=12, font_family='PPI', color='black54'),
                                    ft.Container(
                                        alignment=ft.alignment.center,
                                        content=ft.Row(
                                            controls=[
                                                self.new_bar, self.new_check, self.new_progression_container
                                            ]
                                        )
                                    ),
                                    # ft.Divider(height=1, thickness=1),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.Row(
                                        [MyButton(languages[lang]['valid'], 'check', 180, self.add_new_class)]
                                    )
                                ], spacing=10,
                            )
                        )
                    ], spacing=0
                )
            )
        )

        self.det_main_teacher = ft.TextField(
            **cool_style, width=300, prefix_icon=ft.Icons.ASSIGNMENT_IND, read_only=True
        )
        self.det_count = ft.TextField(
            **cool_style, width=100, prefix_icon='groups_outlined', text_align=ft.TextAlign.RIGHT,
            read_only=True
        )
        self.det_level = ft.TextField(
            **cool_style, width=160, prefix_icon=ft.Icons.ACCOUNT_BALANCE_OUTLINED, read_only=True
        )
        self.det_table_registered = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[lang]['name'].capitalize(), languages[lang]['gender']
                ]
            ]
        )
        self.det_table_affectations = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[lang]['day'].capitalize(), languages[lang]['slot'], languages[lang]['subject'],
                    languages[lang]['teacher'],
                ]
            ]
        )

        # subjects and teachers window ______________________________________________________________________
        self.st_details_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=800, height=700, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="black", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=16, top_right=16),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]["class details"], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_details_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=16, bottom_right=16), expand=True,
                            content=ft.Column(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Column(
                                                        controls=[
                                                            ft.Text(languages[lang]['level'], size=11, color='grey',
                                                                    font_family='PPM'),
                                                            self.det_level,

                                                        ], spacing=2
                                                    ),
                                                    ft.Column(
                                                        controls=[
                                                            ft.Text(languages[lang]['head teacher'], size=11, color='grey',
                                                                    font_family='PPM'),
                                                            self.det_main_teacher,

                                                        ], spacing=2
                                                    ),
                                                    ft.Column(
                                                        controls=[
                                                            ft.Text(languages[lang]['head count'], size=11, color='grey',
                                                                    font_family='PPM'),
                                                            self.det_count,

                                                        ], spacing=2
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    ft.Tabs(
                                        tab_alignment=ft.TabAlignment.START, selected_index=0, expand=True,
                                        animation_duration=300,
                                        unselected_label_color='black54', label_color='black',
                                        indicator_border_radius=30, indicator_border_side=ft.BorderSide(5, MAIN_COLOR),
                                        indicator_tab_size=True,
                                        tabs=[
                                            ft.Tab(
                                                tab_content=ft.Row(
                                                    controls=[
                                                        ft.Icon(ft.Icons.GROUPS, size=20),
                                                        ft.Text(languages[lang]["registered students list"].upper(), size=13,
                                                                font_family="PPM")
                                                    ]
                                                ),
                                                content=ft.Container(
                                                    padding=10, expand=True,
                                                    content=ft.ListView(expand=True, controls=[
                                                                self.det_table_registered])
                                                )
                                            ),
                                            ft.Tab(
                                                tab_content=ft.Row(
                                                    controls=[
                                                        ft.Icon(ft.Icons.SCHOOL, size=20),
                                                        ft.Text(languages[lang]['menu time table'].upper(), size=13,
                                                                font_family="PPM")
                                                    ]
                                                ),
                                                content=ft.Container(
                                                    padding=10, expand=True,
                                                    content=ft.ListView(expand=True, controls=[self.det_table_affectations])
                                                )
                                            )
                                        ]
                                    )
                                ]
                            )
                        )
                    ], spacing=0
                )
            )
        )

        # content ___________________________________________________________________
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
        # self.content = ft.Stack(
        #     expand=True,
        #     controls=[
        #         self.main_window, self.new_class_window, self.st_details_window
        #     ], alignment=ft.alignment.center
        # )
        self.on_mount()

    async def build_main_view(self):
        self.content.controls.clear()

        for widget in (self.main_window, self.new_class_window, self.st_details_window):
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
        self.cp.left_menu.opacity = 0.3
        self.cp.top_menu.opacity = 0.3
        self.main_window.opacity = 0.3
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
        await self.load_datas_classes()
        await self.load_datas_levels()
        await self.load_levels()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_levels(self):
        items = await get_all_level_codes(self.cp.page.client_storage.get('access_token'))

        for item in items:
            self.new_level.options.append(
                ft.dropdown.Option(item)
            )
        self.new_level.update()

    async def load_datas_levels(self):
        access_token = self.cp.page.client_storage.get('access_token')
        details = await count_classes_by_section(access_token)
        exam_classes = await count_exam_classes(access_token)
        self.nb_franco.value = details['francophone']
        self.nb_anglo.value = details['anglophone']
        self.exam_classes.value = exam_classes

        anglo = {
            'value': details['anglophone'], 'label': languages[self.lang]['anglophone classes'],
            'color': 'blue', 'bg_color': 'blue50'
        }
        franco = {
            'value': details['francophone'], 'label': languages[self.lang]['francophone classes'],
            'color': 'teal', 'bg_color': 'teal50'
        }
        self.anglo_franco_container.content.controls.append(
            BarGraphic([anglo, franco], details['francophone'] + details['anglophone'])
        )

        self.cp.page.update()

    async def load_datas_classes(self):
        details = await get_classes_details(self.cp.page.client_storage.get("access_token"))
        self.table.rows.clear()

        active, cap_max, cap_actu = 0, 0, 0

        for detail in details:
            cap_max += detail['capacity']
            cap_actu += detail['student_count']

            if detail['active']:
                color = 'teal'
                bgcolor = 'teal50'
                text = 'active'
                icone = ft.Icons.CHECK
                active += 1
            else:
                color = 'red'
                bgcolor = 'red50'
                text = 'inactive'
                icone = ft.Icons.CLOSE

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(detail['class_code'])),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=bgcolor, padding=5, border_radius=10, width=90,
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(icone, size=16, color=color),
                                        ft.Text(text, size=11, font_family='PPM', color=color)
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=2
                                )
                            )
                        ),
                        ft.DataCell(ft.Text(detail['student_count'])),
                        ft.DataCell(ft.Text(detail['capacity'])),
                        ft.DataCell(MyMiniIcon('edit_outlined', '', 'grey', detail, self.show_class_details), )
                    ]
                )
            )

        self.nb_classes.value = len(details)
        self.nb_active_class.value = active
        self.max_capacity.value = cap_max
        self.actual_capacity.value = cap_actu
        self.fill_rate.value = f"{cap_actu * 100 / cap_max:.2f} %"
        self.pb_rate.value = cap_actu / cap_max

        await self.build_main_view()

    async def filter_datas(self, e):
        details = await get_classes_details(self.cp.page.client_storage.get("access_token"))
        self.table.rows.clear()
        search = self.search.value if self.search.value else ''
        filtered_datas = list(filter(lambda x: search in x['level_code'], details))

        for detail in filtered_datas:
            if detail['active']:
                color = 'teal'
                bgcolor = 'teal50'
                text = 'active'
                icone = ft.Icons.CHECK
            else:
                color = 'red'
                bgcolor = 'red50'
                text = 'inactive'
                icone = ft.Icons.CLOSE

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(detail['class_code'])),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=bgcolor, padding=5, border_radius=10, width=90,
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(icone, size=16, color=color),
                                        ft.Text(text, size=11, font_family='PPM', color=color)
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=2
                                )
                            )
                        ),
                        ft.DataCell(ft.Text(detail['student_count'])),
                        ft.DataCell(ft.Text(detail['capacity'])),
                        ft.DataCell(MyMiniIcon('edit_outlined', '', 'grey', detail, self.show_class_details), )
                    ]
                )
            )

        self.table.update()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    def reset_filter_classes(self, e):
        self.search.value = ""
        self.search.update()
        self.run_async_in_thread(self.load_datas_classes())

    def open_new_class_window(self, e):
        if self.cp.page.client_storage.get("role") in ['principal', 'préfet']:
            self.show_one_window(self.new_class_window)
        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error rights']
            self.cp.box.open = True
            self.cp.box.update()

    def close_new_class_window(self, e):
        self.hide_one_window(self.new_class_window)

    def add_new_class(self, e):
        count = 0
        days = ['day 1', 'day 2', 'day 3', 'day 4', 'day 5']
        slots = ['07:30-08:30', '08:30-09:30', '09:30-10:30', '10:45-11:45', '11:45-12:45', '13:00-14:00', '14:00-15:00', '15:00-16:00']

        if self.new_level.value and self.new_code.value and self.new_capacity.value:

            resp = supabase_client.table('levels').select("id").eq('code', self.new_level.value).execute()
            level_id = resp.data[0]['id']
            print(level_id)

            # create a class
            resp = supabase_client.table('classes').insert(
                {'code': self.new_code.value, 'capacity': int(self.new_capacity.value), 'level_id': level_id}
            ).execute()
            time.sleep(2)
            print('created')

            # get id of the new created class
            resp = supabase_client.table('classes').select('id').eq('code', self.new_code.value).execute()
            class_id = resp.data[0]['id']
            print(class_id)
            print("année id", self.cp.current_year)

            # create affectations
            for day in days:
                for slot in slots:
                    supabase_client.table('affectations').insert(
                        {'year_id': self.cp.current_year, 'class_id': class_id, 'nb_hour': 1, 'day': day, 'slot': slot}
                    )
                    count += 1
                    value = count / 40
                    self.new_bar.value = value
                    self.new_progression_text = f"{value:.0f} %"
                    self.new_bar.update()

                    if 0 < value <= 0.3:
                        color = 'red'
                    elif 0.3 < value < 0.6:
                        color = BASE_COLOR
                    elif 0.6 < value <= 0.99:
                        color = ft.Colors.LIGHT_GREEN
                    else:
                        color = 'green'

                    self.new_progression_container.bgcolor = color
                    self.new_progression_container.update()

            for widget in (self.new_code, self.new_level, self.new_capacity):
                widget.value = None
                widget.update()

            self.new_check.scale = 1
            self.new_check.update()
            self.cp.box.title.value = languages[self.lang]['success']
            self.cp.box.content.value = languages[self.lang]['class creation success']
            self.cp.box.open = True
            self.cp.box.update()

            time.sleep(2)
            self.new_check.scale = 0
            self.new_check.update()
            self.on_mount()

        else:
            self.cp.box.title.value = languages[self.lang]['error']
            self.cp.box.content.value = languages[self.lang]['error msg']
            self.cp.box.open = True
            self.cp.box.update()

    async def open_details_window(self, e):
        self.det_level.value = e.control.data['level_code']
        self.det_count.value = e.control.data['student_count']

        access_token = self.cp.page.client_storage.get('access_token')

        prof_datas = await get_head_teacher_name(access_token, e.control.data['class_id'], self.cp.year_id)

        if isinstance(prof_datas, dict):
            self.det_main_teacher.value = f"{prof_datas['name']} {prof_datas['surname']}"
        else:
            pass

        # students ___________________________________
        details = await get_students_by_class_id(e.control.data['class_id'], access_token)
        self.det_table_registered.rows.clear()

        for detail in details:
            self.det_table_registered.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{detail['name']} {detail['surname']}".upper())),
                        ft.DataCell(ft.Text(f"{detail['gender']}"))
                    ]
                )
            )

        # schedule _______________________________________
        slots = await get_class_schedule(e.control.data['class_id'], access_token)
        self.det_table_affectations.rows.clear()

        for slot in slots:
            self.det_table_affectations.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(languages[self.lang][slot['day']])),
                        ft.DataCell(ft.Text(slot['slot'])),
                        ft.DataCell(ft.Text(slot['teacher_name'])),
                        ft.DataCell(ft.Text(slot['short_name']))
                    ]
                )
            )

        self.show_one_window(self.st_details_window)

    def show_class_details(self, e):
        self.run_async_in_thread(self.open_details_window(e))

    def close_details_window(self, e):
        self.hide_one_window(self.st_details_window)



