import locale
import re
import DAL
import flet as ft
import MensajesPopUp as pop
import SKU

try:
    locale.setlocale(locale.LC_ALL, "")
    sep_decimal = locale.localeconv()["decimal_point"] or "."
except Exception:
    sep_decimal = "."


def VistaNuevoSKU(page: ft.Page, sku_editar=None, on_volver=None):
    es_edicion = sku_editar is not None
    page.title = (
        f"Editar SKU: {sku_editar.Material}"
        if es_edicion
        else "Alta de Nuevo SKU"
    )
    page.theme_mode = ft.ThemeMode.LIGHT

    def volver_a_principal():
        page.clean()
        if on_volver:
            on_volver(page)
        page.update()

    def format_num(val):
        if val is None or val == "":
            return ""
        return str(val).replace(".", sep_decimal)

    def limpiar_campos(e=None):
        # 1. Limpiar campos de texto
        txt_material.value = ""
        txt_short_desc.value = ""
        txt_descripcion.value = ""
        txt_tamaño.value = ""
        txt_bultosXpallet.value = ""
        txt_peso_neto.value = ""
        txt_peso_bruto.value = ""
        txt_pesopallet.value = ""
        txt_longitud.value = ""
        txt_ancho.value = ""
        txt_altura.value = ""
        txt_volumen.value = ""
        txt_UM.value = ""
        txt_UMV.value = ""
        txt_VersFab.value = ""

        # 2. Limpiar y resetear Dropdowns
        ddl_tecnologia.value = None
        ddl_subtecnologia.value = None
        ddl_subtecnologia.options = []

        ddl_brand.value = None
        ddl_familia.value = None
        ddl_familia.options = []

        ddl_producto.value = None
        ddl_producto.options = []

        ddl_source.value = None
        ddl_bagtype.value = None

        # 3. Resetear Switches a valores por defecto
        sw_activo.value = True
        sw_apub.value = False
        sw_chile.value = False

        # 4. Limpiar cualquier texto de error activo
        todos_los_controles = [
            txt_material,
            txt_short_desc,
            txt_descripcion,
            txt_tamaño,
            txt_bultosXpallet,
            txt_peso_neto,
            txt_peso_bruto,
            txt_pesopallet,
            txt_longitud,
            txt_ancho,
            txt_altura,
            txt_volumen,
            txt_UM,
            txt_UMV,
            ddl_source,
            ddl_bagtype,
            txt_VersFab,
            ddl_tecnologia,
            ddl_subtecnologia,
            ddl_brand,
            ddl_familia,
            ddl_producto,
        ]

        for ctrl in todos_los_controles:
            if hasattr(ctrl, "error"):
                ctrl.error = None
            if hasattr(ctrl, "error_text"):
                ctrl.error_text = None

        page.update()

    # ==========================
    # 1. Campos de Entrada
    # ==========================
    sep_regex = re.escape(sep_decimal)

    filtro_enteros = ft.InputFilter(
        allow=True, regex_string=r"^[0-9]*$", replacement_string=""
    )
    filtro_decimales = ft.InputFilter(
        allow=True,
        regex_string=rf"^[0-9]*{sep_regex}?[0-9]*$",
        replacement_string="",
    )

    txt_material = ft.TextField(
        label="Material",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.TAG,
        input_filter=filtro_enteros,
        value=str(sku_editar.Material) if es_edicion else "",
        read_only=es_edicion,
    )
    txt_short_desc = ft.TextField(
        label="Descripción Corta",
        expand=True,
        value=(sku_editar.Short_Desc or "") if es_edicion else "",
    )
    txt_descripcion = ft.TextField(
        label="Descripción",
        expand=True,
        value=(sku_editar.Material_Description or "") if es_edicion else "",
    )

    # Medidas y Logística
    txt_tamaño = ft.TextField(
        label=f"Tamaño ({sep_decimal})",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=filtro_decimales,
        value=format_num(sku_editar.Tamaño) if es_edicion else "",
    )
    txt_bultosXpallet = ft.TextField(
        label="Bultos x Pallet",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=filtro_enteros,
        value=str(sku_editar.Bultos_X_Pallet or "") if es_edicion else "",
    )
    txt_peso_neto = ft.TextField(
        label=f"Peso Neto ({sep_decimal})",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=filtro_decimales,
        value=format_num(sku_editar.Peso_neto) if es_edicion else "",
    )
    txt_peso_bruto = ft.TextField(
        label=f"Peso Bruto ({sep_decimal})",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=filtro_decimales,
        value=format_num(sku_editar.Peso_bruto) if es_edicion else "",
    )
    txt_pesopallet = ft.TextField(
        label=f"Peso Pallet ({sep_decimal})",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=filtro_decimales,
        value=format_num(sku_editar.Peso_Pallet) if es_edicion else "",
    )

    txt_longitud = ft.TextField(
        label="Longitud (mm)",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=filtro_decimales,
        value=format_num(sku_editar.Longitud) if es_edicion else "",
    )
    txt_ancho = ft.TextField(
        label="Ancho (mm)",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=filtro_decimales,
        value=format_num(sku_editar.Ancho) if es_edicion else "",
    )
    txt_altura = ft.TextField(
        label="Altura (mm)",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=filtro_decimales,
        value=format_num(sku_editar.Altura) if es_edicion else "",
    )
    txt_volumen = ft.TextField(
        label="Volumen",
        width=160,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=filtro_decimales,
        value=format_num(sku_editar.Volumen) if es_edicion else "",
    )
    txt_UM = ft.TextField(
        label="Unidad De Medida",
        width=160,
        value=(sku_editar.UM_Long or "") if es_edicion else "",
    )
    txt_UMV = ft.TextField(
        label="Unidad De Volumen",
        width=160,
        value=(sku_editar.UM_Volumen or "") if es_edicion else "",
    )

    # 🔹 Opciones de Fabricación con Dropdowns
    opciones_sources = [
        nom for _, nom in DAL.obtener_catalogo_tabla("Source")
    ] or DAL.devolver_sources()
    opciones_bagtype = [
        nom for _, nom in DAL.obtener_catalogo_tabla("BagType")
    ]

    ddl_source = ft.Dropdown(
        label="Source",
        width=220,
        options=[
            ft.dropdown.Option(key=str(x), text=str(x))
            for x in opciones_sources
        ],
        value=str(sku_editar.Source) if (es_edicion and sku_editar.Source) else None,
    )

    ddl_bagtype = ft.Dropdown(
        label="Bag Type",
        width=220,
        options=[
            ft.dropdown.Option(key=str(x), text=str(x))
            for x in opciones_bagtype
        ],
        value=str(sku_editar.Bag_Type)
        if (es_edicion and sku_editar.Bag_Type)
        else None,
    )

    txt_VersFab = ft.TextField(
        label="Vers Fab",
        width=220,
        value=(sku_editar.Vers_Fab or "") if es_edicion else "",
    )

    # Switches booleanos
    sw_activo = ft.Switch(
        label="Activo", value=bool(sku_editar.Activo) if es_edicion else True
    )
    sw_apub = ft.Switch(
        label="APUB", value=bool(sku_editar.APUB) if es_edicion else False
    )
    sw_chile = ft.Switch(
        label="Chile", value=bool(sku_editar.Chile) if es_edicion else False
    )

    # ==========================
    # 2. Desplegables en Cascada
    # ==========================
    def cambio_tecnologia(e):
        subtecs = DAL.devolver_subtecnologias(ddl_tecnologia.value) or []
        ddl_subtecnologia.options = [
            ft.dropdown.Option(key=str(x), text=str(x)) for x in subtecs
        ]
        ddl_subtecnologia.value = None

        brands = DAL.devolver_brands(ddl_tecnologia.value) or []
        ddl_brand.options = [
            ft.dropdown.Option(key=str(x), text=str(x)) for x in brands
        ]
        ddl_brand.value = None

        ddl_familia.options = []
        ddl_familia.value = None
        ddl_producto.options = []
        ddl_producto.value = None
        page.update()

    def cambio_brand(e):
        familias = DAL.devolver_familias(ddl_brand.value) or []
        ddl_familia.options = [
            ft.dropdown.Option(key=str(x), text=str(x)) for x in familias
        ]
        ddl_familia.value = None

        productos = DAL.devolver_productos(ddl_brand.value) or []
        ddl_producto.options = [
            ft.dropdown.Option(key=str(x), text=str(x)) for x in productos
        ]
        ddl_producto.value = None
        page.update()

    ddl_tecnologia = ft.Dropdown(
        label="Tecnología",
        width=240,
        on_select=cambio_tecnologia,
        options=[
            ft.dropdown.Option(key=str(x), text=str(x))
            for x in (DAL.devolver_tecnologias() or [])
        ],
        value=str(sku_editar.Tecnología)
        if (es_edicion and sku_editar.Tecnología)
        else None,
    )

    subtecs_init = (
        DAL.devolver_subtecnologias(sku_editar.Tecnología)
        if (es_edicion and sku_editar.Tecnología)
        else []
    )
    ddl_subtecnologia = ft.Dropdown(
        label="Sub Tecnología",
        width=240,
        options=[
            ft.dropdown.Option(key=str(x), text=str(x)) for x in subtecs_init
        ],
        value=str(sku_editar.Sub_Tecnologia)
        if (es_edicion and sku_editar.Sub_Tecnologia)
        else None,
    )

    brands_init = (
        DAL.devolver_brands(sku_editar.Tecnología)
        if (es_edicion and sku_editar.Tecnología)
        else (DAL.devolver_brands() or [])
    )
    ddl_brand = ft.Dropdown(
        label="Brand",
        width=240,
        on_select=cambio_brand,
        options=[
            ft.dropdown.Option(key=str(x), text=str(x)) for x in brands_init
        ],
        value=str(sku_editar.Brand)
        if (es_edicion and sku_editar.Brand)
        else None,
    )

    fams_init = (
        DAL.devolver_familias(sku_editar.Brand)
        if (es_edicion and sku_editar.Brand)
        else []
    )
    ddl_familia = ft.Dropdown(
        label="Familia",
        width=240,
        options=[
            ft.dropdown.Option(key=str(x), text=str(x)) for x in fams_init
        ],
        value=str(sku_editar.Familia)
        if (es_edicion and sku_editar.Familia)
        else None,
    )

    prods_init = (
        DAL.devolver_productos(sku_editar.Brand)
        if (es_edicion and sku_editar.Brand)
        else []
    )
    ddl_producto = ft.Dropdown(
        label="Producto",
        width=240,
        options=[
            ft.dropdown.Option(key=str(x), text=str(x)) for x in prods_init
        ],
        value=str(sku_editar.Producto)
        if (es_edicion and sku_editar.Producto)
        else None,
    )

    # ==========================
    # 3. Helpers y Persistencia
    # ==========================
    def parse_float(val):
        try:
            if not val:
                return 0.0
            texto = str(val).strip()
            if sep_decimal == ",":
                texto = texto.replace(".", "").replace(",", ".")
            else:
                texto = texto.replace(",", "")
            return float(texto)
        except (ValueError, TypeError):
            return 0.0

    def parse_int(val):
        try:
            return int(val) if val else 0
        except (ValueError, TypeError):
            return 0

    def guardar(e):
        campos_obligatorios = [
            (txt_material, "Material"),
            (txt_descripcion, "Descripción"),
            (ddl_tecnologia, "Tecnología"),
            (ddl_subtecnologia, "Sub Tecnología"),
            (ddl_brand, "Brand"),
            (txt_tamaño, "Tamaño"),
            (ddl_source, "Source"),
            (txt_VersFab, "Vers Fab"),
        ]

        for control, _ in campos_obligatorios:
            if hasattr(control, "error"):
                control.error = None
            if hasattr(control, "error_text"):
                control.error_text = None
            control.update()

        errores = []
        for control, nombre in campos_obligatorios:
            valor = str(control.value or "").strip()
            if not valor:
                mensaje_error = f"{nombre} requerido"
                if hasattr(control, "error"):
                    control.error = mensaje_error
                if hasattr(control, "error_text"):
                    control.error_text = mensaje_error
                control.update()
                errores.append(nombre)

        if errores:
            mensaje = (
                "Faltan completar los siguientes campos obligatorios:\n\n• "
                + "\n• ".join(errores)
            )
            pop.mostrar_mensaje(page, mensaje, error=True)
            return

        sku_datos = SKU.SKU(
            Material=parse_int(txt_material.value),
            Material_Description=str(txt_descripcion.value).strip(),
            Short_Desc=str(txt_short_desc.value or "").strip(),
            Tamaño=parse_float(txt_tamaño.value),
            UMB="C/U",
            Peso_neto=parse_float(txt_peso_neto.value),
            Peso_bruto=parse_float(txt_peso_bruto.value),
            Unidad="KG",
            Bultos_X_Pallet=parse_int(txt_bultosXpallet.value),
            Peso_Pallet=parse_float(txt_pesopallet.value),
            Brand=str(ddl_brand.value or ""),
            Familia=str(ddl_familia.value or ""),
            Producto=str(ddl_producto.value or ""),
            Longitud=parse_float(txt_longitud.value),
            UM_Long=str(txt_UM.value or "").strip(),
            Ancho=parse_float(txt_ancho.value),
            UM_Ancho=str(txt_UM.value or "").strip(),
            Altura=parse_float(txt_altura.value),
            UM_Alt=str(txt_UM.value or "").strip(),
            Volumen=parse_float(txt_volumen.value),
            UM_Volumen=str(txt_UMV.value or "").strip(),
            Tecnología=str(ddl_tecnologia.value or ""),
            Sub_Tecnologia=str(ddl_subtecnologia.value or ""),
            Bag_Type=str(ddl_bagtype.value or "").strip(),
            Source=str(ddl_source.value or "").strip(),
            Vers_Fab=str(txt_VersFab.value).strip(),
            APUB=bool(sw_apub.value),
            Chile=bool(sw_chile.value),
            Activo=bool(sw_activo.value),
        )

        # ⚡ Guardado instantáneo directo en SQLite
        if es_edicion:
            exito, mensaje = DAL.modificar_sku(sku_datos)
        else:
            exito, mensaje = DAL.agregar_sku(sku_datos)

        pop.mostrar_mensaje(
            page,
            mensaje,
            error=not exito,
            al_cerrar=volver_a_principal if exito else None,
        )

    def cancelar(e):
        volver_a_principal()

    def crear_seccion(titulo: str, icono_nombre, contenido: ft.Control):
        return ft.Container(
            bgcolor="#F9FAFB",
            border=ft.Border.all(1, "#E5E7EB"),
            border_radius=10,
            padding=16,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        spacing=8,
                        controls=[
                            ft.Icon(icono_nombre, size=20, color="blue"),
                            ft.Text(
                                titulo,
                                size=15,
                                weight=ft.FontWeight.W_600,
                                color="#1F2937",
                            ),
                        ],
                    ),
                    ft.Divider(height=1, thickness=1, color="#E5E7EB"),
                    contenido,
                ],
            ),
        )

    # Layout Principal
    titulo_vista = (
        f"Editar SKU: {sku_editar.Material}"
        if es_edicion
        else "Alta de Nuevo SKU"
    )
    icono_vista = (
        ft.Icons.EDIT_NOTE_ROUNDED if es_edicion else ft.Icons.INVENTORY_2_ROUNDED
    )

    formulario = ft.Container(
        width=950,
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
            spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            titulo_vista, size=22, weight=ft.FontWeight.BOLD
                        ),
                        ft.Icon(icono_vista, size=28, color="blue"),
                    ],
                ),
                ft.Divider(height=2),
                # 1. Identificación
                crear_seccion(
                    "Identificación y Clasificación",
                    ft.Icons.BADGE_OUTLINED,
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=15,
                                controls=[txt_material, txt_short_desc],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[txt_descripcion],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=15,
                                run_spacing=12,
                                controls=[ddl_tecnologia, ddl_subtecnologia],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                wrap=True,
                                spacing=15,
                                controls=[
                                    ddl_brand,
                                    ddl_familia,
                                    ddl_producto,
                                ],
                            ),
                        ],
                    ),
                ),
                # 2. Logística
                crear_seccion(
                    "Logística y Dimensiones",
                    ft.Icons.LOCAL_SHIPPING_OUTLINED,
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                wrap=True,
                                spacing=15,
                                controls=[
                                    txt_tamaño,
                                    txt_bultosXpallet,
                                    txt_pesopallet,
                                    txt_peso_neto,
                                    txt_peso_bruto,
                                ],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                wrap=True,
                                spacing=15,
                                controls=[
                                    txt_longitud,
                                    txt_ancho,
                                    txt_altura,
                                    txt_UM,
                                ],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                wrap=True,
                                spacing=15,
                                controls=[txt_volumen, txt_UMV],
                            ),
                        ],
                    ),
                ),
                # 3. Configuración Adicional
                crear_seccion(
                    "Configuración Adicional",
                    ft.Icons.TUNE_ROUNDED,
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                wrap=True,
                                spacing=15,
                                run_spacing=10,
                                controls=[ddl_source, txt_VersFab, ddl_bagtype],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=30,
                                controls=[sw_activo, sw_apub, sw_chile],
                            ),
                        ],
                    ),
                ),
                # Botones Inferiores de Acción
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                    controls=[
                        ft.OutlinedButton(
                            content=ft.Text("Cancelar"),
                            icon=ft.Icons.CLOSE,
                            on_click=cancelar,
                        ),
                        ft.FilledButton(
                            content=ft.Text(
                                "Actualizar SKU"
                                if es_edicion
                                else "Guardar SKU"
                            ),
                            icon=ft.Icons.SAVE,
                            on_click=guardar,
                        ),
                    ],
                ),
            ],
        ),
    )

    page.add(
        ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(height=10),
                formulario,
                ft.Container(height=20),
            ],
        )
    )
    page.update()

