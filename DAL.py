import os
import sqlite3
import pandas as pd
import SKU
import Config
import Audit

RUTA_DB = Config.obtener_ruta_db()
TIMEOUT_DB = Config.obtener_timeout_db()
RUTA_CSV_EXPORT = Config.obtener_ruta_csv_export()
_df = None
_skus = None
_cache_ids = {}


def _get_connection():
    conn = sqlite3.connect(RUTA_DB, TIMEOUT_DB)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def exportar_csv_para_powerquery():
    if _df is not None and not _df.empty:
        try:
            _df.to_csv(
                RUTA_CSV_EXPORT, index=False, encoding="utf-8-sig", sep=";"
            )
        except Exception as e:
            print(f"Aviso al exportar CSV: {e}")

# ==========================================================
# 1. CARGA DE DATOS Y CACHÉ DE IDs EN RAM
# ==========================================================
def _cargar_cache_ids(conn):
    """Carga todos los (nombre -> id) de las tablas maestras en memoria."""
    global _cache_ids
    tablas = [
        "Tecnologia",
        "SubTecnologia",
        "Brand",
        "Familia",
        "Producto",
        "Source",
        "BagType",
    ]
    cursor = conn.cursor()
    _cache_ids = {}
    for t in tablas:
        cursor.execute(f"SELECT nombre, id FROM {t}")
        # Guardamos en minúsculas para búsquedas seguras
        _cache_ids[t] = {str(nom).strip().lower(): i for nom, i in cursor.fetchall()}


def cargar_datos():
    global _df, _skus

    query = """
        SELECT 
            s.Material,
            s.Material_Description,
            s.Short_Desc,
            s.Tamaño,
            s.UMB,
            s.Peso_neto,
            s.Peso_bruto,
            s.Unidad,
            s.Bultos_X_Pallet,
            s.Peso_Pallet,
            IFNULL(t.nombre, '')  AS Tecnología,
            IFNULL(st.nombre, '') AS [Sub Tecnologia],
            IFNULL(b.nombre, '')  AS Brand,
            IFNULL(f.nombre, '')  AS Familia,
            IFNULL(p.nombre, '')  AS Producto,
            s.Longitud,
            s.UM_Long,
            s.Ancho,
            s.UM_Ancho,
            s.Altura,
            s.UM_Alt,
            s.Volumen,
            s.UM_Volumen AS UV,
            IFNULL(bg.nombre, '') AS [Bag Type],
            IFNULL(src.nombre, '') AS Source,
            s.Vers_Fab,
            s.Activo,
            s.APUB,
            s.Chile
        FROM SKU s
        LEFT JOIN Tecnologia t   ON s.tecnologia_id = t.id
        LEFT JOIN SubTecnologia st ON s.sub_tecnologia_id = st.id
        LEFT JOIN Brand b        ON s.brand_id = b.id
        LEFT JOIN Familia f      ON s.familia_id = f.id
        LEFT JOIN Producto p     ON s.producto_id = p.id
        LEFT JOIN Source src     ON s.source_id = src.id
        LEFT JOIN BagType bg     ON s.bagtype_id = bg.id
        ORDER BY s.Activo DESC, s.Material ASC;
    """

    with _get_connection() as conn:
        _df = pd.read_sql_query(query, conn)
        # 🔹 Precargar todos los IDs en los diccionarios de RAM
        _cargar_cache_ids(conn)

    _df["Activo"] = _df["Activo"].astype(bool)
    _df["APUB"] = _df["APUB"].astype(bool)
    _df["Chile"] = _df["Chile"].astype(bool)

    _skus = [
        SKU.SKU(
            Material=int(fila["Material"]),
            Material_Description=str(fila["Material_Description"] or ""),
            Short_Desc=str(fila["Short_Desc"] or ""),
            Tamaño=float(fila["Tamaño"] or 0.0),
            UMB=str(fila["UMB"] or ""),
            Peso_neto=float(fila["Peso_neto"] or 0.0),
            Peso_bruto=float(fila["Peso_bruto"] or 0.0),
            Unidad=str(fila["Unidad"] or ""),
            Bultos_X_Pallet=int(fila["Bultos_X_Pallet"] or 0),
            Peso_Pallet=float(fila["Peso_Pallet"] or 0.0),
            Brand=str(fila["Brand"] or ""),
            Familia=str(fila["Familia"] or ""),
            Producto=str(fila["Producto"] or ""),
            Longitud=float(fila["Longitud"] or 0.0),
            UM_Long=str(fila["UM_Long"] or ""),
            Ancho=float(fila["Ancho"] or 0.0),
            UM_Ancho=str(fila["UM_Ancho"] or ""),
            Altura=float(fila["Altura"] or 0.0),
            UM_Alt=str(fila["UM_Alt"] or ""),
            Volumen=float(fila["Volumen"] or 0.0),
            UM_Volumen=str(fila["UV"] or ""),
            Tecnología=str(fila["Tecnología"] or ""),
            Activo=bool(fila["Activo"]),
            Sub_Tecnologia=str(fila["Sub Tecnologia"] or ""),
            Bag_Type=str(fila["Bag Type"] or ""),
            Source=str(fila["Source"] or ""),
            Vers_Fab=str(fila["Vers_Fab"] or ""),
            APUB=bool(fila["APUB"]),
            Chile=bool(fila["Chile"]),
        )
        for _, fila in _df.iterrows()
    ]
    exportar_csv_para_powerquery()

