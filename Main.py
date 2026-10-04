from ABM_SKU import VistaNuevoSKU, VistaEliminarSKU, VistaCargaMasiva
from ABM_Tablas import VistaAdministrarTablas
from Login import VistaLogin
from Historian import VistaHistorico
import DAL
import flet as ft
import MensajesPopUp as pop
import SL
import ssl

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

DAL.cargar_datos()

def vista_principal(page: ft.Page):
    sku_seleccionado = None
    fila_seleccionada = None
    col_sort = "Material"
    orden_asc = True

    # ==========================
    # Ordenación
    # ==========================

    def toggle_sort(columna):
        nonlocal col_sort, orden_asc
        if col_sort == columna:
            orden_asc = not orden_asc
        else:
            col_sort = columna
            orden_asc = True
        actualizar_headers()
        cargar_lista()

    def obtener_clave_orden(sku):
        es_inactivo = (
            0
            if getattr(sku, "Activo", False)
            in [True, 1, "1", "True", "SÍ", "SI"]
            else 1
        )
        if col_sort == "Material":
            val_col = getattr(sku, "Material", 0)
        elif col_sort == "Descripcion":
            val_col = str(
                getattr(sku, "Material_Description", "") or ""
            ).lower()
        elif col_sort == "Brand":
            val_col = str(getattr(sku, "Brand", "") or "").lower()
        elif col_sort == "Familia":
            val_col = str(getattr(sku, "Familia", "") or "").lower()
        elif col_sort == "Producto":
            val_col = str(getattr(sku, "Producto", "") or "").lower()
        elif col_sort == "Activo":
            val_col = es_inactivo
        else:
            val_col = 0

        return (es_inactivo, val_col)

    # ==========================
    # Eventos de Navegación y Acciones
    # ==========================
    def aplicar_filtros(e):
        cargar_lista()

    def nuevo_sku(e):
        page.clean()
        VistaNuevoSKU(page, sku_editar=None, on_volver=vista_principal)
        page.update()

    def editar_sku(e):
        if not sku_seleccionado:
            pop.mostrar_mensaje(page, "Seleccione SKU a modificar.",True)
            return
        page.clean()
        VistaNuevoSKU(
            page, sku_editar=sku_seleccionado, on_volver=vista_principal
        )
        page.update()

    def eliminar_sku_click(e):
        nonlocal sku_seleccionado
        if not sku_seleccionado:
            pop.mostrar_mensaje(
                page,
                "⚠️ Por favor, selecciona un SKU de la lista para eliminar.",
                error=True,
            )
            return

        page.clean()
        VistaEliminarSKU(
            page, sku_eliminar=sku_seleccionado, on_volver=vista_principal
        )
        page.update()

    def abrir_administrador_tablas(e):
        page.clean()
        VistaAdministrarTablas(page, on_volver=vista_principal)
        page.update()

    def abrir_auditoria(e):
        page.clean()
        VistaHistorico(page, on_volver=vista_principal)
        page.update()

    def activar_desactivar(e):
        if not sku_seleccionado:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("⚠️ Por favor, selecciona un SKU de la lista"),
                open=True,
            )
            page.update()
            return
        print(f"Activar/Desactivar SKU: {sku_seleccionado.Material}")

    def carga_masiva(e):
        page.clean()
        VistaCargaMasiva(page, on_volver=vista_principal)
        page.update()

    def limpiar_filtros(e):
        ddl_tecnologia.value = None
        ddl_subtecnologia.value = None
        ddl_subtecnologia.options = []
        ddl_brand.value = None
        ddl_familia.value = None
        ddl_familia.options = []
        txt_material.value = ""
        cargar_lista()
        page.update()

    # ==========================
    # Lógica de Filtrado y Listado
    # ==========================
    def obtener_skus_filtrados():
        resultado = DAL.devolver_skus() or []
        if ddl_tecnologia.value:
            resultado = [
                sku
                for sku in resultado
                if sku.Tecnología == ddl_tecnologia.value
            ]
        if ddl_subtecnologia.value:
            resultado = [
                sku
                for sku in resultado
                if sku.Sub_Tecnologia == ddl_subtecnologia.value
            ]
        if ddl_brand.value:
            resultado = [
                sku for sku in resultado if sku.Brand == ddl_brand.value
            ]
        if ddl_familia.value:
            resultado = [
                sku for sku in resultado if sku.Familia == ddl_familia.value
            ]
        if txt_material.value:
            texto = txt_material.value.strip().upper()
            resultado = [
                sku
                for sku in resultado
                if (
                    texto in str(sku.Material).upper()
                    or texto in str(sku.Material_Description).upper()
                )
            ]
        return resultado

    def seleccionar_sku(e):
        nonlocal sku_seleccionado, fila_seleccionada

        if fila_seleccionada:
            fila_seleccionada.bgcolor = "white"

        sku_seleccionado = e.control.data
        e.control.bgcolor = "#E0EDFF"  # Azul suave de selección
        fila_seleccionada = e.control
        page.update()

    def cargar_lista():
        filas = []
        skus = obtener_skus_filtrados()
        skus.sort(
            key=obtener_clave_orden, reverse=not orden_asc
        )
        for sku in skus:
            es_activo = bool(sku.Activo)

            badge_estado = ft.Container(
                content=ft.Text(
                    "Activo" if es_activo else "Inactivo",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color="#0E6251" if es_activo else "#922B21",
                ),
                bgcolor="#D4EFDF" if es_activo else "#FADBD8",
                border_radius=12,
                padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                alignment=ft.Alignment.CENTER,
                width=80,
            )

            fila = ft.Container(
                data=sku,
                on_click=seleccionar_sku,
                border_radius=8,
                padding=ft.Padding(left=10, right=10, top=8, bottom=8),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            str(sku.Material),
                            width=80,
                            text_align=ft.TextAlign.CENTER,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            str(sku.Material_Description or ""),
                            width=350,
                            text_align=ft.TextAlign.START,
                        ),
                        ft.Text(
                            str(sku.Brand or ""),
                            width=120,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            str(sku.Familia or ""),
                            width=120,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            str(sku.Producto or ""),
                            width=170,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(
                            content=badge_estado,
                            width=80,
                            alignment=ft.Alignment.CENTER,
                        ),
                    ],
                ),
            )
            filas.append(fila)

        listado.controls = filas
        txt_conteo.value = f"Mostrando {len(filas)} materiales"
        page.update()

    # ==========================
    # 1. Botonera Superior (Toolbar)
    # ==========================
    
    btn_nuevo = ft.FilledButton(
        content=ft.Text("Nuevo SKU"),
        icon=ft.Icons.ADD,
        on_click=nuevo_sku,
        visible=SL.puede_crear_editar(), 
    )

    btn_editar = ft.OutlinedButton(
        content=ft.Text("Editar SKU"),
        icon=ft.Icons.EDIT_OUTLINED,
        on_click=editar_sku,
        visible=SL.puede_crear_editar(),  
    )

    btn_eliminar = ft.OutlinedButton(
        content=ft.Text("Eliminar SKU"),
        icon=ft.Icons.DELETE_OUTLINE,
        on_click=eliminar_sku_click,
        visible=SL.puede_eliminar(),  
    )

    btn_tablas = ft.OutlinedButton(
        content=ft.Text("Gestionar Tablas"),
        icon=ft.Icons.CATEGORY_OUTLINED,
        on_click=abrir_administrador_tablas,
        visible=SL.puede_gestionar_tablas(),  
    )

    btn_historial = ft.OutlinedButton(
        content=ft.Text("Ver Historial"),
        icon=ft.Icons.HISTORY,
        on_click=abrir_auditoria,
        visible=SL.puede_ver_historial(),  
    )

    btn_cargamasiva = ft.OutlinedButton(
        content=ft.Text("Carga Masiva"),
        icon=ft.Icons.UPLOAD_FILE_OUTLINED,
        on_click=carga_masiva,
        visible=SL.puede_crear_editar(),
    )

    toolbar = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=5,
        controls=[
            btn_nuevo,
            btn_editar,
            btn_eliminar,
            btn_tablas,
            btn_historial,
            btn_cargamasiva,
        ],
    )

    # ==========================
    # 2. Filtros de Búsqueda
    # ==========================
    def cambio_tecnologia(e):
        subtecnologias = DAL.devolver_subtecnologias(ddl_tecnologia.value) or []
        ddl_subtecnologia.options = [
            ft.dropdown.Option(key=str(x), text=str(x)) for x in subtecnologias
        ]
        ddl_subtecnologia.value = None
        page.update()

    def cambio_brand(e):
        familias = DAL.devolver_familias(ddl_brand.value) or []
        ddl_familia.options = [
            ft.dropdown.Option(key=str(x), text=str(x)) for x in familias
        ]
        ddl_familia.value = None
        page.update()

    txt_material = ft.TextField(
        label="Buscar",
        hint_text="Código SKU o Descripción...",
        prefix_icon=ft.Icons.SEARCH,
        width=320,
        height=45,
        on_submit=aplicar_filtros,
    )

    ddl_tecnologia = ft.Dropdown(
        label="Tecnología",
        width=200,
        on_select=cambio_tecnologia,
        options=[
            ft.dropdown.Option(key=str(x), text=str(x))
            for x in (DAL.devolver_tecnologias() or [])
        ],
    )

    ddl_subtecnologia = ft.Dropdown(
        label="Sub Tecnología", width=200, options=[]
    )

    ddl_brand = ft.Dropdown(
        label="Brand",
        width=200,
        on_select=cambio_brand,
        options=[
            ft.dropdown.Option(key=str(x), text=str(x))
            for x in (DAL.devolver_brands() or [])
        ],
    )

    ddl_familia = ft.Dropdown(label="Familia", width=200, options=[])

    contenedor_filtros = ft.Container(
        width=1050,
        bgcolor="#F9FAFB",
        border=ft.Border.all(1, "#E5E7EB"),
        border_radius=12,
        padding=18,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.FILTER_ALT_OUTLINED, size=20, color="blue"),
                        ft.Text(
                            "Filtros de Búsqueda",
                            size=15,
                            weight=ft.FontWeight.W_600,
                            color="#1F2937",
                        ),
                    ],
                ),
                ft.Divider(height=1, thickness=1, color="#E5E7EB"),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                    spacing=12,
                    controls=[
                        ddl_tecnologia,
                        ddl_subtecnologia,
                        ddl_brand,
                        ddl_familia,
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        txt_material,
                        ft.FilledButton(
                            content=ft.Text("Buscar"),
                            icon=ft.Icons.SEARCH,
                            on_click=aplicar_filtros,
                        ),
                        ft.OutlinedButton(
                            content=ft.Text("Limpiar Filtros"),
                            icon=ft.Icons.CLEAR_ALL,
                            on_click=limpiar_filtros,
                        ),
                    ],
                ),
            ],
        ),
    )

    # ==========================
    # 3. Encabezado y Tabla
    # ==========================
    def crear_header_click(
        titulo, clave, ancho, align=ft.MainAxisAlignment.CENTER
    ):
        return ft.Container(
            width=ancho,
            on_click=lambda e, c=clave: toggle_sort(c),
            ink=True,
            content=ft.Row(
                alignment=align,
                spacing=4,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        titulo,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#374151",
                    ),
                    ft.Text(
                        (
                            ("▲" if orden_asc else "▼")
                            if col_sort == clave
                            else ""
                        ),
                        size=11,
                        color="blue",
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
        )

    def actualizar_headers():
        header_row.controls = [
            crear_header_click(
                "Material", "Material", 80, ft.MainAxisAlignment.CENTER
            ),
            crear_header_click(
                "Descripción", "Descripcion", 350, ft.MainAxisAlignment.START
            ),
            crear_header_click(
                "Brand", "Brand", 120, ft.MainAxisAlignment.CENTER
            ),
            crear_header_click(
                "Familia", "Familia", 120, ft.MainAxisAlignment.CENTER
            ),
            crear_header_click(
                "Producto", "Producto", 170, ft.MainAxisAlignment.CENTER
            ),
            crear_header_click(
                "Estado", "Activo", 80, ft.MainAxisAlignment.CENTER
            ),
        ]
    header_row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    actualizar_headers()

    header = ft.Container(
        content=header_row,
        bgcolor="#F3F4F6",
        border_radius=8,
        padding=ft.Padding(left=10, right=10, top=12, bottom=12),
    )

    header_row.controls = [
            crear_header_click(
                "Material", "Material", 80, ft.MainAxisAlignment.CENTER
            ),
            crear_header_click(
                "Descripción", "Descripcion", 350, ft.MainAxisAlignment.START
            ),
            crear_header_click(
                "Brand", "Brand", 120, ft.MainAxisAlignment.CENTER
            ),
            crear_header_click(
                "Familia", "Familia", 120, ft.MainAxisAlignment.CENTER
            ),
            crear_header_click(
                "Producto", "Producto", 170, ft.MainAxisAlignment.CENTER
            ),
            crear_header_click(
                "Estado", "Activo", 80, ft.MainAxisAlignment.CENTER
            ),
        ]
    header_row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    actualizar_headers()

    txt_conteo = ft.Text(
        "Cargando...",
        size=13,
        color="#6B7280",
        italic=True,
    )

    listado = ft.ListView(
        controls=[],
        expand=True,
        spacing=4,
    )

    tabla_contenedor = ft.Container(
        width=1050,
        height=520,
        bgcolor="white",
        border=ft.Border.all(1, "#E5E7EB"),
        border_radius=12,
        padding=18,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=12,
            color="#1F000000",
            offset=ft.Offset(0, 3),
        ),
        content=ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Materiales Registrados",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="#1F2937",
                        ),
                        txt_conteo,
                    ],
                ),
                ft.Divider(height=1, thickness=1, color="#E5E7EB"),
                header,
                listado,
            ]
        ),
    )

    # ==========================
    # Layout Principal
    # ==========================
    page.add(
        ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Container(height=5),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.INVENTORY, size=30, color="blue"),
                        ft.Text(
                            "Catálogo Maestro de SKU",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                            color="#111827",
                        ),
                    ],
                ),
                toolbar,
                contenedor_filtros,
                tabla_contenedor,
                ft.Container(height=20),
            ],
        )
    )
    cargar_lista()

def main(page: ft.Page):
    page.title = "ABM SKU"
    page.bgcolor = "#F3F4F6"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.maximized = True
    page.window.full_screen = False
    VistaLogin(page, on_login_exitoso=vista_principal)


ft.run(main)
