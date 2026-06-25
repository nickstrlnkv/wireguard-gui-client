import os
import shutil
import flet as ft
import settings

# path for .conf directory
CONFS_DIR = os.path.join(os.path.dirname(__file__), "confs")

# make directory if not exists
os.makedirs(CONFS_DIR, exist_ok=True)

def OnWireguard():
    pass


def main(page: ft.Page):
    # Main window settings
    page.title = settings.PAGE_TITLE
    page.window.height = settings.PAGE_WINDOW_HEIGHT
    page.window.width = settings.PAGE_WINDOW_WIDTH
    page.bgcolor = settings.WINDOW_BACKGROUND_COLOR
    page.window_resizable = settings.PAGE_WINDOW_RESIZABLE

    is_connected = False

    # Interface elements
    status_text = ft.Text("Отключено", size=20, color=ft.Colors.RED_ACCENT)
    status_icon = ft.Icon(ft.Icons.SHIELD_OUTLINED, color=ft.Colors.RED_ACCENT, size=50)

    def on_connect_click(e):
        nonlocal is_connected
        is_connected = not is_connected

        if is_connected:
            status_text.value = "Подключено"
            status_text.color = ft.Colors.GREEN_ACCENT
            status_icon.name = ft.Icons.SHIELD_ROUNDED  # ИСПРАВЛЕНО: ft.icons
            status_icon.color = ft.Colors.GREEN_ACCENT
            connect_button.text = "Отключить"
            connect_button.bgcolor = ft.Colors.RED_600
        else:
            status_text.value = "Отключено"
            status_text.color = ft.Colors.RED_ACCENT
            status_icon.name = ft.Icons.SHIELD_OUTLINED  # ИСПРАВЛЕНО: ft.icons
            status_icon.color = ft.Colors.RED_ACCENT
            connect_button.text = "Подключиться"
            connect_button.bgcolor = ft.Colors.BLUE_600

        page.update()

    connect_button = ft.ElevatedButton(
        content="Подключиться",
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        on_click=on_connect_click,
        width=200,
        height=50
    )

    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Wireguard Client", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    status_icon,
                    status_text,
                    ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
                    connect_button
                ],
                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
        )
    )


ft.run(main)
