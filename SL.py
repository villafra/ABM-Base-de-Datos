_ROL_ACTUAL = "LECTOR"  # "ADMIN", "EDITOR", "LECTOR"
_USUARIO_ACTUAL = "Anonimo"


def set_sesion(usuario: str, rol: str):
    global _ROL_ACTUAL, _USUARIO_ACTUAL
    _USUARIO_ACTUAL = str(usuario or "Anonimo").strip()
    _ROL_ACTUAL = str(rol[-1] or "LECTOR").strip().upper()


def get_rol_actual() -> str:
    return _ROL_ACTUAL


def get_usuario_actual() -> str:
    return _USUARIO_ACTUAL


# ==========================================
# VERIFICACIÓN DE PERMISOS
# ==========================================
def puede_crear_editar() -> bool:
    return _ROL_ACTUAL in ["ADMIN", "EDITOR"]


def puede_eliminar() -> bool:
    return _ROL_ACTUAL == "ADMIN"


def puede_gestionar_tablas() -> bool:
    return _ROL_ACTUAL == "ADMIN"


def puede_ver_historial() -> bool:
    return _ROL_ACTUAL in ["ADMIN", "EDITOR"]


def puede_hacer_rollback() -> bool:
    return _ROL_ACTUAL == "ADMIN"