# ==========================================================
# BÚSQUEDA INSTANTÁNEA EN DICCIONARIO DE RAM (0.000001s)
# ==========================================================
def _obtener_id_desde_ram(cursor, tabla, valor):
    if not valor or str(valor).strip() == "":
        return None
    val_limpio = str(valor).strip()
    clave_busqueda = val_limpio.lower()

    # 1. Búsqueda instantánea en RAM
    if tabla in _cache_ids and clave_busqueda in _cache_ids[tabla]:
        return _cache_ids[tabla][clave_busqueda]

    # 2. Si no existe en RAM (es un valor nuevo), lo crea en SQLite y actualiza la RAM
    cursor.execute(f"INSERT INTO {tabla} (nombre) VALUES (?)", (val_limpio,))
    nuevo_id = cursor.lastrowid
    if tabla not in _cache_ids:
        _cache_ids[tabla] = {}
    _cache_ids[tabla][clave_busqueda] = nuevo_id
    return nuevo_id


# ==========================================================
# 2. AGREGAR NUEVO SKU (INSTANTÁNEO)
# ==========================================================
def agregar_sku(sku: SKU.SKU) -> tuple[bool, str]:
    global _skus
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()

            # 1. Validar que no exista
            cursor.execute(
                "SELECT Material FROM SKU WHERE Material = ?", (sku.Material,)
            )
            if cursor.fetchone():
                return (
                    False,
                    f"El Material {sku.Material} ya existe en la base de datos.",
                )

            # 2. Obtener IDs desde la memoria RAM (O(1))
            tec_id = _obtener_id_desde_ram(cursor, "Tecnologia", sku.Tecnología)
            subtec_id = _obtener_id_desde_ram(
                cursor, "SubTecnologia", sku.Sub_Tecnologia
            )
            brand_id = _obtener_id_desde_ram(cursor, "Brand", sku.Brand)
            fam_id = _obtener_id_desde_ram(cursor, "Familia", sku.Familia)
            prod_id = _obtener_id_desde_ram(cursor, "Producto", sku.Producto)
            src_id = _obtener_id_desde_ram(cursor, "Source", sku.Source)
            bag_id = _obtener_id_desde_ram(cursor, "BagType", sku.Bag_Type)

            # 3. Insertar
            query_insert = """
                INSERT INTO SKU (
                    Material, Material_Description, Short_Desc, Tamaño, UMB,
                    Peso_neto, Peso_bruto, Unidad, Bultos_X_Pallet, Peso_Pallet,
                    tecnologia_id, sub_tecnologia_id, brand_id, familia_id, producto_id, source_id, bagtype_id,
                    Longitud, UM_Long, Ancho, UM_Ancho, Altura, UM_Alt, Volumen, UM_Volumen,
                    Vers_Fab, Activo, APUB, Chile
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """
            cursor.execute(
                query_insert,
                (
                    sku.Material,
                    sku.Material_Description,
                    sku.Short_Desc,
                    sku.Tamaño,
                    sku.UMB,
                    sku.Peso_neto,
                    sku.Peso_bruto,
                    sku.Unidad,
                    sku.Bultos_X_Pallet,
                    sku.Peso_Pallet,
                    tec_id,
                    subtec_id,
                    brand_id,
                    fam_id,
                    prod_id,
                    src_id,
                    bag_id,
                    sku.Longitud,
                    sku.UM_Long,
                    sku.Ancho,
                    sku.UM_Ancho,
                    sku.Altura,
                    sku.UM_Alt,
                    sku.Volumen,
                    sku.UM_Volumen,
                    sku.Vers_Fab,
                    1 if sku.Activo else 0,
                    1 if sku.APUB else 0,
                    1 if sku.Chile else 0,
                ),
            )
            conn.commit()

        # Actualizar lista en RAM
        if _skus is not None:
            _skus.append(sku)
            _skus.sort(key=lambda x: int(x.Material))
        exportar_csv_para_powerquery()
        Audit.registrar_log(
                tipo_evento="CREAR",
                detalle=f"Creó SKU {sku.Material} ({sku.Material_Description})",
                tabla_afectada="SKU",
                registro_id=str(sku.Material),
                obj_previo=None,
                obj_nuevo=sku,
                 )
        return (
            True,
            f"El SKU: {sku.Material} - {sku.Material_Description} se ha guardado correctamente.",
        )
        
    except Exception as e:
        return False, f"Error al guardar en SQLite: {str(e)}"


