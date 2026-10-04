from dataclasses import asdict, is_dataclass
from datetime import datetime
import json
import sqlite3
import Config

# Variable de sesión en memoria
_USUARIO_ACTIVO = "Anonimo"


def set_usuario_activo(nombre_usuario: str):
    global _USUARIO_ACTIVO
    _USUARIO_ACTIVO = str(nombre_usuario or "Anonimo").strip()


def obtener_usuario_activo() -> str:
    return _USUARIO_ACTIVO


def inicializar_tabla_logs():
    try:
        ruta_db = Config.obtener_ruta_db()
        with sqlite3.connect(ruta_db, timeout=10.0) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Logs_Auditoria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora TEXT NOT NULL,
                    usuario_app TEXT NOT NULL,
                    usuario_windows TEXT NOT NULL,
                    tipo_evento TEXT NOT NULL,
                    tabla_afectada TEXT NOT NULL,
                    registro_id TEXT NOT NULL,
                    detalle TEXT NOT NULL,
                    datos_previos_json TEXT,
                    datos_nuevos_json TEXT
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"Error inicializando tabla Logs_Auditoria: {e}")


def _objeto_a_dict(obj):
    if obj is None:
        return None
    try:
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, dict):
            return obj.copy()
        if hasattr(obj, "__dict__"):
            return {
                k: v
                for k, v in obj.__dict__.items()
                if not k.startswith("_") and not callable(v)
            }
        return {"valor": str(obj)}
    except Exception:
        return {"valor": str(obj)}


def registrar_log(
    tipo_evento: str,
    detalle: str,
    tabla_afectada: str = "SKU",
    registro_id: str = "",
    obj_previo=None,
    obj_nuevo=None,
):
    try:
        inicializar_tabla_logs()
        ruta_db = Config.obtener_ruta_db()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        usuario_win = Config.obtener_usuario_windows()

        # Serialización segura a JSON
        dict_previo = _objeto_a_dict(obj_previo)
        dict_nuevo = _objeto_a_dict(obj_nuevo)

        json_previo = (
            json.dumps(dict_previo, ensure_ascii=False)
            if dict_previo
            else None
        )
        json_nuevo = (
            json.dumps(dict_nuevo, ensure_ascii=False) if dict_nuevo else None
        )

        with sqlite3.connect(ruta_db, timeout=10.0) as conn:
            conn.execute(
                """
                INSERT INTO Logs_Auditoria 
                (fecha_hora, usuario_app, usuario_windows, tipo_evento, tabla_afectada, registro_id, detalle, datos_previos_json, datos_nuevos_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    fecha_actual,
                    _USUARIO_ACTIVO,
                    usuario_win,
                    str(tipo_evento).upper(),
                    str(tabla_afectada),
                    str(registro_id or ""),
                    str(detalle),
                    json_previo,
                    json_nuevo,
                ),
            )
            conn.commit()
    except Exception as e:
        print(f"Error registrando log de auditoría: {e}")


def registrar_modificacion_sku(sku_original, sku_nuevo):
    CAMPOS_SKU = [
        ("Material_Description", "Descripción"),
        ("Short_Desc", "Desc. Corta"),
        ("Tamaño", "Tamaño"),
        ("UMB", "UMB"),
        ("Peso_neto", "Peso Neto"),
        ("Peso_bruto", "Peso Bruto"),
        ("Unidad", "Unidad"),
        ("Bultos_X_Pallet", "Bultos x Pallet"),
        ("Peso_Pallet", "Peso Pallet"),
        ("Brand", "Brand"),
        ("Familia", "Familia"),
        ("Producto", "Producto"),
        ("Longitud", "Longitud"),
        ("UM_Long", "UM Long."),
        ("Ancho", "Ancho"),
        ("UM_Ancho", "UM Ancho"),
        ("Altura", "Altura"),
        ("UM_Alt", "UM Altura"),
        ("Volumen", "Volumen"),
        ("UM_Volumen", "UM Volumen"),
        ("Tecnología", "Tecnología"),
        ("Sub_Tecnologia", "Sub-Tecnología"),
        ("Bag_Type", "Bag Type"),
        ("Source", "Source"),
        ("Vers_Fab", "Vers. Fab."),
        ("Activo", "Activo"),
        ("APUB", "APUB"),
        ("Chile", "Chile"),
    ]

    def _val(obj, attr):
        val = getattr(obj, attr, None)
        if val is None and attr == "Tecnología":
            val = getattr(obj, "Tecnologia", None)
        if val is None and attr == "Sub_Tecnologia":
            val = getattr(obj, "SubTecnologia", None)
        if val is None and attr == "Bag_Type":
            val = getattr(obj, "BagType", None)
        if val is None and isinstance(obj, dict):
            val = obj.get(attr)

        if val is None:
            return ""
        if isinstance(val, bool):
            return "SÍ" if val else "NO"
        if isinstance(val, float):
            return str(round(val, 4))
        return str(val).strip()

    cambios = []
    for attr, nombre_visible in CAMPOS_SKU:
        v_ant = _val(sku_original, attr)
        v_nue = _val(sku_nuevo, attr)
        if v_ant.upper() != v_nue.upper():
            cambios.append(f"{nombre_visible}: '{v_ant}' ➔ '{v_nue}'")

    mat_id = _val(sku_nuevo, "Material") or _val(sku_original, "Material")

    if cambios:
        detalle_final = f"Modificó SKU {mat_id}: " + " | ".join(cambios)
        registrar_log(
            tipo_evento="EDITAR",
            detalle=detalle_final,
            tabla_afectada="SKU",
            registro_id=str(mat_id),
            obj_previo=sku_original,
            obj_nuevo=sku_nuevo,
        )
    else:
        print(f"[AUDIT] Modificación guardada sin cambios de valor en SKU {mat_id}.")


def devolver_ultimos_logs(limite: int = 50):
    try:
        inicializar_tabla_logs()
        ruta_db = Config.obtener_ruta_db()
        with sqlite3.connect(ruta_db, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, fecha_hora, usuario_app, usuario_windows, tipo_evento, tabla_afectada, registro_id, detalle
                FROM Logs_Auditoria
                ORDER BY id DESC
                LIMIT ?
            """,
                (limite,),
            )
            return cursor.fetchall()
    except Exception as e:
        print(f"Error consultando logs: {e}")
        return []
