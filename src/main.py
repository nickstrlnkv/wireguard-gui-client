import flet as ft
import os
import shutil
import asyncio


import settings
import alerts


# directory path for .conf files
CONFS_DIR = os.path.join(os.path.dirname(__file__), "confs")

# creating confs/ directory if not exists
os.makedirs(CONFS_DIR, exist_ok=True)



# wg-quick need root access -> launching through pkexec (graphic)
WG_QUICK = shutil.which("wg-quick") or "/usr/bin/wg-quick"
PKEXEC = shutil.which("pkexec") or "/usr/bin/pkexec"


async def run_wg(action: str, config_path : str):
    # launching wg-quick up/down <config_path> or root through pkexec
    proc = await asyncio.create_subprocess_exec(
        PKEXEC, WG_QUICK, action, config_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode().strip(), stderr.decode().strip(),


def main(page: ft.Page):
    page.title = settings.PAGE_TITLE
    page.window.height = settings.PAGE_WINDOW_HEIGHT
    page.window.width = settings.PAGE_WINDOW_WIDTH
    page.bgcolor = settings.WINDOW_BACKGROUND_COLOR
    page.window.resizable = settings.PAGE_WINDOW_RESIZABLE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.icon = "./assets/icon.png"

    is_connected = False
    active_config_path = None # current .conf file path

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

    def set_connected_ui(name: str):
        status_text.value = f"Connected: {name}"
        status_text.color = ft.Colors.GREEN_ACCENT
        status_icon.name = ft.Icons.SHIELD_ROUNDED
        status_icon.color = ft.Colors.GREEN_ACCENT
        connect_button.content = ft.Text("Disconnect")
        connect_button.bgcolor = ft.Colors.RED_600
        config_dropdown.disabled = True

    def set_disconnected_ui():
        status_text.value = "Disconnected"
        status_text.color = ft.Colors.RED_ACCENT
        status_icon.name = ft.Icons.SHIELD_OUTLINED
        status_icon.color = ft.Colors.RED_ACCENT
        connect_button.content = ft.Text("Connect")
        connect_button.bgcolor = ft.Colors.BLUE_600
        config_dropdown.disabled = False


    # connect / disable logic button
    async def on_connect_click(e):
        nonlocal is_connected, active_config_path
        selected_config = config_dropdown.value

        # if vpn is disabled and user doesn't choose config -> show alert
        if not selected_config and not is_connected:
            alerts.DIALOG.open = True
            page.update()
            return

        # block button while up/down
        connect_button.disabled = True
        connect_button.content = ft.Text("Disabling…" if is_connected else "Connecting…")
        page.update()

        try:
            if not is_connected:
                config_path = os.path.join(CONFS_DIR, selected_config)
                code, out, err = await run_wg("up", config_path)
                if code != 0:

                    # TODO: FIX THIS (dialog is not showing)
                    if err == "Not authorized":
                        dialog = alerts.show_connecting_dialog(err, out)
                        dialog.open = True
                        page.update()
                    set_disconnected_ui()
                    print(f"Connecting error: {err or out}")
                    return
                is_connected = True
                active_config_path = config_path
                set_connected_ui(selected_config)
            else:
                code, out, err = await run_wg("down", active_config_path)
                if code != 0:
                    set_connected_ui(os.path.basename(active_config_path))
                    # dialog error
                    print(f"Disconnecting error: {err or out}")
                    return
                is_connected = False
                active_config_path = None
                set_disconnected_ui()
        finally:
            connect_button.disabled = False
            page.update()


        """if is_connected:
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

        page.update()"""

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
                    alerts.DIALOG
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,

        )
    )


#ft.app(target=main)
ft.run(main, assets_dir="assets")