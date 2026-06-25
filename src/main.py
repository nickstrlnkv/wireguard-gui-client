import flet as ft
import settings

def OnWireguard():
    pass


def main(page: ft.Page):
    # Applying settings
    page.title = settings.PAGE_TITLE
    page.window.height = settings.PAGE_WINDOW_HEIGHT
    page.window.width = settings.PAGE_WINDOW_WIDTH
    page.bgcolor = settings.WINDOW_BACKGROUND_COLOR
    page.window_resizable = settings.PAGE_WINDOW_RESIZABLE


    counter = ft.Text("0", size=50, data=0)

    ft.Button(content="Enable")

    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                content=counter,
                alignment=ft.Alignment.CENTER,
            ),
        )
    )
    page.add(
        ft.Button(content="Enable")
    )


ft.run(main)
