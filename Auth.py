import hashlib
import sqlite3
import Config

# Usuario autenticado en sesión
USUARIO_ACTUAL = None
ROL_ACTUAL = None


def _get_connection():
    return sqlite3.connect(Config.obtener_ruta_db(), timeout=15.0)


def hash_password(password: str) -> str:
    """Aplica hash SHA-256 a la contraseña con salt seguro."""
    salt = "MarsInc_SKU_Catalog_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def inicializar_tabla_usuarios():
    """Crea la tabla de usuarios y un usuario admin por defecto si está vacía."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    rol TEXT NOT NULL DEFAULT 'User'
                )
            """)
            # Si no hay ningún usuario, crear el primer admin
            cursor.execute("SELECT COUNT(*) FROM Usuarios")
            if cursor.fetchone()[0] == 0:
                pass_admin = hash_password("admin123")
                cursor.execute(
                    "INSERT INTO Usuarios (username, password_hash, rol) VALUES (?, ?, ?)",
                    ("admin", pass_admin, "Admin"),
                )
            conn.commit()
    except Exception as e:
        print(f"Aviso al inicializar usuarios: {e}")


def validar_login(username: str, password: str) -> tuple[bool, str, str]:
    """Verifica credenciales. Retorna (exito, mensaje, rol)."""
    global USUARIO_ACTUAL, ROL_ACTUAL
    u_limpio = str(username or "").strip().lower()
    p_limpio = str(password or "").strip()

    if not u_limpio or not p_limpio:
        return False, "Ingresa tu usuario y contraseña.", ""

    try:
        inicializar_tabla_usuarios()
        h_pass = hash_password(p_limpio)
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, rol FROM Usuarios WHERE LOWER(username) = ? AND password_hash = ?",
                (u_limpio, h_pass),
            )
            fila = cursor.fetchone()
            if fila:
                USUARIO_ACTUAL = fila[0]
                ROL_ACTUAL = fila
                return True, f"Bienvenido/a {fila[0]}", fila
            else:
                return (
                    False,
                    "Usuario o contraseña incorrectos.",
                    "",
                )
    except Exception as e:
        return (
            False,
            f"Error al conectar con la base de datos: {str(e)}",
            "",
        )


def registrar_usuario(
    username: str, password: str, rol: str = "LECTOR"
) -> tuple[bool, str]:
    """Crea un nuevo usuario en la base de datos."""
    u_limpio = str(username or "").strip()
    p_limpio = str(password or "").strip()

    if len(u_limpio) < 3:
        return (
            False,
            "El nombre de usuario debe tener al menos 3 caracteres.",
        )
    if len(p_limpio) < 4:
        return (
            False,
            "La contraseña debe tener al menos 4 caracteres.",
        )

    try:
        inicializar_tabla_usuarios()
        h_pass = hash_password(p_limpio)
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM Usuarios WHERE LOWER(username) = LOWER(?)",
                (u_limpio,),
            )
            if cursor.fetchone():
                return (
                    False,
                    f"El usuario '{u_limpio}' ya existe.",
                )

            cursor.execute(
                "INSERT INTO Usuarios (username, password_hash, rol) VALUES (?, ?, ?)",
                (u_limpio, h_pass, rol),
            )
            conn.commit()

        return (
            True,
            f"Usuario '{u_limpio}' creado con éxito. Ya puedes iniciar sesión.",
        )
    except Exception as e:
        return (
            False,
            f"Error al registrar usuario: {str(e)}",
        )