def VistaEliminarSKU(page: ft.Page, sku_eliminar, on_volver=None):
    page.title = f"Eliminar SKU: {sku_eliminar.Material}"
    page.theme_mode = ft.ThemeMode.LIGHT

    def volver_a_principal():
        page.clean()
        if on_volver:
            on_volver(page)
        page.update()

    def confirmar_eliminacion(e):
        exito, mensaje = DAL.eliminar_sku(sku_eliminar.Material)
        if exito:

            pop.mostrar_mensaje(
                page,
                mensaje,
                error=False,
                al_cerrar=volver_a_principal,
            )
        else:
            pop.mostrar_mensaje(
                page,
                f"No se pudo eliminar el SKU:\n\n{mensaje}",
                error=True,
            )

    def fila_detalle(etiqueta: str, valor: str):
        return ft.Container(
            padding=ft.Padding(left=10, right=10, top=6, bottom=6),
            border_radius=6,
            bgcolor="#F9FAFB",
            border=ft.Border.all(1, "#E5E7EB"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        etiqueta,
                        weight=ft.FontWeight.W_600,
                        color="#4B5563",
                        size=14,
                    ),
                    ft.Text(
                        str(valor or "-"),
                        weight=ft.FontWeight.W_500,
                        color="#111827",
                        size=14,
                    ),
                ],
            ),
        )

    # Tarjeta con la información simplificada del SKU
    tarjeta_sku = ft.Container(
        width=550,
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
            spacing=16,
            controls=[
                # Cabecera de advertencia
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.WARNING_AMBER_ROUNDED,
                            size=32,
                            color="#DC2626",
                        ),
                        ft.Text(
                            "Confirmar Eliminación",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#DC2626",
                        ),
                    ],
                ),
                ft.Text(
                    "¿Estás seguro de que deseas eliminar permanentemente este SKU de la base de datos?",
                    text_align=ft.TextAlign.CENTER,
                    color="#6B7280",
                    size=14,
                ),
                ft.Divider(height=1, thickness=1, color="#E5E7EB"),
                # Datos clave simplificados
                fila_detalle("Código de Material:", str(sku_eliminar.Material)),
                fila_detalle(
                    "Descripción:", str(sku_eliminar.Material_Description)
                ),
                fila_detalle("Marca / Brand:", str(sku_eliminar.Brand)),
                fila_detalle("Tecnología:", str(sku_eliminar.Tecnología)),
                fila_detalle("Familia:", str(sku_eliminar.Familia)),
                fila_detalle("Producto:", str(sku_eliminar.Producto)),
                fila_detalle("Source:", str(sku_eliminar.Source)),
                fila_detalle(
                    "Estado:",
                    "Activo" if sku_eliminar.Activo else "Inactivo",
                ),
                ft.Divider(height=1, thickness=1, color="#E5E7EB"),
                # Botones de Acción
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.OutlinedButton(
                            content=ft.Text("Cancelar / Volver"),
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: volver_a_principal(),
                        ),
                        ft.FilledButton(
                            content=ft.Text("Sí, Eliminar SKU"),
                            icon=ft.Icons.DELETE_FOREVER,
                            on_click=confirmar_eliminacion,
                        ),
                    ],
                ),
            ],
        ),
    )

    page.add(
        ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(height=30),
                tarjeta_sku,
                ft.Container(height=30),
            ],
        )
    )
    page.update()

