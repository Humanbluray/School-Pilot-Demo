import flet as ft
from utils.couleurs import *
from components import MyButton
from utils.styles import login_style, drop_style
from translations.translations import languages
from services.supabase_client import supabase_client

# variables...
logo_url = ''
SP_LOGO_URL = 'https://nppwkqytgqlqijpeulfj.supabase.co/storage/v1/object/public/logo_school_pilot/logo%20mini.png'
MOTIF_URL = 'https://nppwkqytgqlqijpeulfj.supabase.co/storage/v1/object/public/logo_school_pilot/motifs.png'


class Signin(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route='/', vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, padding=0,
            bgcolor='#f0f0f6',
        )
        self.page = page
        self.lang_button = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(
                        label='fr', value='fr', active_color=BASE_COLOR,
                        label_style=ft.TextStyle(size=13, font_family='PPM')
                    ),
                    ft.Radio(
                        label='en', value='en', active_color=BASE_COLOR,
                        label_style=ft.TextStyle(size=13, font_family='PPM')
                    ),
                ]
            ), on_change=self.change_language, value='fr'
        )
        self.email = ft.TextField(
            **login_style, prefix_icon=ft.Icons.MAIL_OUTLINE_OUTLINED,
        )
        self.password = ft.TextField(
            **login_style, prefix_icon=ft.Icons.PASSWORD_OUTLINED,
            password=True, can_reveal_password=True
        )
        self.connect_button = MyButton(
            languages[self.lang_button.value]['sign in'], None, None,
            self.authenticate_user
        )
        self.choose_text = ft.Text(languages[self.lang_button.value]['choose language'], size=12, font_family='PPM')
        self.header_password = ft.Text(languages[self.lang_button.value]['password'],
            size=11,
            font_family='PPM', color='grey')
        self.login_text = ft.Text(languages[self.lang_button.value]['login'], size=24, font_family="PBL")

        self.controls=[
            ft.Stack(
                controls=[
                    ft.Container(
                        expand=True, padding=0, alignment=ft.alignment.center,
                        content=ft.Image(
                            src=MOTIF_URL, expand=True, opacity=0.6,
                        )
                    ),
                    ft.Card(
                        elevation=10, shape=ft.RoundedRectangleBorder(radius=24),
                        content=ft.Container(
                            padding=0, alignment=ft.alignment.center, bgcolor='white', width=360,
                            border_radius=24,
                            content=ft.Container(
                                padding=10,
                                content=ft.Column(
                                    controls=[
                                        ft.Container(
                                            padding=10, content=ft.Column(
                                                controls=[
                                                    ft.Row(
                                                        [
                                                            ft.Image(
                                                                src=SP_LOGO_URL, expand=True, width=150, height=150,
                                                            ),
                                                        ], alignment=ft.MainAxisAlignment.CENTER
                                                    ),
                                                    ft.Row(
                                                        controls=[
                                                            self.login_text,
                                                        ], alignment=ft.MainAxisAlignment.CENTER
                                                    ),
                                                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                                                    ft.Column(
                                                        spacing=2, controls=[
                                                            ft.Text(languages[self.lang_button.value]['email'],
                                                                    size=11,
                                                                    font_family='PPM', color='grey'),
                                                            self.email,
                                                        ]
                                                    ),
                                                    ft.Column(
                                                        spacing=2, controls=[
                                                            self.header_password,
                                                            self.password,
                                                        ]
                                                    ),
                                                    self.connect_button,
                                                    ft.Row(
                                                        controls=[
                                                            self.choose_text,
                                                            self.lang_button
                                                        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER
                                                    ),
                                                ]
                                            )
                                        ),
                                        ft.Text("")
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0

                                )
                            )
                        )
                    )
                ], alignment=ft.alignment.center
            )
        ]

        self.box = ft.AlertDialog(
            # surface_tint_color="white", bgcolor="white",
            title=ft.Text("", size=16, font_family="PPL"),
            content=ft.Text("", size=12, font_family="PPM"),
            actions=[
                MyButton(languages[self.lang_button.value]['quit'], 'close', 150, self.close_box)
            ]
        )
        self.page.overlay.append(self.box)

    def authenticate_user(self, e):
        language = self.lang_button.value or 'fr'
        email = self.email.value
        password = self.password.value

        if email and password:
            try:
                result = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
                session = result.session
                user = result.user

                if session and user:
                    access_token = session.access_token
                    refresh_token = session.refresh_token
                    user_id = user.id

                    self.page.client_storage.set("access_token", access_token)
                    self.page.client_storage.set("refresh_token", refresh_token)
                    self.page.client_storage.set("user_id", user_id)
                    self.page.client_storage.set("lang", language)

                    user_data = supabase_client.table("users").select("role").eq("id", user_id).execute()
                    if user_data.data:
                        role = user_data.data[0]["role"]
                        self.page.client_storage.set("role", role)

                    self.page.go(f"/home/{language}/{user_id}")
                    return

                # Si pas de session ou d'utilisateur
                self.show_error_dialog(language, "invalid_credentials")
                return

            except Exception as e:
                error_message = str(e).lower()
                print("[ERREUR AUTH] :", e)

                if "network" in error_message or "connection" in error_message or "timeout" in error_message:
                    self.show_error_dialog(language, "network_error")
                elif "invalid" in error_message or "credentials" in error_message or "email" in error_message:
                    self.show_error_dialog(language, "invalid_credentials")
                else:
                    self.show_error_dialog(language, "general_error")

        else:
            self.show_error_dialog(language, "empty_fields")

    def change_language(self, e):
        lang = self.lang_button.value
        self.choose_text.value = languages[lang]['choose language']
        self.connect_button.content.content.controls[1].value = languages[lang]['sign in']
        self.header_password.value = languages[lang]['password']
        self.login_text.value =  languages[lang]['login']
        self.page.update()

    def close_box(self, e):
        self.box.open = False
        self.box.update()

    def show_error_dialog(self, lang, error_type):
        messages = {
            "network_error": {
                "title": languages[lang]['network error title'],
                "message": languages[lang]['network error msg']
            },
            "invalid_credentials": {
                "title": languages[lang]['error'],
                "message": languages[lang]['invalid credentials']
            },
            "empty_fields": {
                "title": languages[lang]['error'],
                "message": languages[lang]['error msg']
            },
            "general_error": {
                "title": languages[lang]['error'],
                "message": languages[lang]['unexpected error']
            }
        }

        self.box.title.value = messages[error_type]["title"]
        self.box.content.value = messages[error_type]["message"]
        self.box.open = True
        self.box.update()




