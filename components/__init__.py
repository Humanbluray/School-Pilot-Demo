import flet as ft
from utils.couleurs import *
from utils.styles import *
from translations.translations import languages
from services.supabase_client import supabase_client
import asyncio, threading

day_color = {
    'day 1' : {'fg_color': 'deeporange', 'bg_color': 'deeporange50'},
    'day 2' : {'fg_color': 'teal', 'bg_color': 'teal50'},
    'day 3' : {'fg_color': 'indigo', 'bg_color': 'indigo50'},
    'day 4' : {'fg_color': 'deeppurple', 'bg_color': 'deeppurple50'},
    'day 5' : {'fg_color': 'brown', 'bg_color': 'brown50'},
}
day_short_name = {
    'day 1' : {'en': 'MON', 'fr': 'LUN'},
    'day 2' : {'en': 'TUE', 'fr': 'MAR'},
    'day 3' : {'en': 'WED', 'fr': 'MER'},
    'day 4' : {'en': 'THU', 'fr': 'JEU'},
    'day 5' : {'en': 'FRI', 'fr': 'VEN'},
}


class BarGraphic(ft.BarChart):
    def __init__(self, infos: list, max_value: int):
        super().__init__(
            bar_groups=[
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=infos[i]['value'],
                            width=30,  # Largeur de la barre
                            color=infos[i]['color'],  # Couleur principale
                            tooltip=infos[i]['label'],
                            border_radius=24,  # Bords arrondis
                            bg_to_y=max_value + 10,  # Hauteur de la zone de fond
                            bg_color=infos[i]['bg_color'],  # Couleur de fond
                        )
                    ]
                )
                for i in range(len(infos))
            ],

            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=i, label=ft.Text(infos[i]['label'].upper(), size=11, font_family='PPI', color='grey'))
                    for i in range(len(infos))
                ],
                labels_size=40,
            ),
            max_y=max_value + 10,  # Définit la hauteur maximale de l'axe Y
            interactive=True,
            expand=True,
        )


class OnePieGraphic(ft.PieChart):
    def __init__(self, infos: dict):
        super().__init__(
            sections=[
                ft.PieChartSection(
                    value=infos['value'],
                    title_style=ft.TextStyle(size=13, font_family="PPM", color='black'),
                    color='amber',
                    radius=35,
                ),
                ft.PieChartSection(
                    value=100-infos['value'],
                    title='',
                    color='amber50',
                    radius=35,
                ),
            ],
            sections_space=0,
            center_space_radius=40,
            expand=True, scale=0.8
        )


class MyButton(ft.ElevatedButton):
    def __init__(self, title: str, my_icon, my_width, click):
        super().__init__(
            scale=ft.Scale(1), bgcolor=MAIN_COLOR, on_hover=self.hover_effect, on_click=click,
            animate_scale=ft.Animation(300, ft.AnimationCurve.FAST_OUT_SLOWIN),
            elevation=0, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER, height=40,
        )
        self.title = title
        self.my_width = my_width
        self.click = click
        self.my_icon = my_icon
        visible = False if my_icon is None else True

        self.content = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(my_icon, size=18, visible=visible, color='black'),
                    ft.Text(title.lower().capitalize(), size=13, font_family="PPM", color='black'),
                ], alignment=ft.MainAxisAlignment.CENTER,
            ), width=my_width, border_radius=10
        )

    def hover_effect(self, e):
        if e.data == 'true':
            self.scale = 1.05
            self.update()
        else:
            self.scale = 1
            self.update()


class FlatButton(ft.Container):
    def __init__(self, title: str, my_icon, my_width, click):
        super().__init__(
            padding=10, bgcolor=None, height=40, width=my_width, border_radius=6, on_hover=self.hover_effect,
            on_click=click, tooltip=title, border=ft.border.all(1, 'black38')
        )
        self.title = title
        self.my_width = my_width
        self.click = click
        self.my_icon = my_icon
        visible = False if my_icon is None else True

        self.content = ft.Row(
            controls=[
                ft.Icon(my_icon, size=18, visible=visible, color='black54'),
            ], alignment=ft.MainAxisAlignment.CENTER,
        )

    def hover_effect(self, e):
        if e.data == 'true':
            self.scale = 1.04
            self.update()
        else:
            self.scale = 1
            self.update()


