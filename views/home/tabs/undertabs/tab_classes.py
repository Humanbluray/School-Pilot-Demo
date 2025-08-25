from utils.couleurs import *
from utils.styles import drop_style
from components import *
from translations.translations import languages
import asyncio, threading
from services.supabase_client import supabase_client
from services.async_functions.teachers_functions import *
from services.async_functions.students_functions import get_current_year_id


class TabClasses(ft.Tab):
    def __init__(self, cp: object,):
        super().__init__()
        self.cp = cp
        lang = self.cp.cp.language
        self.lang = lang
        self.tab_content = ft.Row(
            expand=True,
            controls=[
                ft.Icon(ft.Icons.ROOFING, size=20),
                ft.Text(languages[lang]['class view'].upper(), size=13, font_family="Poppins Medium")
            ]
        )
        self.year_id = get_current_year_id()
        self.search_class = ft.Dropdown(
            **drop_style, width=170, prefix_icon='roofing', label=languages[lang]['class'],
            on_change=self.on_class_change, menu_height=200
        )
        self.check_class_button = ColoredButton(
            languages[lang]['affectations details'], ft.Icons.VIEW_MODULE, self.open_details_window
        )

        self.monday = ft.Column()
        self.tuesday = ft.Column()
        self.wednesday = ft.Column()
        self.thursday = ft.Column()
        self.friday = ft.Column()

        self.main_window = ft.Container(
            expand=True, padding=10,  # bgcolor='white',
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Row(
                        [
                            self.search_class,
                            self.check_class_button

                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Column(
                        expand=True, scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.Row(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]
                            )
                        ]
                    )
                ]
            )
        )

        # New affectation window...
        self.new_affectation_id = ""
        self.new_prof = ft.Dropdown(
            **drop_style, width=300, prefix_icon='person_outlined', label=languages[lang]['teacher'],
            menu_height=200,
            options=[ft.dropdown.Option(key=" ", text=f"{languages[self.cp.lang]['select option']}")],
            value=" ", on_change=self.on_change_teacher
        )
        self.new_day = ft.TextField(
            **other_style, label=languages[lang]['day'], prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            read_only=True, width=150, visible=False
        )
        self.new_day_display = ft.TextField(
            **other_style, label=languages[lang]['day'], prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            read_only=True, width=150
        )
        self.new_slot = ft.TextField(
            **other_style, label=languages[lang]['slot'], prefix_icon=ft.Icons.TIMER_OUTLINED,
            read_only=True, width=150
        )
        self.new_class_id = ''
        self.new_level = ft.TextField(
            **cool_style, width=200, label=languages[lang]['level'], visible=False
        )
        self.new_subject = ft.Dropdown(
            **drop_style, width=200, label=languages[lang]['subject'], prefix_icon='book_outlined',
            options=[ft.dropdown.Option(key=" ", text=f"{languages[self.cp.lang]['select option']}")],
            on_change=self.on_subject_change, value=" ",
        )
        self.check_validity = ft.Icon(name=None, size=24, color=None)
        self.check_validity_load = ft.Icon(name=None, size=24, color=None)

        self.new_affectation_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=500, height=600, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(
                                bottom=ft.BorderSide(1, CT_BORDER_COLOR)
                            ),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new affectation'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_new_affectation_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(
                                top=ft.BorderSide(1, CT_BORDER_COLOR)
                            ), expand=True,
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                            content=ft.Column(
                                expand=True, scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    ft.Row([self.new_prof], visible=False),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['slot'].upper(), size=12, font_family='PPB'),
                                            ft.Divider(),
                                        ], spacing=0
                                    ),
                                    ft.Row([self.new_day, self.new_day_display, self.new_slot,]),
                                    ft.Divider(color='transparent'),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['teacher and subject'].upper(), size=12, font_family='PPB'),
                                            ft.Divider(),
                                        ], spacing=0
                                    ),
                                    ft.Container(
                                        border_radius=8, padding=10, border=ft.border.all(1, 'grey'),
                                        content=ft.Column(
                                            controls=[
                                                self.new_prof,
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value=f"{languages[self.cp.lang]['teacher availability check']}",
                                                            size=12, font_family='PPM'),
                                                        self.check_validity
                                                    ]
                                                ),
                                            ]
                                        )
                                    ),
                                    self.new_level,
                                    ft.Container(
                                        border_radius=8, padding=10, border=ft.border.all(1, 'grey'),
                                        content=ft.Column(
                                            controls=[
                                                self.new_subject,
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(value=f"{languages[self.cp.lang]['hourly load check']}",
                                                                size=12, font_family='PPM'),
                                                        self.check_validity_load
                                                    ]
                                                ),
                                            ]
                                        )
                                    ),
                                    ft.Container(
                                        padding=ft.padding.only(10, 0, 10 , 0),
                                        content=ft.Row(
                                            [MyButton(languages[lang]['valid'], 'check_circle', 150, self.validate_affectation)]
                                        )
                                    )
                                ]
                            ),
                        )
                    ], spacing=0
                )
            )
        )

        self.det_class = ft.TextField(
            **cool_style, prefix_icon='roofing', width=180, read_only=True
        )
        self.det_progress_bar = ft.ProgressBar(
            color=BASE_COLOR, bgcolor='#f0f0f6', width=150, height=10, border_radius=16,
        )
        self.det_percent = ft.Text(size=16, font_family='PPL')
        self.det_table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color='black45', size=20),
                            ft.Text(languages[lang]['status'])
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.BOOK_OUTLINED, color='black45', size=20),
                            ft.Text(languages[lang]['subject'])
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.WATCH_LATER_OUTLINED, color='black45', size=20),
                            ft.Text(languages[lang]['hourly load'])
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_BOX_OUTLINED, color='black45', size=20),
                            ft.Text(languages[lang]['affected'])
                        ]
                    )
                )
            ]
        )
        self.details_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=700, height=600, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(
                                bottom=ft.BorderSide(1, CT_BORDER_COLOR)
                            ),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['affectations details'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_details_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(
                                top=ft.BorderSide(1, CT_BORDER_COLOR)
                            ), expand=True,
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['class'], size=11, font_family='PPM', color='grey'),
                                                    self.det_class
                                                ], spacing=2
                                            ),
                                            ft.Column(
                                                [
                                                    ft.Text(languages[lang]['affectations state'], size=12, font_family='PPM', color='grey'),
                                                    ft.Row([self.det_progress_bar, self.det_percent])
                                                ], spacing=2
                                            )
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.END
                                    ),
                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                    ft.ListView(expand=True, controls=[self.det_table])
                                ]
                            ),
                        )
                    ], spacing=0
                )
            )
        )

        self.content = ft.Stack(
            expand=True,
            controls=[
                self.main_window, self.new_affectation_window, self.details_window
            ], alignment=ft.alignment.center
        )
        self.on_mount()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    def hide_one_window(self, window_to_hide: object):
        """
        This function helps to make menus clickable
        :param window_to_hide:
        :return:
        """
        window_to_hide.scale = 0

        self.cp.cp.left_menu.disabled = False
        self.cp.cp.top_menu.disabled = False
        self.main_window.disabled = False
        self.cp.cp.left_menu.opacity = 1
        self.cp.cp.top_menu.opacity = 1
        self.main_window.opacity = 1
        self.cp.cp.page.update()

    def show_one_window(self, window_to_show):
        """
        This function helps to make menus non-clickable
        :param window_to_show:
        :return:
        """
        window_to_show.scale = 1

        self.cp.cp.left_menu.disabled = True
        self.cp.cp.top_menu.disabled = True
        self.main_window.disabled = True
        self.cp.cp.left_menu.opacity = 0.3
        self.cp.cp.top_menu.opacity = 0.3
        self.main_window.opacity = 0.3
        self.cp.cp.page.update()

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

    async def load_datas(self):
        access_token = self.cp.cp.page.client_storage.get('access_token')
        all_classes = await get_all_classes_basic_info(access_token)

        for one_class in all_classes:
            self.search_class.options.append(
                ft.dropdown.Option(
                    key=one_class['id'], text=f"{one_class['code']}"
                )
            )

        teachers_names = await get_all_teachers(access_token)
        for teacher in teachers_names:
            self.new_prof.options.append(
                ft.dropdown.Option(
                    key=teacher['id'], text=f"{teacher['name']} {teacher['surname']}".upper()
                )
            )

    async def filter_datas(self, e):
        access_token = self.cp.cp.page.client_storage.get('access_token')
        affectations = await get_all_affectations_details(access_token)

        search = self.search_class.value
        filtered_datas = list(filter(lambda x: search in x['class_id'], affectations))

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.controls.clear()
            widget.update()

        for affectation in filtered_datas:
            card = SlotCardRoom(self, affectation)
            if affectation['day'] == "day 1":
                self.monday.controls.append(card)

            elif affectation['day'] == 'day 2':
                self.tuesday.controls.append(card)

            elif affectation['day'] == 'day 3':
                self.wednesday.controls.append(card)

            elif affectation['day'] == 'day 4':
                self.thursday.controls.append(card)

            else:
                self.friday.controls.append(card)

        level = await get_level_by_class_id(search, access_token)
        self.new_level.value = level['level_id']

        self.cp.cp.page.update()

    def on_class_change(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    def close_new_affectation_window(self, e):
        self.new_subject.value = " "
        self.new_subject.update()

        self.new_prof.value = " "
        self.new_prof.update()
        self.new_subject.value = " "
        self.new_subject.update()

        self.hide_one_window(self.new_affectation_window)

    def refresh_view(self):
        self.run_async_in_thread(self.update_current_view())

    async def update_current_view(self):
        access_token = self.cp.cp.page.client_storage.get('access_token')
        affectations = await get_all_affectations_details(access_token)

        search = self.search_class.value
        filtered_datas = list(filter(lambda x: search in x['class_id'], affectations))

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.controls.clear()
            widget.update()

        for affectation in filtered_datas:
            card = SlotCardRoom(self, affectation)
            if affectation['day'] == "day 1":
                self.monday.controls.append(card)

            elif affectation['day'] == 'day 2':
                self.tuesday.controls.append(card)

            elif affectation['day'] == 'day 3':
                self.wednesday.controls.append(card)

            elif affectation['day'] == 'day 4':
                self.thursday.controls.append(card)

            else:
                self.friday.controls.append(card)

        level = await get_level_by_class_id(search, access_token)
        self.new_level.value = level['level_id']

        self.cp.cp.page.update()

    async def select_teacher(self, e):
        access_token = self.cp.cp.page.client_storage.get('access_token')

        # check if the teacher is busy of free for this slot
        teacher_slot = await is_teacher_busy(self.new_prof.value, self.new_day.value, self.new_slot.value, access_token)
        if teacher_slot['status']:
            self.check_validity.name = "close"
            self.check_validity.color = "red"
            self.check_validity.update()
        else:
            self.check_validity.name = "check_circle"
            self.check_validity.color = "green"
            self.check_validity.update()

        # all subjects id for this teacher for this level...

        # all subjects for this level
        subjects = await get_teacher_subjects_for_level(self.new_prof.value, self.new_level.value, access_token)
        print(subjects)
        self.new_subject.options.clear()
        for subject in subjects:
            self.new_subject.options.append(
                ft.dropdown.Option(
                    key=subject['id'], text=f"{subject['short_name']}"
                )
            )

        self.cp.cp.page.update()

    def on_change_teacher(self, e):
        self.run_async_in_thread(self.select_teacher(e))

    async def select_subject(self, e):
        # check hourly load for the class
        access_token = self.cp.cp.page.client_storage.get('access_token')
        hourly_load = await get_hourly_load_by_subject_id(self.new_subject.value, access_token)
        nb_affectations = await count_affectations_by_subject_and_class(self.new_subject.value, self.search_class.value, access_token)

        if nb_affectations >= hourly_load:
            self.check_validity_load.name = 'close'
            self.check_validity_load.color = 'red'
            self.check_validity_load.update()
        else:
            self.check_validity_load.name = 'check_circle'
            self.check_validity_load.color = 'green'
            self.check_validity_load.update()

    def on_subject_change(self, e):
        self.run_async_in_thread(self.select_subject(e))

    def validate_affectation(self, e):
        if self.new_prof.value is None or self.new_subject.value is None:
            self.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.box.content.value = languages[self.cp.lang]['error msg']
            self.cp.cp.box.open = True
            self.cp.cp.box.update()

        else:
            if self.check_validity.name == 'check_circle' and self.check_validity_load.name == 'check_circle':
                supabase_client.table('affectations').update(
                    {
                        'subject_id': self.new_subject.value,
                        "teacher_id": self.new_prof.value,
                    }
                ).eq('id', self.new_affectation_id).execute()

                self.new_affectation_window.scale = 0
                self.main_window.opacity = 1
                self.main_window.disabled = False
                self.cp.cp.left_menu.opacity = 1
                self.cp.cp.left_menu.disabled = False
                self.cp.page.update()

                self.cp.cp.box.title.value = languages[self.cp.lang]['success']
                self.cp.cp.box.content.value = languages[self.cp.lang]['successful assignment']
                self.cp.cp.box.open = True
                self.cp.cp.box.update()

                self.new_subject.options.clear()
                self.new_subject.options.append(
                    ft.dropdown.Option(key=" ", text=f"{languages[self.cp.lang]['select option']}")
                )
                self.new_subject.value = " "
                self.new_subject.update()

                self.new_prof.value = " "
                self.new_prof.update()

                for widget in (self.check_validity, self.check_validity_load):
                    widget.name = None
                    widget.color = None
                    widget.update()

                self.refresh_view()

            elif self.check_validity.name == 'close' and self.check_validity_load.name == 'check_circle':
                self.cp.cp.box.title.value = languages[self.cp.lang]['error']
                self.cp.cp.box.content.value = languages[self.cp.lang]['teacher slot busy']
                self.cp.cp.box.open = True
                self.cp.cp.box.update()

            elif self.check_validity.name == 'check_circle' and self.check_validity_load.name == 'close':
                self.cp.cp.box.title.value = languages[self.cp.lang]['error']
                self.cp.cp.box.content.value = languages[self.cp.lang]['hourly load exceeded']
                self.cp.cp.box.open = True
                self.cp.cp.box.update()

            elif self.check_validity.name is None or self.check_validity_load.name is None:
                pass

            else:
                self.cp.cp.box.title.value = languages[self.cp.lang]['error']
                self.cp.cp.box.content.value = (f"{languages[self.cp.lang]['teacher slot busy']}\n"
                                                f"{languages[self.cp.lang]['hourly load exceeded']}")
                self.cp.cp.box.open = True
                self.cp.cp.box.update()

    async def load_details(self, e):
        self.show_one_window(self.details_window)

        access_token = self.cp.cp.page.client_storage.get('access_token')
        self.det_class.value = await get_class_code_by_id_async(self.search_class.value, access_token)

        details = await get_class_subjects_with_affectations(access_token, self.search_class.value)

        total, total_affected = 0, 0
        self.det_table.rows.clear()
        self.cp.cp.page.update()

        for detail in details:
            total += detail['hourly load']
            total_affected += detail["nombre_affectations"]

            if detail['hourly load'] > detail["nombre_affectations"]:
                status_icon = ft.Icons.INFO_OUTLINE_ROUNDED
                status_color = 'red'
            else:
                status_icon = ft.Icons.CHECK_CIRCLE
                status_color = 'teal'

            self.det_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Icon(status_icon, color=status_color, size=16)),
                        ft.DataCell(ft.Text(detail['short_name'].upper())),
                        ft.DataCell(ft.Text(detail['hourly load'])),
                        ft.DataCell(ft.Text(detail['nombre_affectations']))
                    ]
                )
            )

        percent = total_affected * 100 / total
        self.det_percent.value = f"{percent:.0f}%"
        self.det_progress_bar.value = total_affected / total

        if 0 < percent < 33:
            self.det_progress_bar.color = 'deeporange'
        elif 33 <= percent < 66:
            self.det_progress_bar.color = 'amber'
        elif 66 <= percent < 100:
            self.det_progress_bar.color = 'green'
        else:
            self.det_progress_bar.color = ft.Colors.LIGHT_GREEN


        self.cp.page.update()

    def open_details_window(self, e):
        self.run_async_in_thread(self.load_details(e))

    def close_details_window(self, e):
        self.det_class.value = None
        self.det_percent.value = None
        self.det_table.rows.clear()
        self.det_progress_bar.value = None

        self.hide_one_window(self.details_window)





