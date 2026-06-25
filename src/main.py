import os
import shutil
import flet as ft
import settings

# directory path for .conf files
CONFS_DIR = os.path.join(os.path.dirname(__file__), "confs")

# creating confs/ directory if not exists
os.makedirs(CONFS_DIR, exist_ok=True)

dialog = ft.AlertDialog(
                title=ft.Text("Error. No file selected"),
                content=ft.Text("Please choose or add .conf file in dropdown list"),
                alignment=ft.Alignment.CENTER,
                on_dismiss=lambda e: print("Dialog dismissed!"),
                title_padding=ft.Padding.all(25),
            )

def main(page: ft.Page):
    page.title = settings.PAGE_TITLE
    page.window.height = settings.PAGE_WINDOW_HEIGHT
    page.window.width = settings.PAGE_WINDOW_WIDTH
    page.bgcolor = settings.WINDOW_BACKGROUND_COLOR
    page.window.resizable = settings.PAGE_WINDOW_RESIZABLE

    is_connected = False

    # func for getting list of configs
    def get_saved_configs():
        return [f for f in os.listdir(CONFS_DIR) if f.endswith(".conf")]

    # status elements interface
    status_text = ft.Text("Disabled", size=20, color=ft.Colors.RED_ACCENT)
    status_icon = ft.Icon(ft.Icons.SHIELD_OUTLINED, color=ft.Colors.RED_ACCENT, size=50)

    # dropdown list for choosing configuration
    config_dropdown = ft.Dropdown(
        label="Choose configuration",
        width=250,
        options=[ft.dropdown.Option(f) for f in get_saved_configs()],
    )

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # connect / disable logic button
    def on_connect_click(e):
        nonlocal is_connected
        selected_config = config_dropdown.value


        # if vpn is disabled and user doesn't choose config -> show alert
        if not selected_config and not is_connected:
            dialog.open = True
            page.update()
            return

        is_connected = not is_connected

        if is_connected:
            config_path = os.path.join(CONFS_DIR, selected_config)

            # TODO: CLI-call: wg-quick up {file_path}
            print(f"Launching Wireguard with config: {config_path}")

            status_text.value = f"Connected: {selected_config}"
            status_text.color = ft.Colors.GREEN_ACCENT
            status_icon.name = ft.Icons.SHIELD_ROUNDED
            status_icon.color = ft.Colors.GREEN_ACCENT
            connect_button.content = ft.Text("Disable")
            connect_button.bgcolor = ft.Colors.RED_600
            config_dropdown.disabled = True
        else:
            # TODO: CLI-call: wg-quick down {config_path}
            print("Disabling WireGuard")

            status_text.value = "Disabled"
            status_text.color = ft.Colors.RED_ACCENT
            status_icon.name = ft.Icons.SHIELD_OUTLINED
            status_icon.color = ft.Colors.RED_ACCENT
            connect_button.content = ft.Text("Connect")
            connect_button.bgcolor = ft.Colors.BLUE_600
            config_dropdown.disabled = False

        page.update()

    # event handler for "+" button
    async def add_config_click(e):

        # choose file event handler
        files = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["conf"],
        )
        if not files:
            return
        for f in files:
            file_name = os.path.basename(f.path)
            shutil.copy(f.path, os.path.join(CONFS_DIR, file_name))
        config_dropdown.options = [ft.dropdown.Option(f) for f in get_saved_configs()]
        config_dropdown.value = file_name
        page.update()

    # add new file button
    add_config_button = ft.IconButton(
        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
        icon_color=ft.Colors.BLUE_400,
        icon_size=30,
        tooltip="Add .conf file",
        on_click=add_config_click,
    )

    # connect button
    connect_button = ft.ElevatedButton(
        content=ft.Text("Connect"),
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        on_click=on_connect_click,
        width=200,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )

    # container for dropdown list
    config_selection_row = ft.Row(
        controls=[config_dropdown, add_config_button],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # render main interface
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Wireguard Client", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    config_selection_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    status_icon,
                    status_text,
                    ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                    connect_button,
                    dialog
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,

        )
    )


ft.app(target=main)