# ==========================================================
# 3. MODIFICAR SKU (INSTANTÁNEO)
# ==========================================================
def modificar_sku(sku: SKU.SKU) -> tuple[bool, str]:
    global _skus
    sku_anterior = next(
            (
                s
                for s in (_skus or [])
                if str(s.Material) == str(sku.Material)
            ),
            None,
             )
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            # Obtener IDs desde RAM
            tec_id = _obtener_id_desde_ram(cursor, "Tecnologia", sku.Tecnología)
            subtec_id = _obtener_id_desde_ram(
                cursor, "SubTecnologia", sku.Sub_Tecnologia
            )
            brand_id = _obtener_id_desde_ram(cursor, "Brand", sku.Brand)
            fam_id = _obtener_id_desde_ram(cursor, "Familia", sku.Familia)
            prod_id = _obtener_id_desde_ram(cursor, "Producto", sku.Producto)
            src_id = _obtener_id_desde_ram(cursor, "Source", sku.Source)
            bag_id = _obtener_id_desde_ram(cursor, "BagType", sku.Bag_Type)

            query_update = """
                UPDATE SKU SET
                    Material_Description = ?,
                    Short_Desc = ?,
                    Tamaño = ?,
                    UMB = ?,
                    Peso_neto = ?,
                    Peso_bruto = ?,
                    Unidad = ?,
                    Bultos_X_Pallet = ?,
                    Peso_Pallet = ?,
                    tecnologia_id = ?,
                    sub_tecnologia_id = ?,
                    brand_id = ?,
                    familia_id = ?,
                    producto_id = ?,
                    source_id = ?,
                    bagtype_id = ?,
                    Longitud = ?,
                    UM_Long = ?,
                    Ancho = ?,
                    UM_Ancho = ?,
                    Altura = ?,
                    UM_Alt = ?,
                    Volumen = ?,
                    UM_Volumen = ?,
                    Vers_Fab = ?,
                    Activo = ?,
                    APUB = ?,
                    Chile = ?
                WHERE Material = ?
            """
            cursor.execute(
                query_update,
                (
                    sku.Material_Description,
                    sku.Short_Desc,
                    sku.Tamaño,
                    sku.UMB,
                    sku.Peso_neto,
                    sku.Peso_bruto,
                    sku.Unidad,
                    sku.Bultos_X_Pallet,
                    sku.Peso_Pallet,
                    tec_id,
                    subtec_id,
                    brand_id,
                    fam_id,
                    prod_id,
                    src_id,
                    bag_id,
                    sku.Longitud,
                    sku.UM_Long,
                    sku.Ancho,
                    sku.UM_Ancho,
                    sku.Altura,
                    sku.UM_Alt,
                    sku.Volumen,
                    sku.UM_Volumen,
                    sku.Vers_Fab,
                    1 if sku.Activo else 0,
                    1 if sku.APUB else 0,
                    1 if sku.Chile else 0,
                    sku.Material,
                ),
            )
            conn.commit()

        # Actualizar en RAM
        if _skus is not None:
            for i, item in enumerate(_skus):
                if item.Material == sku.Material:
                    _skus[i] = sku
                    break
        exportar_csv_para_powerquery()
        if sku_anterior:
            Audit.registrar_modificacion_sku(sku_anterior, sku)
        return (
            True,
            f"El SKU: {sku.Material} - {sku.Material_Description} se ha modificado correctamente.",
        )

    except Exception as e:
        return False, f"Error al modificar en SQLite: {str(e)}"

