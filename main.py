import os
import flet as ft
from views.signin import Signin
from views.home.home import Home
import re, asyncio

SIGNIN_ROUTE = "/"
HOME_ROUTE = '/home'


def main(page: ft.Page):
    page.title = 'School Pilot'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {
        "PPL": "/fonts/Poppins-light.ttf",
        "PPM": "/fonts/Poppins-Medium.ttf",
        "PPI": "/fonts/Poppins-Italic.ttf",
        "PPB": "/fonts/Poppins-Bold.ttf",
        "PSB": "/fonts/Poppins-SemiBold.ttf",
        "PBL": "/fonts/Poppins-Black.ttf",
        "PPR": "/fonts/Poppins-Regular.ttf",
        "PEB": "/fonts/Poppins-ExtraBold.ttf",
    }

    route_views = {
        "/": Signin,
        "/home": Home
    }

    # main.py - Version Corrigée
    async def route_change(event: ft.RouteChangeEvent):
        page.views.clear()
        current_route = event.route

        match = re.match(r"^/home/([^/]+)/([^/]+)$", current_route)

        if match:
            language = match.group(1)
            user_uid = match.group(2)
            view = Home(page, language, user_uid)
            page.views.append(view)
            page.update()  # <-- juste ceci
            await view.did_mount_async()

        elif current_route in route_views:
            page.views.append(route_views[current_route](page))
            page.update()

        else:
            page.views.append(Signin(page))
            page.update()

    def view_pop(view):
        top_view = page.views[-1]
        page.go(top_view.route)

    def run_async(coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)

    page.on_route_change = lambda e: run_async(route_change(e))
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    ft.app(
        target=main, assets_dir='assets', route_url_strategy='default', port=port,
        # view=ft.AppView.WEB_BROWSER
    )






