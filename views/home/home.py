from utils.couleurs import *
from components import MyButton
from components.Menu import NavBar
from translations.translations import languages
from services.supabase_client import supabase_client
import asyncio
from services.async_functions.students_functions import get_current_year_id, get_current_year_label, get_current_year_short
from services.async_functions.general_functions import get_active_quarter, get_active_sequence

user_infos_is_active = False
menu_is_active = False


class Home(ft.View):
    def __init__(self, page: ft.Page, language: str, user_id: str):
        super().__init__(
            route=f'/home/{language}/{user_id}',
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            padding=0, bgcolor="white",
        )
        self.user_id = user_id
        self.language = language
        self.page = page
        self.year_id = get_current_year_id()
        self.year_label = get_current_year_label()
        self.year_short = get_current_year_short()

        # On prépare aussi les éléments à l'avance (pour éviter les erreurs plus tard)
        self.user_account = ft.Text(size=13, font_family='PPM')
        self.user_role = ft.Text(size=13, font_family='PPM')
        self.user_function = ft.Text(size=13, font_family='PPM')
        self.user_email = ft.Text(size=13, font_family='PPM')
        self.user_contact = ft.Text(size=13, font_family='PPM')
        self.user_name = ft.Text(size=16, font_family='PSB')
        self.user_surname = ft.Text(size=12, font_family='PPM', color='grey')
        self.user_picture = ft.CircleAvatar(radius=20)

        self.current_year = get_current_year_id()
        self.my_content = ft.Column(
            expand=True, controls=[
                ft.Container(
                    alignment=ft.alignment.center, expand=True,
                    content=ft.Image(src='/pictures/logo complet.png', width=500, height=500,)
                )
            ]
        )
        self.current_year_label = get_current_year_label()

        self.left_menu = ft.Container(
            content=NavBar(self), width=200,  # border=ft.border.only(right=ft.BorderSide(1, 'grey')),
            offset=ft.Offset(0, 0),
            animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_IN)
        )
        self.active_quarter = ft.Text(size=12, font_family="PPM")
        self.active_sequence = ft.Text(size=12, font_family="PPM")
        self.top_menu = ft.Container(
            padding=ft.padding.only(20, 10, 20, 10), bgcolor='white',
            border=ft.border.only(bottom=ft.BorderSide(2, '#f0f0f6')),
            content=ft.Row(
                controls=[
                    ft.Text(''),
                    ft.Row(
                        controls=[
                            ft.Container(
                                border_radius=16, padding=10, bgcolor='#f0f0f6',
                                # border=ft.border.all(1, 'amber'),
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.EDIT_CALENDAR_OUTLINED, color='black', size=20),
                                        self.active_quarter
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=5,
                                )
                            ),
                            ft.Container(
                                border_radius=16, padding=10, bgcolor='#f0f0f6',
#                                 border=ft.border.all(1, 'amber'),
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, color='black', size=20),
                                        self.active_sequence
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=5,
                                )
                            )
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                bgcolor='#f0f0f6', alignment=ft.alignment.center, shape=ft.BoxShape.CIRCLE,
                                content=ft.Icon(ft.Icons.NOTIFICATIONS, color='black54', size=20), height=40,
                                padding=10,
                                on_click=self.open_user_container
                            ),
                            ft.Container(
                                bgcolor='#f0f0f6', alignment=ft.alignment.center, shape=ft.BoxShape.CIRCLE,
                                content=ft.Icon(ft.Icons.WINDOW_ROUNDED, color='black54', size=20), height=40,
                                padding=10,
                                on_click=self.open_user_container
                            ),
                            ft.Container(content=self.user_picture, on_click=self.open_user_container)
                        ]
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        self.user_container = ft.Card(
            elevation=10, shape=ft.RoundedRectangleBorder(radius=10), right=10, top=60,
            scale=ft.Scale(0), animate_scale=ft.Animation(100, ft.AnimationCurve.BOUNCE_OUT),
            content=ft.Container(
                bgcolor='white', padding=20, border_radius=10, width=280, expand=True,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=0,
                            content=ft.Row(
                                controls=[
                                    ft.Column([self.user_name, self.user_surname], spacing=0)
                                ],
                            )
                        ),
                        ft.Divider(),
                        ft.Container(
                            bgcolor="white", padding=0,
                            content=ft.ListView(
                                controls=[
                                    ft.Column([
                                        ft.Text(languages[self.language]['email'], size=12, font_family='PPI',
                                                color='grey'),
                                        ft.Row([self.user_email])
                                    ]),

                                    ft.Column([
                                        ft.Text(languages[self.language]['function'], size=12, font_family='PPI',
                                                color='grey'),
                                        ft.Row([self.user_function])
                                    ]),

                                    ft.Column([
                                        ft.Text(languages[self.language]['role'], size=12, font_family='PPI',
                                                color='grey'),
                                        ft.Row([self.user_role])
                                    ]),

                                    ft.Column([
                                        ft.Text(languages[self.language]['contact'], size=12, font_family='PPI',
                                                color='grey'),
                                        ft.Row([self.user_contact])
                                    ]),
                                    ft.Divider(),
                                    MyButton(languages[self.language]['logout'], 'logout', None, self.logout)
                                ], spacing=10
                            )
                        ),
                    ],
                )
            )
        )

        self.box = ft.AlertDialog(
            surface_tint_color='white',
            title=ft.Text(size=16, font_family="PPR"),
            content=ft.Text(size=12, font_family="PPM"),
            actions=[MyButton("Quitter", 'black', 120, self.close_box)]
        )

        # overlays...
        self.fp_image_student = ft.FilePicker()
        self.fp_import_notes = ft.FilePicker()

        for widget in (
                self.fp_image_student, self.box, self.fp_import_notes
        ):
            self.page.overlay.append(widget)

        # Indicateur de chargement
        self.controls = [
            ft.Column(
                controls=[
                    ft.Text(languages[language]['loading screen'], size=12, font_family="PPM",),
                    ft.ProgressRing(color=BASE_COLOR)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ]

    async def did_mount_async(self):
        print("[DEBUG] Vue montée : appel check_auth()")
        await self.check_auth()

    async def check_auth(self):
        access_token = self.page.client_storage.get("access_token")
        print("[DEBUG] Access token :", access_token)

        if not access_token:
            self.page.go('/')
            return

        try:
            user_response = await asyncio.to_thread(supabase_client.auth.get_user, access_token)
            print("[DEBUG] Réponse utilisateur :", user_response)

            if not user_response or not user_response.user:
                raise Exception("Utilisateur non trouvé ou token invalide.")

            active_sequence = await get_active_sequence(access_token)
            active_quarter = await get_active_quarter(access_token)

            self.active_sequence.value = languages[self.language][active_sequence['name']]
            self.active_quarter.value = languages[self.language][active_quarter['name']]
            self.active_sequence.data = active_sequence['name']
            self.active_quarter.data = active_quarter['name']

            await self.build_main_view()  # Interface
            await self.load_user_data(user_response.user)  # Données utilisateur

        except Exception as e:
            print(f"[ERREUR AUTHENTIFICATION] {e}")
            import traceback; traceback.print_exc()
            self.page.client_storage.clear()
            self.page.go('/')

    async def load_user_data(self, user):
        print("[DEBUG] Chargement des infos utilisateur")

        access_token = self.page.client_storage.get('access_token')

        resp = supabase_client.table('users').select('*').eq('id', self.user_id).execute()
        self.user_name.value = f"{resp.data[0]['name']}"
        self.user_surname.value = f"{resp.data[0]['surname']}"
        self.user_email.value = user.email
        self.user_function.value = resp.data[0]['function']
        self.user_role.value = resp.data[0]['role']
        self.user_contact.value = resp.data[0]['contact']
        self.user_picture.foreground_image_src = resp.data[0]['image_url']
        self.page.update()

    def logout(self, e):
        try:
            supabase_client.auth.sign_out()
        except Exception as e:
            print(f"Erreur lors de la déconnexion : {e}")
        self.page.client_storage.clear()
        self.page.go('/')

    async def build_main_view(self):
        print("[DEBUG] Construction de la vue principale")

        # Remplacement du ProgressRing par l'UI principale
        self.controls.clear()
        self.controls.append(
            ft.Container(
                padding=10, expand=True, bgcolor='white',
                content=ft.Stack(
                    expand=True,
                    controls=[
                        ft.Row(
                            expand=True, spacing=0,
                            controls=[
                                self.left_menu,
                                ft.Container(
                                    expand=True, bgcolor='#f0f0f6', border_radius=16,
                                    content=ft.Column(
                                        expand=True, spacing=0,
                                        controls=[
                                            self.top_menu,
                                            ft.Container(
                                                padding=20, expand=True, bgcolor='#f0f0f6',
                                                content=self.my_content
                                            ),
                                        ]
                                    ),
                                )
                            ]
                        ),
                        self.user_container,
                    ]
                )
            )
        )
        self.page.update()

    def close_box(self, e):
        self.box.open = False
        self.box.update()

    def open_user_container(self, e):
        global user_infos_is_active
        user_infos_is_active = not user_infos_is_active
        self.user_container.scale = 1 if user_infos_is_active else 0
        self.user_container.update()

    def hide_show_menu(self, e):
        global menu_is_active

        if menu_is_active:
            menu_is_active = False
            self.left_menu.offset = ft.Offset(-1, 0)
            self.left_menu.update()
        else:
            menu_is_active = True
            self.left_menu.offset = ft.Offset(0, 0)
            self.left_menu.update()