# ==========================================================
# ELIMINAR SKU (SQLITE + RAM: INSTANTÁNEO)
# ==========================================================
def eliminar_sku(material: int) -> tuple[bool, str]:
    global _skus, _df
    sku_a_eliminar = next(
        (s for s in (_skus or []) if str(s.Material) == str(material)), None
    )
    try:
        mat_int = int(material)
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM SKU WHERE Material = ?", (mat_int,))
            conn.commit()

        Audit.registrar_log(
                tipo_evento="ELIMINAR",
                detalle=f"Eliminó el SKU {material}",
                tabla_afectada="SKU",
                registro_id=str(material),
                obj_previo=sku_a_eliminar,
                obj_nuevo=None,
                )
        # Eliminar de la lista en memoria RAM (O(N) rápido)
        if _skus is not None:
            _skus = [x for x in _skus if int(x.Material) != mat_int]

        # Eliminar del DataFrame si existe
        if _df is not None and not _df.empty:
            _df = _df[_df["Material"] != mat_int]
        exportar_csv_para_powerquery()
        return (
            True,
            f"El SKU {material} ha sido eliminado correctamente del catálogo.",
        )
    except Exception as e:
        return False, f"Error al eliminar en SQLite: {str(e)}"

import Audit
import pandas as pd


def procesar_carga_masiva_excel(
    ruta_excel: str, modo: str = "GENERAR"
) -> dict:
    """Procesa el Excel resolviendo automáticamente los IDs de Tecnología, Brand, Familia, etc."""
    resumen = {
        "exito": True,
        "procesados": 0,
        "salteados": [],
        "errores": [],
        "total_filas": 0,
    }

    try:
        df = pd.read_excel(ruta_excel)
        df.columns = [str(c).strip() for c in df.columns]
        resumen["total_filas"] = len(df)

        if "Material" not in df.columns:
            return {
                "exito": False,
                "mensaje": "El Excel no contiene la columna obligatoria 'Material'.",
            }

        with _get_connection() as conn:
            cursor = conn.cursor()

            # 1. Función interna para obtener o auto-crear el ID en tablas maestras
            def obtener_o_crear_id(tabla, nombre_valor):
                texto = str(nombre_valor or "").strip()
                if not texto or texto.lower() == "nan":
                    return None
                # Buscar ID existente
                cursor.execute(
                    f"SELECT id FROM {tabla} WHERE UPPER(TRIM(Nombre)) = UPPER(TRIM(?))",
                    (texto,),
                )
                fila = cursor.fetchone()
                if fila:
                    return fila[0]
                # Si no existe, crearlo automáticamente en la tabla maestra
                cursor.execute(
                    f"INSERT INTO {tabla} (Nombre) VALUES (?)", (texto,)
                )
                return cursor.lastrowid

            # 2. Obtener lista de SKUs existentes
            cursor.execute("SELECT Material FROM SKU")
            existentes = set(str(r[0]).strip() for r in cursor.fetchall())

            for idx, row in df.iterrows():
                mat_id = str(row.get("Material", "")).strip()
                if not mat_id or mat_id.lower() == "nan":
                    continue

                ya_existe = mat_id in existentes

                # Resolver IDs numéricos reales
                id_tec = obtener_o_crear_id(
                    "Tecnologia", row.get("Tecnología", row.get("Tecnologia"))
                )
                id_sub = obtener_o_crear_id(
                    "SubTecnologia",
                    row.get("Sub_Tecnologia", row.get("SubTecnologia")),
                )
                id_bra = obtener_o_crear_id("Brand", row.get("Brand"))
                id_fam = obtener_o_crear_id("Familia", row.get("Familia"))
                id_pro = obtener_o_crear_id("Producto", row.get("Producto"))
                id_src = obtener_o_crear_id("Source", row.get("Source"))
                id_bag = obtener_o_crear_id(
                    "BagType", row.get("Bag_Type", row.get("BagType"))
                )

                # Limpieza de datos numéricos y booleanos
                def _num(val, default=0.0):
                    try:
                        return (
                            default
                            if pd.isna(val)
                            else float(str(val).replace(",", "."))
                        )
                    except:
                        return default

                def _int(val, default=0):
                    try:
                        return default if pd.isna(val) else int(float(val))
                    except:
                        return default

                def _bool(val, default=0):
                    if pd.isna(val):
                        return default
                    return (
                        1
                        if str(val).upper() in ["1", "TRUE", "SI", "SÍ"]
                        else 0
                    )

                # ==========================================
                # MODO 1: GENERAR (Insertar solo nuevos)
                # ==========================================
                if modo == "GENERAR":
                    if ya_existe:
                        resumen["salteados"].append(
                            f"Fila {idx+2}: Material '{mat_id}' ya existe."
                        )
                        continue

                    query_ins = """
                        INSERT INTO SKU (
                            Material, Material_Description, Short_Desc, Tamaño, UMB,
                            Peso_neto, Peso_bruto, Unidad, Bultos_X_Pallet, Peso_Pallet,
                            tecnologia_id, sub_tecnologia_id, brand_id, familia_id, producto_id,
                            source_id, bagtype_id, Longitud, UM_Long, Ancho, UM_Ancho,
                            Altura, UM_Alt, Volumen, UM_Volumen, Vers_Fab, Activo, APUB, Chile
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?, ?, ?, ?
                        )
                    """
                    valores_ins = (
                        mat_id,
                        str(
                            ""
                            if pd.isna(row.get("Material_Description"))
                            else row.get("Material_Description")
                        ),
                        str(
                            ""
                            if pd.isna(row.get("Short_Desc"))
                            else row.get("Short_Desc")
                        ),
                        _int(row.get("Tamaño")),
                        str(
                            ""
                            if pd.isna(row.get("UMB"))
                            else row.get("UMB")
                        ),
                        _num(row.get("Peso_neto")),
                        _num(row.get("Peso_bruto")),
                        str(
                            ""
                            if pd.isna(row.get("Unidad"))
                            else row.get("Unidad")
                        ),
                        _int(row.get("Bultos_X_Pallet")),
                        _num(row.get("Peso_Pallet")),
                        id_tec,
                        id_sub,
                        id_bra,
                        id_fam,
                        id_pro,
                        id_src,
                        id_bag,
                        _num(row.get("Longitud")),
                        str(
                            ""
                            if pd.isna(row.get("UM_Long"))
                            else row.get("UM_Long")
                        ),
                        _num(row.get("Ancho")),
                        str(
                            ""
                            if pd.isna(row.get("UM_Ancho"))
                            else row.get("UM_Ancho")
                        ),
                        _num(row.get("Altura")),
                        str(
                            ""
                            if pd.isna(row.get("UM_Alt"))
                            else row.get("UM_Alt")
                        ),
                        _num(row.get("Volumen")),
                        str(
                            ""
                            if pd.isna(row.get("UV", row.get("UM_Volumen")))
                            else row.get("UV", row.get("UM_Volumen"))
                        ),
                        str(
                            ""
                            if pd.isna(row.get("Vers_Fab"))
                            else row.get("Vers_Fab")
                        ),
                        _bool(row.get("Activo", 1), 1),
                        _bool(row.get("APUB", 0), 0),
                        _bool(row.get("Chile", 0), 0),
                    )
                    cursor.execute(query_ins, valores_ins)
                    existentes.add(mat_id)
                    resumen["procesados"] += 1

                # ==========================================
                # MODO 2: MODIFICAR (Sobrescribe sin validar)
                # ==========================================
                elif modo == "MODIFICAR":
                    if not ya_existe:
                        resumen["salteados"].append(
                            f"Fila {idx+2}: Material '{mat_id}' no existe para editar."
                        )
                        continue

                    query_upd = """
                        UPDATE SKU SET
                            Material_Description = ?, Short_Desc = ?, Tamaño = ?, UMB = ?,
                            Peso_neto = ?, Peso_bruto = ?, Unidad = ?, Bultos_X_Pallet = ?, Peso_Pallet = ?,
                            tecnologia_id = ?, sub_tecnologia_id = ?, brand_id = ?, familia_id = ?, producto_id = ?,
                            source_id = ?, bagtype_id = ?, Longitud = ?, UM_Long = ?, Ancho = ?, UM_Ancho = ?,
                            Altura = ?, UM_Alt = ?, Volumen = ?, UM_Volumen = ?, Vers_Fab = ?,
                            Activo = ?, APUB = ?, Chile = ?
                        WHERE Material = ?
                    """
                    valores_upd = (
                        str(
                            ""
                            if pd.isna(row.get("Material_Description"))
                            else row.get("Material_Description")
                        ),
                        str(
                            ""
                            if pd.isna(row.get("Short_Desc"))
                            else row.get("Short_Desc")
                        ),
                        _int(row.get("Tamaño")),
                        str(
                            ""
                            if pd.isna(row.get("UMB"))
                            else row.get("UMB")
                        ),
                        _num(row.get("Peso_neto")),
                        _num(row.get("Peso_bruto")),
                        str(
                            ""
                            if pd.isna(row.get("Unidad"))
                            else row.get("Unidad")
                        ),
                        _int(row.get("Bultos_X_Pallet")),
                        _num(row.get("Peso_Pallet")),
                        id_tec,
                        id_sub,
                        id_bra,
                        id_fam,
                        id_pro,
                        id_src,
                        id_bag,
                        _num(row.get("Longitud")),
                        str(
                            ""
                            if pd.isna(row.get("UM_Long"))
                            else row.get("UM_Long")
                        ),
                        _num(row.get("Ancho")),
                        str(
                            ""
                            if pd.isna(row.get("UM_Ancho"))
                            else row.get("UM_Ancho")
                        ),
                        _num(row.get("Altura")),
                        str(
                            ""
                            if pd.isna(row.get("UM_Alt"))
                            else row.get("UM_Alt")
                        ),
                        _num(row.get("Volumen")),
                        str(
                            ""
                            if pd.isna(row.get("UV", row.get("UM_Volumen")))
                            else row.get("UV", row.get("UM_Volumen"))
                        ),
                        str(
                            ""
                            if pd.isna(row.get("Vers_Fab"))
                            else row.get("Vers_Fab")
                        ),
                        _bool(row.get("Activo", 1), 1),
                        _bool(row.get("APUB", 0), 0),
                        _bool(row.get("Chile", 0), 0),
                        mat_id,
                    )
                    cursor.execute(query_upd, valores_upd)
                    resumen["procesados"] += 1

            conn.commit()

        # Registro en Auditoría
        Audit.registrar_log(
            tipo_evento="CARGA_MASIVA",
            detalle=f"Carga Masiva [{modo}]: {resumen['procesados']} procesados, {len(resumen['salteados'])} salteados.",
            tabla_afectada="SKU",
        )

        # Recargar memoria y regenerar CSV Live
        cargar_datos()
        exportar_csv_para_powerquery()
        return resumen

    except Exception as e:
        return {"exito": False, "mensaje": str(e)}




