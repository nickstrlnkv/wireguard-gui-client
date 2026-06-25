import flet as ft

DIALOG = ft.AlertDialog(
                title=ft.Text("Error. No file selected"),
                content=ft.Text("Please choose or add .conf file in dropdown list"),
                alignment=ft.Alignment.CENTER,
                on_dismiss=lambda e: print("Dialog dismissed!"),
                title_padding=ft.Padding.all(25),
            )

def show_connecting_dialog(err: str, out: str):
    DIALOG = ft.AlertDialog(
        title=ft.Text(err),
        content=ft.Text(out),
        alignment=ft.Alignment.CENTER,
        on_dismiss=lambda e: print("SHOW_CONNECTING_DIALOG_DEBUG: Dialog dismissed!"),
        title_padding=ft.Padding.all(25),
    )
    return DIALOG