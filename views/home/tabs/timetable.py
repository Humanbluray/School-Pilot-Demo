from utils.couleurs import *
from services.async_functions.students_functions import get_current_year_label
from views.home.tabs.undertabs.tab_teacher import TabTeacher
from views.home.tabs.undertabs.tab_classes import TabClasses


class Schedule(ft.Container):
    def __init__(self, cp: object):
        super().__init__(expand=True)

        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        self.current_year_label = ft.Text(f"{get_current_year_label()}", size=11, color='indigo', font_family="PPM")
        self.content = ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Container(
                        expand=True, border_radius=10, bgcolor='white',
                        padding=20,
                        content=ft.Tabs(
                            tab_alignment=ft.TabAlignment.START, selected_index=0, expand=True, animation_duration=300,
                            unselected_label_color=ft.Colors.GREY, label_color='black',
                            indicator_border_radius=30, indicator_border_side=ft.BorderSide(5, BASE_COLOR),
                            indicator_tab_size=True,
                            tabs=[TabTeacher(self), TabClasses(self)],
                        )
                    ),
                ]
            )
        )