# ==========================================================
# 4. FUNCIONES DE CONSULTA (DESDE MEMORIA)
# ==========================================================
def devolver_skus():
    return _skus or []


def devolver_dataframe():
    return _df


def devolver_tecnologias():
    if not _cache_ids.get("Tecnologia"):
        return []
    return sorted(
        [k.title() for k in _cache_ids["Tecnologia"].keys() if k.strip()]
    )


def devolver_subtecnologias(tecnologia=None):
    if not _skus:
        return []
    if not tecnologia or str(tecnologia).strip() in ["", "Todas", "Todos"]:
        subtecs_unicas = set(sku.Sub_Tecnologia.title() for sku in _skus if sku.Sub_Tecnologia)
        return sorted(list(subtecs_unicas))

    tec_filtro = str(tecnologia).strip().upper()
    subtecs_filtradas = set(
        sku.Sub_Tecnologia.title()
        for sku in _skus
        if sku.Sub_Tecnologia and sku.Tecnología.upper() == tec_filtro
    )
    return sorted(list(subtecs_filtradas))


def devolver_brands(tecnologia=None):
    if not _skus:
        return []
    if not tecnologia or str(tecnologia).strip() in ["", "Todas", "Todos"]:
        brands_unicas = set(sku.Brand.title() for sku in _skus if sku.Brand)
        return sorted(list(brands_unicas))
    tec_filtro = str(tecnologia).strip().upper()
    brands_filtradas = set(
        sku.Brand.title()
        for sku in _skus
        if sku.Brand and sku.Tecnología.upper() == tec_filtro
    )
    return sorted(list(brands_filtradas))