class TopMenuButton(ft.Container):
    def __init__(self, my_icon, click):
        super().__init__(
            padding=10, bgcolor=SECOND_COLOR, height=55,
            on_click=click, shape=ft.BoxShape.CIRCLE
        )
        self.my_icon = my_icon
        self.content = ft.Row(
            controls=[
                ft.Icon(my_icon, size=24, color=MAIN_COLOR),
            ], alignment=ft.MainAxisAlignment.CENTER,
        )


class DateSelection(ft.Row):
    def __init__(self, cp):
        super().__init__()
        self.cp = cp
        self.day = ft.Dropdown(
            **drop_style, width=95, text_align=ft.TextAlign.RIGHT, menu_height=200,
            options=[ft.dropdown.Option(f"{i}") for i in range(1, 32)], hint_text=languages[self.cp.lang]['jj']
        )
        self.month = ft.Dropdown(
            **drop_style, width=95, text_align=ft.TextAlign.RIGHT, hint_text=languages[self.cp.lang]['mm'],
            menu_height=200,
            options=[ft.dropdown.Option(f"{i}") for i in range(1, 13)]
        )
        self.year = ft.TextField(
            height=50, hint_text=languages[self.cp.lang]['yyyy'],
            focused_border_width=1, focused_border_color=END_COLOR,
            label_style=ft.TextStyle(size=11, font_family="PPM", color="black"),
            hint_style=ft.TextStyle(size=12, font_family="PPM"),
            text_style=ft.TextStyle(size=13, font_family="PPM"), cursor_color='black',
            border_radius=6, border_width=1, capitalization=ft.TextCapitalization.CHARACTERS,
            input_filter=ft.NumbersOnlyInputFilter(), width=80, text_align=ft.TextAlign.RIGHT,
        )
        self.controls=[
            ft.Row(
                controls=[
                    self.day, self.month, self.year
                ], spacing=3
            )
        ]


class MyIconButton(ft.Container):
    def __init__(self, icon: str, text: str, couleur: str, click):
        super().__init__(
            border_radius=10, alignment=ft.alignment.center,
            border=ft.border.all(1, couleur), padding=5,
            content=ft.Icon(name=icon, size=24, color='black87'), on_click=click,
            on_hover=self.hover_effect, tooltip=text,
            scale=ft.Scale(1), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN)
        )

    def hover_effect(self, e):
        if e.data == "true":
            self.scale = 1.1
        else:
            self.scale = 1
        self.update()


class MyMiniIcon(ft.Container):
    def __init__(self, icon: str, text: str, color:str, data, click):
        super().__init__(
            border_radius=6, alignment=ft.alignment.center,
            padding=5,
            content=ft.Icon(name=icon, size=24, color=color), on_click=click,
            on_hover=self.hover_effect, tooltip=text, data=data,
            scale=ft.Scale(1), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN)
        )

    def hover_effect(self, e):
        if e.data == "true":
            self.scale = 1.1
        else:
            self.scale = 1
        self.update()


class ColoredIcon(ft.Container):
    def __init__(self, my_icon: str,color: str, bg_color: str):
        super().__init__(
            bgcolor=bg_color, alignment=ft.alignment.center, padding=5,
            # border=ft.border.all(1, color),
            width=30, height=30, shape=ft.BoxShape.CIRCLE,
            content=ft.Icon(my_icon, size=14, color=color), scale=0.9
        )


