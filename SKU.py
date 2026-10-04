from dataclasses import dataclass

@dataclass
class SKU:
    Material: int
    Material_Description: str
    Short_Desc: str
    Tamaño: int
    UMB: str
    Peso_neto: float
    Peso_bruto: float
    Unidad: str
    Bultos_X_Pallet: int
    Peso_Pallet: float
    Brand: str
    Familia: str
    Producto: str
    Longitud: float
    UM_Long: str
    Ancho: float
    UM_Ancho: str
    Altura: float
    UM_Alt: str
    Volumen: float
    UM_Volumen: str
    Tecnología: str
    Activo: bool
    Sub_Tecnologia: str
    Bag_Type: str
    Source: str
    Vers_Fab: str
    APUB: bool
    Chile: bool