def devolver_familias(brand=None):
    if not _skus:
        return []
    if not brand or str(brand).strip() in ["", "Todas", "Todos"]:
        familias_unicas = set(sku.Familia.title() for sku in _skus if sku.Familia)
        return sorted(list(familias_unicas))
    brand_filtro = str(brand).strip().upper()
    familias_filtradas = set(
        sku.Familia.title()
        for sku in _skus
        if sku.Familia and sku.Brand.upper() == brand_filtro
    )
    return sorted(list(familias_filtradas))


def devolver_productos(brand=None):
    if not _skus:
        return []
    if not brand or str(brand).strip() in ["", "Todas", "Todos"]:
        productos_unicos = set(sku.Producto.title() for sku in _skus if sku.Producto)
        return sorted(list(productos_unicos))
    brand_filtro = str(brand).strip().upper()
    productos_filtrados = set(
        sku.Producto.title()
        for sku in _skus
        if sku.Producto and sku.Brand.upper() == brand_filtro
    )
    return sorted(list(productos_filtrados))


def devolver_sources():
    if not _cache_ids.get("Source"):
        return []
    return sorted(
        [k.title() for k in _cache_ids["Source"].keys() if k.strip()]
    )

def devolver_bagtypes():
    if not _cache_ids.get("BagType"):
        return[]
    return sorted([k.title() for k in _cache_ids["BagType"].keys() if k.strip()])