from tkinter import Tk, filedialog
import DAL
import flet as ft
import MensajesPopUp as pop


def VistaCargaMasiva(page: ft.Page, on_volver=None):
    page.title = "Carga Masiva de SKU desde Excel"

    txt_ruta_archivo = ft.TextField(
        label="Archivo Excel (.xlsx)",
        hint_text="Ningún archivo seleccionado...",
        read_only=True,
        width=500,
        height=45,
    )

    rg_modo = ft.RadioGroup(
        value="GENERAR",
        content=ft.Row(
            spacing=20,
            controls=[
                ft.Radio(
                    value="GENERAR",
                    label="Generar (Saltea duplicados existentes)",
                ),
                ft.Radio(
                    value="MODIFICAR",
                    label="Modificar (Sobrescribe datos sin validar)",
                ),
            ],
        ),
    )

    txt_resumen = ft.Text(
        "", size=14, weight=ft.FontWeight.W_500, color="#1F2937"
    )
    lista_detalles = ft.ListView(expand=True, spacing=4, height=220)

    def seleccionar_archivo(e):
        try:
            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            ruta = filedialog.askopenfilename(
                title="Selecciona el archivo Excel de SKUs",
                filetypes=[("Archivos de Excel", "*.xlsx;*.xls")],
            )
            root.destroy()

            if ruta:
                txt_ruta_archivo.value = ruta
                txt_ruta_archivo.update()
        except Exception as ex:
            pop.mostrar_mensaje(
                page, f"Error al abrir selector: {ex}", error=True
            )

    def procesar_archivo(e):
        ruta = txt_ruta_archivo.value
        if not ruta:
            pop.mostrar_mensaje(
                page, "Selecciona un archivo Excel primero.", error=True
            )
            return

        modo_sel = rg_modo.value  # 'GENERAR' o 'MODIFICAR'

        lista_detalles.controls.clear()
        txt_resumen.value = "⏳ Procesando archivo Excel..."
        page.update()

        resultado = DAL.procesar_carga_masiva_excel(ruta, modo=modo_sel)

        if not resultado.get("exito", False):
            pop.mostrar_mensaje(
                page,
                f"Error: {resultado.get('mensaje', 'Desconocido')}",
                error=True,
            )
            txt_resumen.value = "❌ Ocurrió un error en la carga."
            page.update()
            return

        # Mostrar Resumen
        procesados = resultado["procesados"]
        salteados = resultado["salteados"]
        total = resultado["total_filas"]

        txt_resumen.value = (
            f"✅ Proceso completado: {procesados} procesados de {total} filas."
        )

        if salteados:
            lista_detalles.controls.append(
                ft.Text(
                    f"⚠️ Materiales no procesados ({len(salteados)}):",
                    weight=ft.FontWeight.BOLD,
                    color="#B91C1C",
                )
            )
            for item in salteados:
                lista_detalles.controls.append(
                    ft.Text(f" • {item}", size=12, color="#4B5563")
                )
        else:
            lista_detalles.controls.append(
                ft.Text(
                    "🎉 Todos los registros se procesaron correctamente sin omisiones.",
                    color="#0E6251",
                    size=13,
                )
            )

        pop.mostrar_mensaje(
            page,
            f"Carga Masiva finalizada: {procesados} registros procesados.",
            error=False,
        )
        page.update()

    def volver_click(e):
        page.clean()
        if on_volver:
            on_volver(page)

    # Layout de la vista
    page.add(
        ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Container(height=10),
                # Encabezado
                ft.Container(
                    width=750,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.UPLOAD_FILE,
                                        size=30,
                                        color="blue",
                                    ),
                                    ft.Text(
                                        "Carga Masiva de SKUs",
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
                ),
                # Tarjeta de Configuración y Selección
                ft.Container(
                    width=750,
                    bgcolor="white",
                    border=ft.Border.all(1, "#E5E7EB"),
                    border_radius=12,
                    padding=20,
                    content=ft.Column(
                        spacing=14,
                        controls=[
                            ft.Text(
                                "1. Seleccione el modo de operación:",
                                weight=ft.FontWeight.BOLD,
                                color="#374151",
                            ),
                            rg_modo,
                            ft.Divider(height=1, color="#F3F4F6"),
                            ft.Text(
                                "2. Seleccione el archivo Excel:",
                                weight=ft.FontWeight.BOLD,
                                color="#374151",
                            ),
                            ft.Row(
                                controls=[
                                    txt_ruta_archivo,
                                    ft.FilledButton(
                                        "Examinar...",
                                        icon=ft.Icons.FOLDER_OPEN,
                                        on_click=seleccionar_archivo,
                                    ),
                                ]
                            ),
                            ft.Container(height=4),
                            ft.FilledButton(
                                "Iniciar Carga Masiva",
                                icon=ft.Icons.PLAY_ARROW,
                                height=45,
                                width=710,
                                on_click=procesar_archivo,
                            ),
                        ],
                    ),
                ),
                # Tarjeta de Reporte de Resultados
                ft.Container(
                    width=750,
                    bgcolor="#F9FAFB",
                    border=ft.Border.all(1, "#E5E7EB"),
                    border_radius=12,
                    padding=16,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            txt_resumen,
                            ft.Divider(height=1, color="#E5E7EB"),
                            lista_detalles,
                        ],
                    ),
                ),
            ],
        )
    )
    page.update()
