from components import MyButton, ColoredIconButton, ColoredButton, MyMiniIcon, SingleOption, EditSingleOption, ColoredIcon
from utils.styles import drop_style, datatable_style, numeric_style, cool_style
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading, json
from services.async_functions.users_functions import *
from utils.useful_functions import add_separator, format_number


class Users(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True
        )
        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # KPI _________________________________________________
        self.nb_users = ft.Text(size=28, font_family="PPM", weight=ft.FontWeight.BOLD)

        self.ct_nb_users = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'indigo', 'indigo50'),
                            ft.Text(languages[lang]['total'].upper(), size=12, font_family='PPI', color='indigo')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.nb_users,
                            ft.Text(languages[lang]['nb users'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ]
            )
        )

        # Main window...
        self.search = ft.TextField(
            **cool_style, width=300, label=f"{languages[lang]['search']}", prefix_icon='search',
            on_change=self.on_search_change
        )
        self.table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(menu)) for menu in [
                    languages[lang]['name'].capitalize(), languages[lang]['email'].capitalize(),
                    languages[lang]['function'].capitalize(), languages[lang]['role'].capitalize(),
                    languages[lang]['contact'].capitalize(), 'Actions'
                ]
            ]
        )

        self.main_window = ft.Container(
            expand=True, content=ft.Column(
                expand=True, controls=[
                    # Kpi..
                    ft.Row(
                        controls=[
                            self.ct_nb_users,
                            ft.VerticalDivider()
                        ]
                    ),
                    # datas...
                    ft.Row(
                        expand=True,
                        controls=[
                            ft.Container(
                                padding=0, border_radius=16, border=ft.border.all(1, 'white'),
                                expand=True, bgcolor='white', content=ft.Column(
                                    controls=[
                                        ft.Container(
                                            padding=20, content=ft.Row(
                                                controls=[
                                                    ColoredButton(
                                                        languages[lang]['new user'], "person_add_outlined", self.open_new_user_window
                                                    ),
                                                    self.search
                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            )
                                        ),
                                        ft.Divider(color=ft.Colors.TRANSPARENT),
                                        ft.ListView(expand=True, controls=[self.table])
                                    ]
                                )
                            ),
                        ]
                    )
                ]
            )
        )

        # new user window...
        self.new_name = ft.TextField(
            **cool_style, width=300, prefix_icon=ft.Icons.PERSON_OUTLINED
        )
        self.new_surname = ft.TextField(
            **cool_style, width=300, prefix_icon=ft.Icons.PERSON_OUTLINED
        )
        self.new_email = ft.TextField(
            **cool_style, width=300, prefix_icon=ft.Icons.MAIL_OUTLINED
        )
        self.new_contact = ft.TextField(
            **cool_style, width=180, prefix_icon=ft.Icons.PHONE_ANDROID_OUTLINED, prefix_text='+237'
        )
        self.new_function = ft.TextField(
            **cool_style, width=300, prefix_icon=ft.Icons.FUNCTIONS_OUTLINED
        )
        self.new_role = ft.RadioGroup(
            content=ft.Column(
                controls=[
                    ft.Radio(
                        label=option['label'], value=option['value'],
                        label_style=ft.TextStyle(size=13, font_family='PPM')
                    )
                        for option in [
                            {'label': languages[lang]['bursar'], 'value': 'économe'},
                            {'label': languages[lang]['secretary'], 'value': 'secrétaire'},
                            {'label': languages[lang]['teacher'], 'value': 'professeur'},
                            {'label': languages[lang]['principal'], 'value': 'principal'},
                            {'label': languages[lang]['prefect of studies'], 'value': 'préfet'},
                            {'label': languages[lang]['administrator'], 'value': 'admin'},
                        ]
                ]
            )
        )
        self.new_user_container = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN), expand=True,
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=700, height=750, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20,
                            border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['new student'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_new_user_window
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
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['name'], size=11, font_family='PPM', color='grey'),
                                                    self.new_name
                                                ],spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['surname'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_surname
                                                ], spacing=2
                                            )
                                        ]
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['email'], size=11, font_family='PPM', color='grey'),
                                                    self.new_email
                                                ],spacing=2
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(languages[lang]['contact'], size=11, font_family='PPM',
                                                            color='grey'),
                                                    self.new_contact
                                                ], spacing=2
                                            )
                                        ]
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(languages[lang]['function'], size=11, font_family='PPM', color='grey'),
                                            self.new_function
                                        ], spacing=2
                                    ),
                                    self.new_role,
                                    ft.Container(
                                        padding=10,
                                        content=ft.Row(
                                            controls=[
                                                MyButton(languages[lang]['valid'], 'check', None, self.create_new_user)
                                            ]
                                        )
                                    )

                                ]
                            )
                        )
                    ]
                )
            )
        )

        self.content = ft.Stack(
            controls=[
                self.main_window, self.new_user_container
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
        await self.load_datas()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_datas(self):
        access_token = self.cp.page.client_storage.get('access_token')
        datas = await get_all_users(access_token)

        self.table.rows.clear()

        for data in datas:
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{data['name']} {data['surname']}".upper())),
                        ft.DataCell(ft.Text(f"{data['email']}")),
                        ft.DataCell(ft.Text(f"{data['function']}")),
                        ft.DataCell(ft.Text(f"{data['role']}")),
                        ft.DataCell(ft.Text(f"{data['contact']}")),
                        ft.DataCell(ft.Row(
                            controls=[
                                MyMiniIcon('edit_outlined', '', 'grey', data, None),
                                MyMiniIcon(ft.Icons.FORMAT_LIST_BULLETED_SHARP, '', 'grey', data, None),
                            ], spacing=0
                        )),
                    ]
                )
            )

        self.cp.page.update()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    async def filter_datas(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        datas = await get_all_users(access_token)
        search = self.search.value if self.search.value else ''

        filtered_datas = list(filter(lambda x: search in x['name'] or search in x['surname'], datas))
        self.table.rows.clear()

        for data in filtered_datas:
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{data['name']} {data['surname']}".upper())),
                        ft.DataCell(ft.Text(f"{data['email']}")),
                        ft.DataCell(ft.Text(f"{data['function']}")),
                        ft.DataCell(ft.Text(f"{data['role']}")),
                        ft.DataCell(ft.Text(f"{data['contact']}")),
                        ft.DataCell(ft.Row(
                            controls=[
                                MyMiniIcon('edit_outlined', '', 'grey', data, None),
                                MyMiniIcon(ft.Icons.FORMAT_LIST_BULLETED_SHARP, '', 'grey', data, None),
                            ], spacing=0
                        )),
                    ]
                )
            )

        self.cp.page.update()

    def open_new_user_window(self, e):
        self.show_one_window(self.new_user_container)

    def close_new_user_window(self, e):
        self.hide_one_window(self.new_user_container)

        for widget in (self.new_name, self.new_surname, self.new_function, self.new_contact,
                       self.new_email, self.new_role):
            widget.value = None
            widget.update()

    def create_new_user(self, e):
        try:
            # send invitation
            response = supabase_client.auth.admin.invite_user_by_email(
                email=self.new_email.value,
                redirect_to=app_url
            )
            user = response.user

            if user:
                print("Invitation envoyée avec succès.")
                print("ID de l'utilisateur :", user.id)

                # 2. Créer un profil lié dans la table `users`
                data = {
                    "id": user.id,  # correspond à auth.users.id
                    "email": self.new_email.value,
                    "name": self.new_name.value,
                    "surname": self.new_surname.value,
                    "role": self.new_role.value,
                    'function': self.new_function.value,
                    'contact': self.new_contact.value
                }

                insert_response = supabase_client.table("users").insert(data).execute()

                if insert_response.data:
                    print("Profil utilisateur ajouté dans la table users.")
                    return True
                else:
                    print("Erreur lors de l'insertion dans la table users.")
                    return False

        except Exception as e:
            print("Erreur lors de l'invitation :", e)
            return False