# ==========================================================
# 5. GESTIÓN DE TABLAS MAESTRAS (CATÁLOGOS)
# ==========================================================
def obtener_catalogo_tabla(nombre_tabla: str) -> list[tuple[int, str]]:
    tablas_permitidas = [
        "Brand",
        "Tecnologia",
        "SubTecnologia",
        "Familia",
        "Producto",
        "Source",
        "BagType",
    ]
    if nombre_tabla not in tablas_permitidas:
        return []

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT id, nombre FROM {nombre_tabla} ORDER BY nombre ASC"
        )
        return cursor.fetchall()


def agregar_item_catalogo(nombre_tabla: str, valor: str) -> tuple[bool, str]:
    val_limpio = str(valor or "").strip()
    if not val_limpio:
        return False, "El nombre no puede estar vacío."

    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id FROM {nombre_tabla} WHERE LOWER(nombre) = LOWER(?)",
                (val_limpio,),
            )
            if cursor.fetchone():
                return (
                    False,
                    f"'{val_limpio}' ya existe en la tabla {nombre_tabla}.",
                )

            cursor.execute(
                f"INSERT INTO {nombre_tabla} (nombre) VALUES (?)", (val_limpio,)
            )
            nuevo_id = cursor.lastrowid
            conn.commit()

        # Actualizar caché de RAM
        if nombre_tabla not in _cache_ids:
            _cache_ids[nombre_tabla] = {}
        _cache_ids[nombre_tabla][val_limpio.lower()] = nuevo_id

        return (
            True,
            f"'{val_limpio}' fue agregado exitosamente a {nombre_tabla}.",
        )
    except Exception as e:
        return False, f"Error al insertar en {nombre_tabla}: {str(e)}"


