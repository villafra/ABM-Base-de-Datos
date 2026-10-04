import json
import Audit
import Config
import DAL
import flet as ft
import MensajesPopUp as pop


def VistaHistorico(page: ft.Page, on_volver=None):
    lista_logs_container = ft.ListView(expand=True, spacing=8)
    txt_filtro_material = ft.TextField(
        label="Buscar Material",
        hint_text="Ej: 102938...",
        prefix_icon=ft.Icons.SEARCH,
        width=250,
        height=45,
    )
    ddl_tipo_evento = ft.Dropdown(
        label="Tipo de Evento",
        width=180,
        options=[
            ft.dropdown.Option("TODOS", "Todos los Eventos"),
            ft.dropdown.Option("CREAR", "Solo Creados"),
            ft.dropdown.Option("EDITAR", "Solo Modificados"),
            ft.dropdown.Option("ELIMINAR", "Solo Eliminados"),
        ],
        value="TODOS",
    )

    def volver_click(e):
        page.clean()
        if on_volver:
            on_volver(page)

    def ejecutar_rollback(id_log, material_id):
        def confirmar_rollback(e):
            dialog.open = False
            page.update()

            # 1. Ejecutar reversión desde Audit
            exito, mensaje = Audit.revertir_cambio_log(id_log)
            if exito:
                # 2. Recargar datos en memoria de la app
                DAL.cargar_datos()
                pop.mostrar_mensaje(page, mensaje, error=False)
                cargar_historial()
            else:
                pop.mostrar_mensaje(page, mensaje, error=True)

        def cancelar(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirmar Reversión de Cambios"),
            content=ft.Text(
                f"¿Deseas restaurar el Material {material_id} al estado exacto previo de este registro?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.FilledButton(
                    "Sí, Restaurar",
                    on_click=confirmar_rollback,
                    bgcolor=ft.Colors.RED_600,
                ),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def cargar_historial(e=None):
        lista_logs_container.controls.clear()
        filtro_mat = txt_filtro_material.value.strip().upper()
        filtro_tipo = ddl_tipo_evento.value

        logs = Audit.devolver_ultimos_logs(limite=100)

        for log in logs:
            id_l, fecha, u_app, u_win, tipo, tabla, reg_id, detalle = log[:8]

            if filtro_mat and filtro_mat not in str(reg_id).upper():
                continue
            if filtro_tipo != "TODOS" and tipo != filtro_tipo:
                continue

            color_badge = (
                "#D4EFDF"
                if tipo == "CREAR"
                else ("#FCF3CF" if tipo == "EDITAR" else "#FADBD8")
            )
            color_texto = (
                "#0E6251"
                if tipo == "CREAR"
                else ("#7D6608" if tipo == "EDITAR" else "#922B21")
            )

            btn_rollback = (
                ft.OutlinedButton(
                    content=ft.Text("Deshacer / Revertir", size=12),
                    icon=ft.Icons.RESTORE,
                    on_click=lambda e, lid=id_l, mat=reg_id: ejecutar_rollback(
                        lid, mat
                    ),
                )
                if tipo in ["EDITAR", "ELIMINAR"]
                else ft.Container()
            )

            tarjeta = ft.Container(
                bgcolor="white",
                border=ft.Border.all(1, "#E5E7EB"),
                border_radius=10,
                padding=14,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Container(
                                            content=ft.Text(
                                                tipo,
                                                size=11,
                                                weight=ft.FontWeight.BOLD,
                                                color=color_texto,
                                            ),
                                            bgcolor=color_badge,
                                            border_radius=6,
                                            padding=ft.Padding(6, 2, 6, 2),
                                        ),
                                        ft.Text(
                                            f"Material: {reg_id}",
                                            weight=ft.FontWeight.BOLD,
                                            size=14,
                                            color="#1F2937",
                                        ),
                                    ],
                                ),
                                ft.Text(
                                    f"🕒 {fecha} | 👤 {u_app} ({u_win})",
                                    size=12,
                                    color="#6B7280",
                                ),
                            ],
                        ),
                        ft.Divider(height=1, color="#F3F4F6"),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    content=ft.Text(
                                        detalle, size=13, color="#374151"
                                    ),
                                ),
                                btn_rollback,
                            ],
                        ),
                    ],
                ),
            )
            lista_logs_container.controls.append(tarjeta)

        if not lista_logs_container.controls:
            lista_logs_container.controls.append(
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    padding=20,
                    content=ft.Text(
                        "No se encontraron registros de cambios con esos filtros.",
                        color="#6B7280",
                        italic=True,
                    ),
                )
            )

        page.update()

    txt_filtro_material.on_submit = cargar_historial
    ddl_tipo_evento.on_change = cargar_historial

    # ==========================
    # Layout de la Vista
    # ==========================
    page.add(
        ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
            controls=[
                ft.Container(height=5),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=1050,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(
                                    ft.Icons.HISTORY, size=28, color="blue"
                                ),
                                ft.Text(
                                    "Auditoría e Historial de Cambios",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color="#111827",
                                ),
                            ],
                        ),
                        ft.OutlinedButton(
                            "← Volver al Catálogo",
                            icon=ft.Icons.ARROW_BACK,
                            on_click=volver_click,
                        ),
                    ],
                ),
                # Barra de Filtros
                ft.Container(
                    width=1050,
                    bgcolor="#F9FAFB",
                    border=ft.Border.all(1, "#E5E7EB"),
                    border_radius=10,
                    padding=12,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=12,
                                controls=[txt_filtro_material, ddl_tipo_evento],
                            ),
                            ft.FilledButton(
                                "Actualizar",
                                icon=ft.Icons.REFRESH,
                                on_click=cargar_historial,
                            ),
                        ],
                    ),
                ),
                # Contenedor de la lista
                ft.Container(
                    width=1050,
                    height=520,
                    bgcolor="#F3F4F6",
                    border=ft.Border.all(1, "#E5E7EB"),
                    border_radius=10,
                    padding=10,
                    content=lista_logs_container,
                ),
            ],
        )
    )

    cargar_historial()
