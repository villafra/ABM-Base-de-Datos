import flet as ft

def mostrar_mensaje(page, texto, error=False, al_cerrar=None):
        def cerrar_dialogo(e):
            if hasattr(page, "pop_dialog"):
                page.pop_dialog()
            else:
                message_box.open = False
                page.update()

            if al_cerrar:
                al_cerrar()

        message_box = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Error" if error else "ℹ️ Información"),
            content=ft.Text(texto),
            actions=[
                ft.FilledButton(
                    content=ft.Text("Aceptar"),
                    on_click=cerrar_dialogo,
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if hasattr(page, "show_dialog"):
            page.show_dialog(message_box)
        else:
            page.dialog = message_box
            message_box.open = True
            page.update()

def crear_dialogo_espera(texto):
        return ft.AlertDialog(
            modal=True,
            content=ft.Row(
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.ProgressRing(width=30, height=30, stroke_width=3),
                    ft.Text(texto, size=14, weight=ft.FontWeight.W_500),
                ],
            ),
        )