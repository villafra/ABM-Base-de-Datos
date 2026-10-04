import os
from tkinter import Tk, filedialog
import Auth
import Config
import flet as ft
import MensajesPopUp as pop
import Audit
import SL
from ABM_Usuarios import VistaUsuarios


def VistaLogin(page: ft.Page, on_login_exitoso):
    page.title = "Acceso al Catálogo de SKU"
    page.theme_mode = ft.ThemeMode.LIGHT

    def examinar_db_click(e):
        try:
            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            ruta_seleccionada = filedialog.askopenfilename(
                title="Selecciona la base de datos Catalogo_SKU.db",
                filetypes=[("Base de Datos SQLite", "*.db;*.sqlite;*.sqlite3")],
            )
            root.destroy()

            if ruta_seleccionada:
                txt_ruta_db.value = ruta_seleccionada
                Config.actualizar_ruta_db(ruta_seleccionada)
                txt_ruta_db.update()
        except Exception as ex:
            pop.mostrar_mensaje(
                page, f"No se pudo abrir el selector: {str(ex)}", error=True
            )

    # 2. Formulario de Login
    txt_login_user = ft.TextField(
        label="Usuario", prefix_icon=ft.Icons.PERSON_OUTLINE, width=340
    )
    txt_login_pass = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        width=340,
    )

    def ejecutar_login(e=None):
        exito, msg, rol = Auth.validar_login(
            txt_login_user.value, txt_login_pass.value
        )
        if exito:
            SL.set_sesion(txt_login_user.value,rol)
            Audit.set_usuario_activo(txt_login_user.value)
            Audit.registrar_log(
            tipo_evento="LOGIN",
            detalle=f"Usuario '{txt_login_user.value}' inició sesión en la máquina '{Config.obtener_usuario_windows()}'",
            tabla_afectada="SESION",
            registro_id=txt_login_user.value,
                )
            page.clean()
            on_login_exitoso(page)
        else:
            pop.mostrar_mensaje(page, msg, error=True)

    def ir_a_gestion_usuarios(e):
            usuario = txt_login_user.value
            password = txt_login_pass.value
    
            if not usuario or not password:
                pop.mostrar_mensaje(
                    page, "Ingrese usuario y contraseña para acceder.", error=True
                )
                return
    
            exito, msg, rol = Auth.validar_login(usuario, password)
            if not exito:
                pop.mostrar_mensaje(page, msg, error=True)
                return
            if str(rol[-1]).upper() != "ADMIN":
                pop.mostrar_mensaje(
                    page,
                    "⛔ Solo Administradores pueden gestionar usuarios.",
                    error=True,
                )
                return
    
            page.clean()
            VistaUsuarios(page, on_volver=lambda p: VistaLogin(p, on_login_exitoso))

    txt_login_pass.on_submit = ejecutar_login

    btn_login = ft.FilledButton(
        content=ft.Text(
            "Iniciar Sesión", size=15, weight=ft.FontWeight.W_600
        ),
        icon=ft.Icons.LOGIN,
        width=340,
        height=45,
        on_click=ejecutar_login,
    )

    btn_admin_usuarios = ft.OutlinedButton(
        content=ft.Text("Gestión de Usuarios", size=14),
        icon=ft.Icons.ADMIN_PANEL_SETTINGS,
        width=340,
        height=42,
        on_click=ir_a_gestion_usuarios,
    )


    # 3. Formulario de Registro
    txt_reg_user = ft.TextField(
        label="Nuevo Usuario",
        prefix_icon=ft.Icons.PERSON_ADD_ALT_1,
        width=340,
    )
    txt_reg_pass = ft.TextField(
        label="Nueva Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.KEY_OUTLINED,
        width=340,
    )
    txt_ruta_db = ft.TextField(
        label="Ruta de Base de Datos",
        value=Config.obtener_ruta_db(),
        read_only=True,
        width=280,
    )

    def ejecutar_registro(e=None):
        if not os.path.exists(txt_ruta_db.value):
            pop.mostrar_mensaje(
                page,
                "La base de datos seleccionada no existe. Presiona 'Examinar' para buscarla.",
                error=True,
            )
            return

        exito, msg = Auth.registrar_usuario(
            txt_reg_user.value, txt_reg_pass.value
        )
        if exito:
            pop.mostrar_mensaje(page, msg, error=False)
            txt_login_user.value = txt_reg_user.value
            txt_login_pass.value = ""
            cambiar_seccion(None, "login")
        else:
            pop.mostrar_mensaje(page, msg, error=True)

    btn_registro = ft.FilledButton(
        content=ft.Text(
            "Crear Cuenta", size=15, weight=ft.FontWeight.W_600
        ),
        icon=ft.Icons.APP_REGISTRATION,
        width=340,
        height=45,
        on_click=ejecutar_registro,
    )

    # Contenedores de vistas
    panel_login = ft.Column(
        visible=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
        controls=[
            txt_login_user,
            txt_login_pass,
            btn_login,
            btn_admin_usuarios,
        ],
    )

    panel_registro = ft.Column(
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
                controls=[
                    txt_ruta_db,
                    ft.IconButton(
                        icon=ft.Icons.FOLDER_OPEN,
                        tooltip="Seleccionar Catalogo_SKU.db",
                        on_click=examinar_db_click,
                    ),
                ],
            ),
            txt_reg_user,
            txt_reg_pass,
            btn_registro,
        ],
    )

    def cambiar_seccion(e, modo_directo=None):
        modo = modo_directo or (
            selector_modo.selected[0] if selector_modo.selected else "login"
        )
        if modo == "login":
            panel_login.visible = True
            panel_registro.visible = False
            selector_modo.selected = ["login"]
        else:
            panel_login.visible = False
            panel_registro.visible = True
            selector_modo.selected = ["registro"]
        page.update()

    selector_modo = ft.SegmentedButton(
        selected=["login"],
        allow_multiple_selection=False,
        on_change=cambiar_seccion,
        segments=[
            ft.Segment(
                value="login",
                label=ft.Text("Iniciar Sesión"),
                icon=ft.Icon(ft.Icons.LOCK_OUTLINE),
            ),
            ft.Segment(
                value="registro",
                label=ft.Text("Registrarse"),
                icon=ft.Icon(ft.Icons.PERSON_ADD_ALT_OUTLINED),
            ),
        ],
    )

    tarjeta_principal = ft.Container(
        width=480,
        bgcolor="white",
        border_radius=14,
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
                ft.Icon(ft.Icons.INVENTORY_2, size=36, color="blue"),
                ft.Text(
                    "Catálogo Maestro de SKU",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Divider(height=1, thickness=1, color="#E5E7EB"),
                selector_modo,
                ft.Container(height=8),
                panel_login,
                panel_registro,
            ],
        ),
    )

    page.add(
        ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(height=40),
                tarjeta_principal,
                ft.Container(height=40),
            ],
        )
    )
    page.update()