class ColoredButton(ft.Container):
    def __init__(self, text: str,icon: str, click):
        super().__init__(
            border_radius=12, alignment=ft.alignment.center, padding=10,
            on_click=click, bgcolor='#f0f0f6',
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=16, color='black'),
                    ft.Text(text, size=12, font_family='PPM', color='black')
                ], alignment=ft.MainAxisAlignment.CENTER
            ), on_hover=self.on_hover_effect
        )

    def on_hover_effect(self, e):
        if e.data == 'true':
            self.bgcolor = BASE_COLOR
            self.update()
        else:
            self.bgcolor = '#f0f0f6'
            self.update()


class ColoredIconButton(ft.Container):
    def __init__(self, icone: str, text: str,color: str, bg_color: str, click):
        super().__init__(
            border_radius=6, alignment=ft.alignment.center, padding=8, tooltip=text,
            border=ft.border.all(1, color), on_click=click, on_hover=self.hover_effect,
            content=ft.Row(
                controls=[
                    ft.Icon(icone, size=16, color=color)
                ], alignment=ft.MainAxisAlignment.CENTER
            ), scale=0.9
        )
        self.color = color
        self.bg_color = bg_color

    def hover_effect(self, e):
        if e.data == "true":
            self.bgcolor = self.bg_color
        else:
            self.bgcolor = None

        self.update()


class IndicatorIcon(ft.Container):
    def __init__(self, my_icon: str):
        super().__init__(
            bgcolor=MAIN_COLOR, border_radius=6, alignment=ft.alignment.center, padding=5,
            width=30, height=30,
            content=ft.Icon(my_icon, size=16, color='white'),
        )


class SingleOption(ft.Container):
    def __init__(self, cp: object, name: str):
        super().__init__(
            bgcolor='grey100',
            alignment=ft.alignment.center, border_radius=7, on_click=self.set_status,
            padding=ft.padding.only(5, 3, 5, 3)
        )
        self.cp = cp
        self.name = name
        self.selected: bool = False
        self.element = ft.Text(name, size=11, font_family='PPM', color='black54')
        self.content=self.element

    def set_status(self, e):
        if self.selected:
            self.selected = False
            self.bgcolor = 'grey100'
            self.element.color = 'black54'
            self.element.update()
            self.cp.count_subject.value = int(self.cp.count_subject.value) - 1 if int(self.cp.count_subject.value) > 0 else 0
            self.cp.count_subject.update()
            self.update()
        else:
            self.selected = True
            self.bgcolor = EMERALD_GREEN
            self.element.color = 'white'
            self.element.update()
            self.cp.count_subject.value = int(self.cp.count_subject.value) + 1
            self.cp.count_subject.update()
            self.update()

    def set_initial(self):
        self.selected = True
        self.bgcolor = 'grey100'
        self.element.color = 'black54'
        self.element.update()
        self.update()

    def set_selected(self):
        self.selected = True
        self.bgcolor = EMERALD_GREEN
        self.element.color = 'white'
        self.element.update()
        self.update()


class EditSingleOption(ft.Container):
    def __init__(self, cp: object, name: str):
        super().__init__(
            bgcolor='#f0f0f6',
            alignment=ft.alignment.center, border_radius=7, on_click=self.set_status,
            padding=ft.padding.only(5, 3, 5, 3)
        )
        self.cp = cp
        self.name = name
        self.selected: bool = False
        self.element = ft.Text(name, size=11, font_family='PPM', color='black')
        self.content = self.element

    def set_status(self, e):
        if self.selected:
            self.selected = False
            self.bgcolor = '#f0f0f6'
            self.element.color = 'black'
            self.element.update()
            self.cp.edit_count_subject.value = int(self.cp.edit_count_subject.value) - 1 if int(
                self.cp.edit_count_subject.value) > 0 else 0
            self.cp.edit_count_subject.update()
            self.update()
        else:
            self.selected = True
            self.bgcolor = EMERALD_GREEN
            self.element.color = 'white'
            self.element.update()
            self.cp.edit_count_subject.value = int(self.cp.edit_count_subject.value) + 1
            self.cp.edit_count_subject.update()
            self.update()

    def set_initial(self):
        self.selected = False
        self.bgcolor = '#f0f0f6'
        self.element.color = 'black'
        self.element.update()
        self.update()

    def set_selected(self):
        self.selected = True
        self.bgcolor = EMERALD_GREEN
        self.element.color = 'white'
        self.element.update()
        self.update()


