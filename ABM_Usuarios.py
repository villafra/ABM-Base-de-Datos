import DAL
import flet as ft
import MensajesPopUp as pop


def VistaUsuarios(page: ft.Page, on_volver=None):
    lista_usuarios_view = ft.ListView(expand=True, spacing=10)

    def guardar_cambio_rol(id_user, nombre_user, drop_control):
        nuevo_rol = drop_control.value
        if not nuevo_rol:
            pop.mostrar_mensaje(
                page, "Seleccione un rol válido.", error=True
            )
            return

        if hasattr(DAL, "actualizar_rol_usuario") and DAL.actualizar_rol_usuario(
            id_user, nuevo_rol
        ):
            pop.mostrar_mensaje(
                page,
                f"✅ Rol de '{nombre_user}' actualizado a '{nuevo_rol}'",
                error=False,
            )
        else:
            pop.mostrar_mensaje(
                page, "No se pudo actualizar el rol en la base de datos.", error=True
            )

    def ir_al_catalogo(e):
        page.clean()
        if on_volver:
            on_volver(page)

    def cargar_filas():
        lista_usuarios_view.controls.clear()
        usuarios = (
            DAL.devolver_usuarios()
            if hasattr(DAL, "devolver_usuarios")
            else []
        )

        for id_u, nombre_u, rol_u in usuarios:
            ddl_rol = ft.Dropdown(
                width=130,
                height=42,
                value=str(rol_u or "LECTOR").upper(),
                options=[
                    ft.dropdown.Option("ADMIN", "ADMIN"),
                    ft.dropdown.Option("EDITOR", "EDITOR"),
                    ft.dropdown.Option("LECTOR", "LECTOR"),
                ],
            )

            # 🟢 Botón explícito para guardar/asignar el rol
            btn_asignar = ft.FilledButton(
                content=ft.Text("Asignar Rol", size=12),
                icon=ft.Icons.CHECK,
                height=40,
                on_click=lambda e, uid=id_u, nom=nombre_u, ctrl=ddl_rol: guardar_cambio_rol(
                    uid, nom, ctrl
                ),
            )

            fila = ft.Container(
                padding=ft.Padding(16, 10, 16, 10),
                bgcolor="white",
                border_radius=10,
                border=ft.Border.all(1, "#E5E7EB"),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        # Datos del usuario
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(
                                    ft.Icons.ACCOUNT_CIRCLE,
                                    size=28,
                                    color="blue",
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            str(nombre_u),
                                            weight=ft.FontWeight.BOLD,
                                            size=15,
                                            color="#1F2937",
                                        ),
                                        ft.Text(
                                            f"Rol actual: {str(rol_u or 'LECTOR').upper()}",
                                            size=12,
                                            color="#6B7280",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # Desplegable + Botón de Asignación
                        ft.Row(
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ddl_rol,
                                btn_asignar,  # 🟢 Aquí se ubica el botón
                            ],
                        ),
                    ],
                ),
            )
            lista_usuarios_view.controls.append(fila)

    cargar_filas()

    # Layout de la pantalla
    page.add(
        ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Container(height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=750,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(
                                    ft.Icons.ADMIN_PANEL_SETTINGS,
                                    size=30,
                                    color="blue",
                                ),
                                ft.Text(
                                    "Control de Acceso y Roles de Usuarios",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color="#111827",
                                ),
                            ],
                        ),
                        ft.OutlinedButton(
                            "← Volver",
                            icon=ft.Icons.ARROW_BACK,
                            on_click=ir_al_catalogo,
                        ),
                    ],
                ),
                ft.Container(
                    width=750,
                    height=450,
                    bgcolor="#F9FAFB",
                    border=ft.Border.all(1, "#E5E7EB"),
                    border_radius=12,
                    padding=16,
                    content=lista_usuarios_view,
                ),
            ],
        )
    )
    page.update()