def eliminar_item_catalogo(
    nombre_tabla: str, item_id: int
) -> tuple[bool, str]:
    map_fk = {
        "Tecnologia": "tecnologia_id",
        "SubTecnologia": "sub_tecnologia_id",
        "Brand": "brand_id",
        "Familia": "familia_id",
        "Producto": "producto_id",
        "Source": "source_id",
        "BagType": "bagtype_id",
    }
    fk_col = map_fk.get(nombre_tabla)

    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            if fk_col:
                cursor.execute(
                    f"SELECT COUNT(*) FROM SKU WHERE {fk_col} = ?", (item_id,)
                )
                usos = cursor.fetchone()[0]
                if usos > 0:
                    return (
                        False,
                        f"No se puede eliminar: hay {usos} SKU(s) usando este registro.",
                    )

            cursor.execute(
                f"DELETE FROM {nombre_tabla} WHERE id = ?", (item_id,)
            )
            conn.commit()

        # Actualizar caché RAM
        if nombre_tabla in _cache_ids:
            _cache_ids[nombre_tabla] = {
                k: v
                for k, v in _cache_ids[nombre_tabla].items()
                if v != item_id
            }

        return True, "Registro eliminado correctamente."
    except Exception as e:
        return False, f"Error al eliminar: {str(e)}"

def devolver_usuarios():
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, rol FROM Usuarios ORDER BY username ASC"
            )
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []


def actualizar_rol_usuario(id_usuario: int, nuevo_rol: str) -> bool:
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()

            # Obtener nombre antes de actualizar para el log
            cursor.execute(
                "SELECT username, rol FROM Usuarios WHERE id = ?", (id_usuario,)
            )
            fila = cursor.fetchone()
            if not fila:
                return False

            nombre_user, rol_anterior = fila

            # Actualizar rol en SQLite
            cursor.execute(
                "UPDATE Usuarios SET rol = ? WHERE id = ?",
                (nuevo_rol.upper().strip(), id_usuario),
            )
            conn.commit()

        # Registrar en Auditoría
        Audit.registrar_log(
            tipo_evento="EDITAR",
            detalle=f"Cambió el rol del usuario '{nombre_user}': '{rol_anterior}' ➔ '{nuevo_rol}'",
            tabla_afectada="USUARIOS",
            registro_id=str(nombre_user),
        )
        return True
    except Exception as e:
        print(f"Error al actualizar rol: {e}")
        return False
