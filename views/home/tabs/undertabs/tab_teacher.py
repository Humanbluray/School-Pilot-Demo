import flet as ft
from PIL.ImageChops import difference

from utils.couleurs import *
from utils.styles import *
from components import *
from translations.translations import languages
import asyncio, threading
from services.supabase_client import supabase_client
from services.async_functions.teachers_functions import *
from services.async_functions.students_functions import get_current_year_id

days = ['day 1', 'day 2', 'day 3', 'day 4', 'day 5']
slots = ['07:30-08:30', '08:30-09:30', '09:30-10:30', '10:45-11:45', '11:45-12:45', '13:00-14:00', '14:00-15:00', '15:00-16:00']


class TabTeacher(ft.Tab):
    def __init__(self, cp: object,):
        super().__init__(
        )
        self.cp = cp
        lang = self.cp.cp.language
        self.lang = lang
        self.filtered_subjects: list = []
        self.tab_content=ft.Row(
            expand=True,
            controls=[
                ft.Icon(ft.Icons.PERSON_OUTLINED, size=20),
                ft.Text(languages[lang]['teacher view'].upper(), size=13, font_family="Poppins Medium")
            ]
        )
        self.year_id = get_current_year_id()
        self.search_prof = ft.Dropdown(
            **drop_style, width=300, prefix_icon='person_outlined', label=languages[lang]['name'],
            on_change=self.on_search_change, menu_height=200
        )
        self.assign_button = MyButton(
            languages[self.cp.lang]['assign several slots'], ft.Icons.PLAYLIST_ADD_CHECK_OUTLINED, 250,
            self.open_multi_affectation_window
        )
        self.prof_id = ft.Text(size=12, font_family="PPM", visible=False)
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
                        controls=[
                            self.search_prof,
                            self.prof_id
                        ]
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

        # New affectation window _________________________________________
        self.new_prof = ft.Text(size=16, font_family='PPL')
        self.new_prof_id = ft.Text(visible=True)
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
        self.new_class = ft.Dropdown(
            **drop_style, width=200, label=languages[lang]['class'], prefix_icon='roofing',
            on_change=self.on_class_change, menu_height=200,
            options=[ft.dropdown.Option(key=" ", text=f"{languages[self.cp.lang]['select option']}")],
            value=" "
        )
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
                                    ft.Row([self.new_prof, self.new_prof_id,], visible=False),
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
                                            ft.Text(languages[lang]['class and subject'].upper(), size=12, font_family='PPB'),
                                            ft.Divider(),
                                        ], spacing=0
                                    ),
                                    ft.Container(
                                        bgcolor='#f0f0f6', border_radius=8, padding=10,
                                        content=ft.Column(
                                            controls=[
                                                self.new_class,
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value=f"{languages[self.cp.lang]['class availability check']}",
                                                            size=12, font_family='PPM'),
                                                        self.check_validity
                                                    ]
                                                ),
                                            ]
                                        )
                                    ),
                                    self.new_level,
                                    ft.Container(
                                        bgcolor='#f0f0f6', border_radius=8, padding=10,
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
                                            [MyButton(languages[lang]['valid'], None, 150, self.validate_affectation)]
                                        )
                                    )
                                ]
                            ),
                        )
                    ], spacing=0
                )
            )
        )

        # Multiple affectations___________________________________________________________
        self.multi_prof = ft.Text(size=16, font_family='PPL')
        self.multi_prof_id = ft.Text(visible=True)
        self.multi_class = ft.Dropdown(
            **drop_style, width=300, label=languages[lang]['class'], prefix_icon='roofing',
            on_change=self.on_multi_class_change, menu_height=200,
            options=[ft.dropdown.Option(key=" ", text=f"{languages[self.cp.lang]['select option']}...")],
            value=" ",
        )
        self.multi_level = ft.TextField(
            **cool_style, width=300, label=languages[lang]['level'], visible=False
        )
        self.multi_subject = ft.Dropdown(
            **drop_style, width=300, label=languages[lang]['subject'], prefix_icon='book_outlined',
            options=[ft.dropdown.Option(key=" ", text=f"{languages[self.cp.lang]['select option']}...")],
            on_change=self.on_subject_change, value=" "
        )
        self.multi_affectation_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=10, border_radius=16, width=500, height=400, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.all(1, CT_BORDER_COLOR),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new affectation'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_multi_affectation_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.all(1, CT_BORDER_COLOR),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                            content=ft.Column(
                                controls=[
                                    ft.Row([self.multi_prof, self.multi_prof_id, ], visible=False),
                                    self.multi_class,
                                    ft.Divider(color='transparent'),
                                    self.multi_level,
                                    self.multi_subject,
                                    ft.Container(
                                        padding=ft.padding.only(10, 0, 10, 0),
                                        content=ft.Row(
                                            [MyButton(languages[lang]['valid'], None, 150, self.validate_affectation)]
                                        )
                                    )
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
                self.main_window, self.multi_affectation_window, self.new_affectation_window
            ], alignment=ft.alignment.center
        )
        self.on_mount()

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

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_datas(self):
        access_token = self.cp.cp.page.client_storage.get('access_token')
        teachers_names = await get_all_teachers(access_token)
        
        for teacher in teachers_names:
            self.search_prof.options.append(
                ft.dropdown.Option(
                    key=teacher['id'], text=f"{teacher['name']} {teacher['surname']}".upper()
                )
            )

        classes = await get_all_classes_basic_info(access_token)
        for item in classes:
            self.new_class.options.append(
                ft.dropdown.Option(
                    key = item['id'], text=f"{item['code']}"
                )
            )

        for item in classes:
            self.multi_class.options.append(
                ft.dropdown.Option(
                    key = item['id'], text=f"{item['code']}"
                )
            )

        self.cp.cp.page.update()

    async def filter_on_teacher(self, e):
        self.new_subject.options.clear()
        self.multi_subject.options.clear()
        self.prof_id.value = self.search_prof.value
        access_token = self.cp.cp.page.client_storage.get('access_token')

        # on récupère toutes les matières enseignées par le professeur...
        teachers = await get_all_teachers(access_token)
        filtered_teacher = list(filter(lambda x: self.prof_id.value in x['id'], teachers))[0]
        filtered_subjects = filtered_teacher['subjects']

        for subject in filtered_subjects:
            self.filtered_subjects.append(subject)

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.controls.clear()
            widget.update()

        all_affectations = await get_teacher_affectations_details(self.search_prof.value, access_token)

        for day in days:
            for slot in slots:
                filtered_datas = list(filter(lambda x: slot in x['slot'] and day in x['day'], all_affectations))

                if filtered_datas:
                    card = SlotCard(self, filtered_datas[0])
                else:
                    card = SlotCard(
                        self, {
                            "id": None,
                            "day": day,
                            "slot": slot,
                            "teacher_id": None,
                            "teacher_name": None,
                            "subject_id": None,
                            "subject_name": None,
                            "subject_short_name": None,
                            "class_id": None,
                            "class_code": None,
                            "status": False
                        }
                    )
                if day == "day 1":
                    self.monday.controls.append(card)

                elif day == 'day 2':
                    self.tuesday.controls.append(card)

                elif day == 'day 3':
                    self.wednesday.controls.append(card)

                elif day == 'day 4':
                    self.thursday.controls.append(card)

                else:
                    self.friday.controls.append(card)

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.update()
            print(len(widget.controls))

        self.cp.cp.page.update()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_on_teacher(e))

    async def update_current_view(self):
        self.prof_id.value = self.search_prof.value
        print(self.prof_id.value)
        access_token = self.cp.cp.page.client_storage.get('access_token')

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.controls.clear()
            widget.update()

        all_affectations = await get_teacher_affectations_details(self.search_prof.value, access_token)

        for day in days:
            for slot in slots:
                filtered_datas = list(filter(lambda x: slot in x['slot'] and day in x['day'], all_affectations))

                if filtered_datas:
                    card = SlotCard(self, filtered_datas[0])
                else:
                    card = SlotCard(
                        self, {
                            "id": None,
                            "day": day,
                            "slot": slot,
                            "teacher_id": None,
                            "teacher_name": None,
                            "subject_id": None,
                            "subject_name": None,
                            "subject_short_name": None,
                            "class_id": None,
                            "class_code": None,
                            "status": False
                        }
                    )
                if day == "day 1":
                    self.monday.controls.append(card)

                elif day == 'day 2':
                    self.tuesday.controls.append(card)

                elif day == 'day 3':
                    self.wednesday.controls.append(card)

                elif day == 'day 4':
                    self.thursday.controls.append(card)

                else:
                    self.friday.controls.append(card)

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            widget.update()
            print(len(widget.controls))

        self.cp.cp.page.update()

    def refresh_view(self):
        self.run_async_in_thread(self.update_current_view())

    def on_class_change(self, e):
        self.run_async_in_thread(self.filter_by_class(e))

    async def filter_by_class(self, e):
        access_token = self.cp.cp.page.client_storage.get('access_token')
        level = await get_level_by_class_id(self.new_class.value, access_token)

        self.new_level.value = level['level_id']
        self.new_level.update()

        # on trouve toutes les matières liées à ce level
        subjects = await get_subjects_by_level_id(level['level_id'], access_token)
        self.new_subject.options.clear()
        for subject in subjects:
            if subject['short_name'] in self.filtered_subjects:
                self.new_subject.options.append(
                    ft.dropdown.Option(
                        key=subject['id'], text=f"{subject['short_name']}"
                    )
                )

        self.new_subject.update()

        # on vérifie la disponibilité du créneau pour la classe...
        status = await is_class_slot_occupied(self.new_class.value, self.new_day.value, self.new_slot.value, access_token)
        if status['occupied']:
            self.check_validity.name = "close"
            self.check_validity.color = "red"
            self.check_validity.update()
        else:
            self.check_validity.name = "check_circle"
            self.check_validity.color = "green"
            self.check_validity.update()

    def validate_affectation(self, e):
        if self.new_class.value is None or self.new_subject.value is None:
            self.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.box.content.value = languages[self.cp.lang]['error msg']
            self.cp.cp.box.open = True
            self.cp.cp.box.update()

        else:
            if self.check_validity.name == 'check_circle' and self.check_validity_load.name == 'check_circle':
                supabase_client.table('affectations').update(
                    {
                        'subject_id': self.new_subject.value,
                        "teacher_id": self.prof_id.value,
                    }
                ).eq('day', self.new_day.value).eq('slot', self.new_slot.value).eq(
                    "class_id", self.new_class.value).eq('year_id', self.year_id).execute()

                self.hide_one_window(self.new_affectation_window)

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

                for widget in (self.check_validity, self.check_validity_load):
                    widget.name = None
                    widget.color = None
                    widget.update()

                self.refresh_view()

            elif self.check_validity.name == 'close' and self.check_validity_load.name == 'check_circle':
                self.cp.cp.box.title.value = languages[self.cp.lang]['error']
                self.cp.cp.box.content.value = languages[self.cp.lang]['slot class busy']
                self.cp.cp.box.open = True
                self.cp.cp.box.update()

            elif self.check_validity.name == 'check_circle' and self.check_validity_load.name == 'close':
                self.cp.cp.box.title.value = languages[self.cp.lang]['error']
                self.cp.cp.box.content.value = languages[self.cp.lang]['hourly load exceeded']
                self.cp.cp.box.open = True
                self.cp.cp.box.update()

            else:
                self.cp.cp.box.title.value = languages[self.cp.lang]['error']
                self.cp.cp.box.content.value = (f"{languages[self.cp.lang]['slot class busy']}\n"
                                                f"{languages[self.cp.lang]['hourly load exceeded']}")
                self.cp.cp.box.open = True
                self.cp.cp.box.update()

    def on_subject_change(self, e):
        self.run_async_in_thread(self.on_filter_subject(e))

    async def on_filter_subject(self, e):
        access_token = self.cp.cp.page.client_storage.get('access_token')
        hourly_load = await get_hourly_load_by_subject_id(self.new_subject.value, access_token)
        nb_affectations = await count_affectations_by_subject_and_class(self.new_subject.value, self.new_class.value, access_token)

        if nb_affectations >= hourly_load:
            self.check_validity_load.name = 'close'
            self.check_validity_load.color = 'red'
            self.check_validity_load.update()
        else:
            self.check_validity_load.name = 'check_circle'
            self.check_validity_load.color = 'green'
            self.check_validity_load.update()

    def close_new_affectation_window(self, e):
        self.new_subject.value = " "
        self.new_class.value = " "
        self.hide_one_window(self.new_affectation_window)

    def open_multi_affectation_window(self, e):
        count_checked = 0
        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            for item in widget.controls:
                if item.check.value:
                    count_checked += 1

        if count_checked < 2:
            self.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.box.content.value = languages[self.cp.lang]['slots checked required']
            self.cp.cp.box.open = True
            self.cp.cp.box.update()

        elif self.prof_id.value is None:
            self.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.box.content.value = languages[self.cp.lang]['no teacher selected']
            self.cp.cp.box.open = True
            self.cp.cp.box.update()

        else:
            self.multi_affectation_window.scale = 1
            self.main_window.opacity = 0.6
            self.main_window.disabled = True
            self.cp.cp.left_menu.opacity = 0.6
            self.cp.cp.left_menu.disabled = True
            self.multi_subject.options.clear()
            self.cp.page.update()

    def close_multi_affectation_window(self, e):
        self.multi_affectation_window.scale = 0
        self.main_window.opacity = 0.6
        self.main_window.disabled = True
        self.cp.cp.left_menu.opacity = 0.6
        self.cp.cp.left_menu.disabled = True
        self.new_subject.options.clear()
        self.cp.page.update()

    async def filter_by_multi_class(self, e):
        access_token = self.cp.cp.page.client_storage.get('access_token')
        level = await get_level_by_class_id(self.multi_class.value, access_token)

        self.multi_level.value = level['level_id']
        self.multi_level.update()

        # on trouve toutes les matières liées à ce level
        subjects = await get_subjects_by_level_id(level['level_id'], access_token)
        self.multi_subject.options.clear()
        for subject in subjects:
            if subject['short_name'] in self.filtered_subjects:
                self.multi_subject.options.append(
                    ft.dropdown.Option(
                        key=subject['id'], text=f"{subject['short_name']}"
                    )
                )

        self.multi_subject.update()

    def on_multi_class_change(self, e):
        self.run_async_in_thread(self.filter_by_multi_class(e))

    async def create_multi_affectations(self, e):
        errors: list = []
        selected_prof_id = self.multi_prof_id.value
        selected_class_id = self.multi_class.value
        subject_id = self.multi_subject.value
        access_token = self.cp.cp.page.client_storage.get('access_token')
        level = await get_level_by_class_id(self.new_class.value, access_token)
        level_id = level['level_id']

        for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
            for item in widget.controls:
                if item.check.value:
                    slot = item.infos['slot']
                    day = item.infos['day']

                    # Check class slot availability...
                    class_status = await is_class_slot_occupied(
                        selected_class_id, day, slot, access_token
                    )

                    # check the load...
                    hourly_load = await get_hourly_load_by_subject_id(
                        self.multi_subject.value, access_token
                    )
                    nb_affectations = await count_affectations_by_subject_and_class(
                        self.multi_subject.value, selected_class_id, access_token
                    )
                    max_hours = hourly_load - nb_affectations


                    if class_status['occupied'] and max_hours > 0:
                        errors.append(
                            {"nature": "slot availability", "details": f"{languages[self.cp.lang]['slot class busy']}"}
                        )

                    elif class_status['occupied'] and max_hours == 0:
                        errors.append(
                            {"nature": "slot availability", "details": f"{languages[self.cp.lang]['slot class busy']}"}
                        )
                        errors.append(
                            {"nature": "hourly laod", "details": f"{languages[self.cp.lang]['hourly load exceeded']}"}
                        )

                    elif class_status['occupied'] is False and max_hours == 0:
                        errors.append(
                            {"nature": "hourly laod", "details": f"{languages[self.cp.lang]['hourly load exceeded']}"}
                        )

                    else:
                        pass

        if len(errors) > 0:
            text_error = ""

            for error in errors:
                text_error = text_error + f"\n{error['details']}"

            self.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.box.content.value = text_error
            self.cp.cp.box.open = True
            self.cp.cp.box.update()
        else:
            for widget in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
                for item in widget.controls:
                    if item.check.value:
                        slot = item.infos['slot']
                        day = item.infos['day']

                        supabase_client.table('affectations').update(
                            {'teacher_id': selected_prof_id, 'subject_id': subject_id}
                        ).eq('class_id', selected_class_id).eq('year_id', self.year_id).eq(
                            'day', day
                        ).eq('slot', slot).execute()

            self.cp.cp.box.title.value = languages[self.cp.lang]['success']
            self.cp.cp.box.content.value = languages[self.cp.lang]['successful assignment']
            self.cp.cp.box.open = True
            self.cp.cp.box.update()

    def validate_multiple_affectations(self, e):
        self.run_async_in_thread(self.create_multi_affectations(e))












