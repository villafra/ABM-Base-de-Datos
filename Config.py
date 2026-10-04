import configparser
import getpass
import os
import sys
from tkinter import Tk, filedialog

# 1. Determinar el directorio base (ejecutable .exe o script .py)
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RUTA_CONFIG = os.path.join(BASE_DIR, "config.ini")
_config = configparser.ConfigParser()


def obtener_usuario_windows() -> str:
    """Devuelve el usuario actual de Windows en minúsculas."""
    try:
        return getpass.getuser().strip().lower()
    except Exception:
        return (
            os.environ.get("USERNAME", "default_user").strip().lower()
        )


def _pedir_ruta_db_interactiva() -> str:
    """Abre el explorador nativo de Windows si el usuario no tiene ruta configurada."""
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    ruta_elegida = filedialog.askopenfilename(
        title=f"Selecciona Catalogo_SKU.db para el usuario: {obtener_usuario_windows()}",
        filetypes=[("Base de Datos SQLite", "*.db;*.sqlite;*.sqlite3")],
    )
    root.destroy()
    return ruta_elegida


def _asegurar_secciones_base():
    """Garantiza que las secciones GLOBAL y SECURITY existan con sus valores por defecto."""
    modificado = False

    if not _config.has_section("GLOBAL"):
        _config.add_section("GLOBAL")
        _config.set("GLOBAL", "timeout", "20.0")
        modificado = True

    if not _config.has_section("SECURITY"):
        _config.add_section("SECURITY")
        _config.set("SECURITY", "admin_pin", "admin123")
        _config.set("SECURITY", "require_admin_to_delete", "True")
        modificado = True

    if modificado:
        try:
            with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
                _config.write(f)
        except Exception as e:
            print(f"Aviso al inicializar config.ini: {e}")


def cargar_configuracion():
    """Lee el archivo config.ini y asegura que existan los parámetros globales."""
    if os.path.exists(RUTA_CONFIG):
        _config.read(RUTA_CONFIG, encoding="utf-8")
    _asegurar_secciones_base()
    return _config


# ==========================================================
# GESTIÓN DE BASE DE DATOS MULTI-USUARIO
# ==========================================================
def obtener_ruta_db() -> str:
    cargar_configuracion()
    usuario = obtener_usuario_windows()
    seccion_usuario = f"USER_{usuario}"

    if _config.has_section(seccion_usuario):
        ruta_guardada = _config.get(seccion_usuario, "db_path", fallback="")
        if ruta_guardada and os.path.exists(ruta_guardada):
            return ruta_guardada

    # Si no tiene ruta o la ruta guardada ya no existe, pedirla interactivamente
    nueva_ruta = _pedir_ruta_db_interactiva()

    if not nueva_ruta or not os.path.exists(nueva_ruta):
        user_home = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        nueva_ruta = os.path.join(
            user_home,
            "Mars Inc",
            "Planning South LATAM - Documentos",
            "DataBase",
            "Catalogo_SKU.db",
        )

    actualizar_ruta_db(nueva_ruta)
    return nueva_ruta


def actualizar_ruta_db(nueva_ruta: str) -> bool:
    """Guarda o actualiza la ruta de la base de datos para el usuario actual."""
    cargar_configuracion()
    usuario = obtener_usuario_windows()
    seccion_usuario = f"USER_{usuario}"

    if not _config.has_section(seccion_usuario):
        _config.add_section(seccion_usuario)
    _config.set(seccion_usuario, "db_path", nueva_ruta)

    try:
        with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
            _config.write(f)
        return True
    except Exception as e:
        print(f"Error al escribir config.ini: {e}")
        return False


def obtener_timeout_db() -> float:
    cargar_configuracion()
    return _config.getfloat("GLOBAL", "timeout", fallback=20.0)

def obtener_ruta_csv_export() -> str:
    ruta_db = obtener_ruta_db()
    carpeta_db = os.path.dirname(ruta_db)
    return os.path.join(carpeta_db, "Catalogo_SKU_Live.csv")

# ==========================================================
# GESTIÓN DE SEGURIDAD Y ADMIN
# ==========================================================
def obtener_admin_pin() -> str:
    """Obtiene la contraseña o PIN maestro de administrador desde config.ini."""
    cargar_configuracion()
    return _config.get("SECURITY", "admin_pin", fallback="admin123")


def actualizar_admin_pin(nuevo_pin: str) -> bool:
    """Permite cambiar la contraseña de administrador y persistirla en config.ini."""
    cargar_configuracion()
    _config.set("SECURITY", "admin_pin", str(nuevo_pin).strip())
    try:
        with open(RUTA_CONFIG, "w", encoding="utf-8") as f:
            _config.write(f)
        return True
    except Exception as e:
        print(f"Error al guardar nuevo PIN: {e}")
        return False


def requiere_admin_eliminar() -> bool:
    cargar_configuracion()
    return _config.getboolean(
        "SECURITY", "require_admin_to_delete", fallback=True
    )