class SlotCard(ft.Container):
    def __init__(self, cp: object, infos: dict):
        super().__init__(
            border_radius=16, bgcolor = day_color[infos['day']]['bg_color'],
            # border=ft.border.all(1, 'black')
        )
        self.cp = cp
        self.infos = infos
        self.delete_bt = MyMiniIcon('delete_outlined', languages[self.cp.lang]['free slot'], "black", self.infos, self.free_affectation)
        self.assign_bt = MyMiniIcon(ft.Icons.ADD, languages[self.cp.lang]['assign slot'], "black", self.infos, self.add_affectation)
        self.check = ft.Checkbox()
        role = self.cp.cp.page.client_storage.get('role')

        if infos['status']:
            if role not in ['principal', 'préfet']:
                self.status_icon = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                self.status_color = 'red'
                self.delete_bt.visible = False
                self.assign_bt.visible = False
                self.check.disabled = True
                self.visible_bgcolor = day_color[infos['day']]['fg_color']

            else:
                self.status_icon = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                self.status_color = 'red'
                self.delete_bt.visible = True
                self.assign_bt.visible = False
                self.check.disabled = True
                self.visible_bgcolor = day_color[infos['day']]['fg_color']

        else:
            if role not in ['principal', 'préfet']:
                self.status_icon = ft.Icons.CHECK_CIRCLE
                self.status_color = 'green'
                self.delete_bt.visible = False
                self.assign_bt.visible = False
                self.check.disabled = False
                self.visible_bgcolor = 'white'

            else:
                self.status_icon = ft.Icons.CHECK_CIRCLE
                self.status_color = 'green'
                self.delete_bt.visible = False
                self.assign_bt.visible = True
                self.check.disabled = False
                self.visible_bgcolor = 'white'

        self.prof = "" if infos['teacher_id'] is None else infos['teacher_name']
        self.mat = "" if infos['subject_id'] is None else infos['subject_short_name']
        self.class_code = "" if infos['class_id'] is None else infos['class_code']

        self.content = ft.Container(
            border_radius=16, padding=10, width=210,
            content=ft.Column(
                controls=[
                    ft.Container(
                        padding=5, border_radius=8, bgcolor='white', content=ft.Row(
                            controls=[
                                ft.Icon(self.status_icon, size=18, color=self.status_color),
                                ft.Text(languages[self.cp.lang][infos['day']].upper(), size=14, font_family="PPM"),
                            ], alignment=ft.MainAxisAlignment.CENTER
                        )
                    ),
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon('timer_outlined', size=18, color='black45'),
                                    ft.Text(infos['slot'], font_family='PPM', size=14),
                                ]
                            ),
                            ft.Row([self.assign_bt, self.delete_bt])
                        ], alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        padding=8, border_radius=8, expand=True,
                        bgcolor=self.visible_bgcolor,
                        content=ft.Row(
                            controls=[
                                ft.Text(f"{self.mat} - {self.class_code}", size=14, font_family="PPL", color="white"),

                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ), tooltip=f"{languages[self.cp.lang]['day']}: {languages[self.cp.lang][infos['day']]}\n"
                                   f"{languages[self.cp.lang]['slot']}: {infos['slot']}\n"
                                   f"{languages[self.cp.lang]['class']}: {infos['class_code']}\n"
                                   f"{languages[self.cp.lang]['subject']}: {infos['subject_name']}\n"
                                   f"{languages[self.cp.lang]['teacher']}: {infos['teacher_name']}\n"
                    ),
                ]
            )
        )

    @staticmethod
    def run_async_in_thread(coro):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        thread = threading.Thread(target=runner)
        thread.start()

    def add_affectation(self, e):
        self.cp.new_prof_id.value = self.cp.prof_id.value

        self.cp.new_day.value = e.control.data['day']
        self.cp.new_day_display.value = languages[self.cp.lang][e.control.data['day']]
        self.cp.new_slot.value = e.control.data['slot']
        self.cp.new_day.update()
        self.cp.new_day_display.update()
        self.cp.new_slot.update()

        self.cp.new_affectation_window.scale = 1
        self.cp.new_affectation_window.update()
        self.cp.main_window.opacity = 0.2
        self.cp.main_window.disabled = True
        self.cp.main_window.update()
        self.cp.cp.cp.left_menu.opacity = 0.2
        self.cp.cp.cp.left_menu.disabled = True
        self.cp.cp.cp.left_menu.update()

    async def delete_affectation(self, e):
        role = self.cp.cp.page.client_storage.get('role')
        print(role)

        if role in ['principal', 'préfet']:
            # supprimer affectation
            resp = supabase_client.table('affectations').update(
                {
                    "teacher_id": None, "subject_id": None
                }
            ).eq("day", self.infos['day']).eq('slot', self.infos['slot']).eq("year_id", self.infos['year_id']).execute()

            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['success']
            self.cp.cp.cp.box.content.value = languages[self.cp.lang]['free time slot']
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()

            await self.cp.refresh_view()

        else:
            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.cp.box.content.value = languages[self.cp.lang]['error rights']
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()

    def free_affectation(self, e):
        self.run_async_in_thread(self.delete_affectation(e))


