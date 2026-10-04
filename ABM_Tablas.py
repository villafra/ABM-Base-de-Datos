import DAL
import flet as ft
import MensajesPopUp as pop


def VistaAdministrarTablas(page: ft.Page, on_volver=None):
    page.title = "Gestión de Tablas Maestras"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Tablas disponibles con sus nombres legibles e íconos
    CATALOGOS = [
        ("Brand", "Marcas / Brands", ft.Icons.LABEL_OUTLINED),
        ("Tecnologia", "Tecnologías", ft.Icons.MEMORY_OUTLINED),
        ("SubTecnologia", "Sub Tecnologías", ft.Icons.ACCOUNT_TREE_OUTLINED),
        ("Familia", "Familias", ft.Icons.CATEGORY_OUTLINED),
        ("Producto", "Productos", ft.Icons.INVENTORY_2_OUTLINED),
        ("Source", "Sources", ft.Icons.LOCATION_ON_OUTLINED),
        ("BagType", "Bag Types", ft.Icons.SHOPPING_BAG_OUTLINED),
    ]

    tabla_actual = "Brand"

    def volver(e=None):
        page.clean()
        if on_volver:
            on_volver(page)
        page.update()

    # ==========================================================
    # Lógica de Listado y Acciones
    # ==========================================================
    def cargar_elementos():
        items = DAL.obtener_catalogo_tabla(tabla_actual)
        filas = []

        if not items:
            listado.controls = [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        "No hay registros cargados.",
                        color="#9CA3AF",
                        italic=True,
                    ),
                )
            ]
        else:
            for item_id, nombre in items:

                def click_borrar(e, i_id=item_id, n_nom=nombre):
                    def confirmar_borrado():
                        exito, msg = DAL.eliminar_item_catalogo(
                            tabla_actual, i_id
                        )
                        if exito:
                            cargar_elementos()
                        else:
                            pop.mostrar_mensaje(page, msg, error=True)

                    pop.mostrar_mensaje(
                        page,
                        f"¿Estás seguro de eliminar '{n_nom}' de la tabla {tabla_actual}?",
                        error=False,
                        al_cerrar=confirmar_borrado,
                    )

                fila = ft.Container(
                    padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                    border_radius=8,
                    bgcolor="#F9FAFB",
                    border=ft.Border.all(1, "#E5E7EB"),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.CHECK_CIRCLE_OUTLINE,
                                        size=18,
                                        color="#3B82F6",
                                    ),
                                    ft.Text(
                                        str(nombre),
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                        color="#1F2937",
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color="#DC2626",
                                tooltip="Eliminar",
                                on_click=click_borrar,
                            ),
                        ],
                    ),
                )
                filas.append(fila)

            listado.controls = filas

        txt_conteo.value = f"{len(items)} registros en {tabla_actual}"
        page.update()

    def agregar_nuevo(e=None):
        val = txt_nuevo_nombre.value
        if not val or not val.strip():
            txt_nuevo_nombre.error_text = "Ingresa un nombre"
            txt_nuevo_nombre.update()
            return

        txt_nuevo_nombre.error_text = None
        txt_nuevo_nombre.update()

        exito, msg = DAL.agregar_item_catalogo(tabla_actual, val)
        if exito:
            txt_nuevo_nombre.value = ""
            cargar_elementos()
        else:
            pop.mostrar_mensaje(page, msg, error=True)

    def cambiar_catalogo(e):
        nonlocal tabla_actual
        tabla_actual = ddl_tablas.value
        txt_nuevo_nombre.value = ""
        txt_nuevo_nombre.label = f"Nuevo nombre para {tabla_actual}"
        cargar_elementos()

    # ==========================================================
    # Componentes de la Interfaz
    # ==========================================================
    ddl_tablas = ft.Dropdown(
        label="Seleccionar Catálogo a Gestionar",
        width=320,
        value="Brand",
        on_select=cambiar_catalogo,
        options=[
            ft.dropdown.Option(key=key, text=label) for key, label, _ in CATALOGOS
        ],
    )

    txt_nuevo_nombre = ft.TextField(
        label="Nuevo nombre para Brand",
        hint_text="Ej: Royal Canin",
        width=320,
        on_submit=agregar_nuevo,  # Presionar Enter agrega directo
    )

    btn_agregar = ft.FilledButton(
        content=ft.Text("Agregar"),
        icon=ft.Icons.ADD,
        on_click=agregar_nuevo,
    )

    txt_conteo = ft.Text(
        "",
        size=13,
        color="#6B7280",
        italic=True,
    )

    listado = ft.ListView(
        controls=[],
        expand=True,
        spacing=6,
    )

    # Contenedor de formulario y tabla
    contenedor_principal = ft.Container(
        width=750,
        bgcolor="white",
        border_radius=12,
        padding=24,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=12,
            color="#1F000000",
            offset=ft.Offset(0, 3),
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                # Encabezado
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(
                                    ft.Icons.SETTINGS_SUGGEST_ROUNDED,
                                    size=26,
                                    color="blue",
                                ),
                                ft.Text(
                                    "Catálogos Maestros",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color="#111827",
                                ),
                            ],
                        ),
                        ft.OutlinedButton(
                            content=ft.Text("Volver al Catálogo"),
                            icon=ft.Icons.ARROW_BACK,
                            on_click=volver,
                        ),
                    ],
                ),
                ft.Divider(height=1, thickness=1, color="#E5E7EB"),
                # Selector de Catálogo
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[ddl_tablas],
                ),
                # Entrada de nuevo elemento
                ft.Container(
                    padding=14,
                    bgcolor="#F9FAFB",
                    border=ft.Border.all(1, "#E5E7EB"),
                    border_radius=10,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                        controls=[
                            txt_nuevo_nombre,
                            btn_agregar,
                        ],
                    ),
                ),
                # Lista de Registros Existentes
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Registros Actuales",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color="#374151",
                        ),
                        txt_conteo,
                    ],
                ),
                ft.Container(
                    height=280,
                    padding=8,
                    border=ft.Border.all(1, "#E5E7EB"),
                    border_radius=8,
                    content=listado,
                ),
            ],
        ),
    )

    cargar_elementos()

    # Agregar a la página con scroll
    page.add(
        ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(height=15),
                contenedor_principal,
                ft.Container(height=25),
            ],
        )
    )
    page.update()