class SlotCardRoom(ft.Container):
    def __init__(self, cp: object, infos: dict):
        super().__init__(
            border_radius=16, bgcolor = day_color[infos['day']]['bg_color'],
            # border=ft.border.all(1, 'black')
        )
        self.cp = cp
        self.infos = infos
        self.delete_bt = MyMiniIcon('delete_outlined', languages[self.cp.lang]['free slot'], "black", self.infos, self.delete_affectation)
        self.assign_bt = MyMiniIcon(ft.Icons.ADD, languages[self.cp.lang]['assign slot'], "black", self.infos, self.add_affectation)
        self.check = ft.Checkbox()
        role = self.cp.cp.page.client_storage.get('role')

        if infos['status']:
            if role not in ['principal', 'préfet']:
                self.status_icon = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                self.status_color = 'red'
                self.delete_bt.visible = False
                self.assign_bt.visible = False
                self.check.disabled = True
                self.visible_bgcolor = day_color[infos['day']]['fg_color']

            else:
                self.status_icon = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                self.status_color = 'red'
                self.delete_bt.visible = True
                self.assign_bt.visible = False
                self.check.disabled = True
                self.visible_bgcolor = day_color[infos['day']]['fg_color']

        else:
            if role not in ['principal', 'préfet']:
                self.status_icon = ft.Icons.CHECK_CIRCLE
                self.status_color = 'green'
                self.delete_bt.visible = False
                self.assign_bt.visible = False
                self.check.disabled = False
                self.visible_bgcolor = 'white'

            else:
                self.status_icon = ft.Icons.CHECK_CIRCLE
                self.status_color = 'green'
                self.delete_bt.visible = False
                self.assign_bt.visible = True
                self.check.disabled = False
                self.visible_bgcolor = 'white'

        self.prof = "" if infos['teacher_id'] is None else infos['teacher_name']
        self.mat = "" if infos['subject_id'] is None else infos['subject_short_name']
        self.class_code = "" if infos['class_id'] is None else infos['class_code']

        self.content = ft.Container(
            border_radius=16, padding=10, width=190,
            content=ft.Column(
                controls=[
                    ft.Container(
                        padding=5, border_radius=8, bgcolor='white', content=ft.Row(
                            controls=[
                                ft.Icon(self.status_icon, size=18, color=self.status_color),
                                ft.Text(languages[self.cp.lang][infos['day']].upper(), size=14, font_family="PPM"),
                            ], alignment=ft.MainAxisAlignment.CENTER
                        )
                    ),
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon('timer_outlined', size=18, color='black45'),
                                    ft.Text(infos['slot'], font_family='PPM', size=14),
                                ]
                            ),
                            ft.Row([self.assign_bt, self.delete_bt])
                        ], alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        padding=8, border_radius=8, expand=True,
                        bgcolor=self.visible_bgcolor,
                        content=ft.Row(
                            controls=[
                                ft.Text(f"{self.mat} - {self.prof}", size=14, font_family="PPL", color="white"),

                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        tooltip=f"{languages[self.cp.lang]['day']}: {languages[self.cp.lang][infos['day']]}\n"
                                   f"{languages[self.cp.lang]['slot']}: {infos['slot']}\n"
                                   f"{languages[self.cp.lang]['class']}: {infos['class_code']}\n"
                                   f"{languages[self.cp.lang]['subject']}: {infos['subject_name']}\n"
                                   f"{languages[self.cp.lang]['teacher']}: {infos['teacher_name']}\n"
                    ),
                ]
            )
        )

    @staticmethod
    def run_async_in_thread(coro):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        thread = threading.Thread(target=runner)
        thread.start()

    def add_affectation(self, e):
        role = self.cp.cp.page.client_storage.get('role')

        if role in ['principal', 'préfet']:
            self.cp.new_affectation_id = e.control.data['id']
            self.cp.new_day.value = e.control.data['day']
            self.cp.new_day_display.value = languages[self.cp.lang][e.control.data['day']]
            self.cp.new_slot.value = e.control.data['slot']
            self.cp.new_day.update()
            self.cp.new_day_display.update()
            self.cp.new_slot.update()

            self.cp.new_affectation_window.scale = 1
            self.cp.new_affectation_window.update()
            self.cp.main_window.opacity = 0.2
            self.cp.main_window.disabled = True
            self.cp.main_window.update()
            self.cp.cp.cp.left_menu.opacity = 0.2
            self.cp.cp.cp.left_menu.disabled = True
            self.cp.cp.cp.left_menu.update()

        else:
            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.cp.box.content.value = languages[self.cp.lang]['error rights']
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()



    def delete_affectation(self, e):
        role = self.cp.cp.page.client_storage.get('role')

        if role in ['principal', 'préfet']:
            # supprimer affectation
            resp = supabase_client.table('affectations').update(
                {
                    "teacher_id": None, "subject_id": None
                }
            ).eq('id', self.infos['id']).execute()

            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['success']
            self.cp.cp.cp.box.content.value = languages[self.cp.lang]['free time slot']
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()

            self.cp.refresh_view()

        else:
            self.cp.cp.cp.box.title.value = languages[self.cp.lang]['error']
            self.cp.cp.cp.box.content.value = languages[self.cp.lang]['error rights']
            self.cp.cp.cp.box.open = True
            self.cp.cp.cp.box.update()


class BoxStudentNote(ft.Container):
    def __init__(self, infos: dict):
        super().__init__(
            padding=ft.padding.only(10, 5, 10, 5), data=infos,
        )
        self.check = ft.Icon(size=16)
        self.infos = infos
        self.my_note = ft.TextField(
            **cool_style, width=70,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]", replacement_string=""),
            text_align=ft.TextAlign.RIGHT, on_blur=self.on_note_change
        )
        self.my_name = ft.Text(f"{infos['name']} {infos['surname']}".upper(), size=13, font_family='PPM', data=infos)
        self.content = ft.Row(
            controls=[
                self.my_name,
                ft.Row([self.my_note, self.check], spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def on_note_change(self, e):
        if float(self.my_note.value) > 20:
            self.check.name = ft.Icons.DANGEROUS
            self.check.color = 'red'

        elif self.my_note.value is None:
            pass

        else:
            self.check.name = ft.Icons.CHECK_CIRCLE
            self.check.color = ft.Colors.LIGHT_GREEN

        self.check.update()







