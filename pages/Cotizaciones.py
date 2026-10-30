"""
Módulo de Cotizaciones y Ofertas Comerciales (Streamlit).

Correcciones principales frente a la versión anterior:
- Consecutivo seguro: se calcula al guardar, con candado y usando el número máximo (antes se repetía).
- Estado de firma estricto: solo FIRMADO cuenta como aprobada (antes cualquier valor raro contaba).
- Contraseña de gerencia fuera del código (st.secrets["GERENCIA_PASSWORD"] o variable de entorno).
- Sin st.stop() dentro de las pestañas; validaciones que listan todos los errores.
- Números guardados como números; escritura atómica con candado y manejo de errores.
- Se guarda el costo base y el precio se recalcula (moneda, TRM y margen ya no se desfasan).
- IVA configurable por oferta; documento con logo, formato colombiano y total en letras.
- Anular (con motivo), duplicar oferta, lista de pendientes y reparación de consecutivos repetidos.
"""
import base64
import hmac
import os
import re
import shutil
import tempfile
import threading
import unicodedata
import uuid
from datetime import date, datetime
from html import escape as esc

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Validación de seguridad de sesión
if not st.session_state.get("password_correct", False):
    st.error("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal.")
    st.stop()

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
LOGO_EMBEBIDO = "data:image/png;base64,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"  # si existe logo.png junto a la app, ese tiene prioridad
LOGOS_ARCHIVO = ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp")

ARCHIVO_COT = "base_cotizaciones.xlsx"
ARCHIVO_MATERIALES = "base_materiales.xlsx"
ARCHIVO_CLIENTES = "base_clientes.xlsx"        # opcional; si no existe se usa base_proveedores.xlsx
ARCHIVO_PROVEEDORES = "base_proveedores.xlsx"

COLS_COT = [
    "CONSECUTIVO", "FECHA", "CLIENTE", "NIT_CLIENTE", "DIRECCION", "TELEFONO",
    "MONEDA", "TRM", "VALIDEZ_OFERTA", "FORMA_PAGO", "CONDICIONES",
    "ELABORADO_POR", "APROBADO_POR", "ESTADO_FIRMA", "CODIGO_MATERIAL", "DESCRIPCION",
    "REFERENCIA", "UNIDAD", "CANTIDAD", "COSTO_UNITARIO_COP",
    "MARGEN_PCT", "PRECIO_UNITARIO_FINAL", "SUBTOTAL",
    "IVA_PCT", "FECHA_APROBACION", "MOTIVO_ANULACION",   # columnas nuevas (se crean solas)
]
COLS_NUM = ["TRM", "CANTIDAD", "COSTO_UNITARIO_COP", "MARGEN_PCT", "PRECIO_UNITARIO_FINAL", "SUBTOTAL", "IVA_PCT"]
CLAVE_CABECERA = ["CLIENTE", "FECHA", "ELABORADO_POR", "MONEDA", "VALIDEZ_OFERTA", "FORMA_PAGO"]

PENDIENTE, FIRMADO, ANULADA = "PENDIENTE", "FIRMADO", "ANULADA"
MONEDAS = {"COP (Peso Colombiano)": "COP", "USD (Dólar Americano)": "USD"}
IVA_OPCIONES = {"19%": 19.0, "5%": 5.0, "0% (Excluido / Exento)": 0.0}
SIN_CLIENTE = "-- Seleccione un Cliente --"
SIN_MATERIAL = "-- Seleccione un material --"
ITEM_LIBRE = "✏️ Ítem libre (no está en el catálogo)"
OBS_DEFECTO = "Suministro cotizado bajo los términos comerciales vigentes."

EMPRESA = {
    "nombre": "Asuserviciosss SAS",
    "nit": "901224239-3",
    "direccion": "CL 67 22 62 CA 14 BRR PARNASO",
    "telefono": "3186565776",
    "correo": "asuserviciosss@hotmail.com",
    "regimen": "COMUN",
}


# =============================================================================
# UTILIDADES DE TEXTO Y NÚMEROS
# =============================================================================
def norm(s):
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def norm_col(s):
    s = unicodedata.normalize("NFD", str(s))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").upper().strip()


def parse_valor(x, defecto=0.0):
    t = str(x).strip().replace("$", "").replace(" ", "")
    if t in ("", "nan", "None"):
        return defecto
    if "." in t and "," in t:
        t = t.replace(".", "").replace(",", ".") if t.rfind(",") > t.rfind(".") else t.replace(",", "")
    elif "," in t:
        t = t.replace(",", "") if re.fullmatch(r"\d{1,3}(,\d{3})+", t) else t.replace(",", ".")
    elif "." in t and re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return defecto


def a_num(x, defecto=0.0):
    """Número guardado por la app (punto decimal) o escrito a la colombiana."""
    t = str(x).strip().replace("$", "").replace(" ", "")
    if re.fullmatch(r"-?\d+(\.\d+)?", t):
        return float(t)
    return parse_valor(t, defecto)


def fmt_dinero(v, moneda="COP"):
    t = f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if moneda != "USD" and t.endswith(",00"):
        t = t[:-3]
    return ("US$ " if moneda == "USD" else "$") + t


def fmt_num(v):
    v = float(v)
    return str(int(v)) if v.is_integer() else f"{v:g}".replace(".", ",")


def fmt_fecha(x):
    t = str(x).strip()
    if not t:
        return ""
    try:
        return pd.to_datetime(t, dayfirst="/" in t).strftime("%d/%m/%Y")
    except Exception:
        return t


def estado_norm(x):
    t = norm(x)
    if t in ("FIRMADO", "FIRMADA", "APROBADO", "APROBADA"):
        return FIRMADO
    if t in ("ANULADO", "ANULADA"):
        return ANULADA
    return PENDIENTE


_UNID = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
         "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho",
         "diecinueve", "veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco",
         "veintiséis", "veintisiete", "veintiocho", "veintinueve"]
_DECENAS = ["", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]
_CENTENAS = ["", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos",
             "seiscientos", "setecientos", "ochocientos", "novecientos"]


def _menor_mil(n):
    if n == 100:
        return "cien"
    c, r = divmod(n, 100)
    partes = [_CENTENAS[c]] if c else []
    if r:
        if r < 30:
            partes.append(_UNID[r])
        else:
            d, u = divmod(r, 10)
            partes.append(_DECENAS[d] + (f" y {_UNID[u]}" if u else ""))
    return " ".join(partes)


def _apocope(t):
    if t.endswith("veintiuno"):
        return t[:-9] + "veintiún"
    if t.endswith("uno"):
        return t[:-3] + "un"
    return t


def numero_a_letras(n):
    n = int(round(n))
    if n == 0:
        return "cero"
    millones, resto = divmod(n, 1_000_000)
    miles, unidades = divmod(resto, 1000)
    partes = []
    if millones:
        partes.append("un millón" if millones == 1 else f"{_apocope(numero_a_letras(millones))} millones")
    if miles:
        partes.append("mil" if miles == 1 else f"{_apocope(_menor_mil(miles))} mil")
    if unidades:
        partes.append(_menor_mil(unidades))
    return " ".join(partes)


def total_en_letras(valor, moneda):
    if valor >= 10 ** 12:
        return ""
    if moneda == "USD":
        entero, cent = divmod(int(round(valor * 100)), 100)
        texto = _apocope(numero_a_letras(entero)) if entero % 1000 else numero_a_letras(entero)
        return f"{texto} CON {cent:02d}/100 DÓLARES AMERICANOS".upper()
    n = int(round(valor))
    if n == 1:
        return "UN PESO M/CTE"
    texto = _apocope(numero_a_letras(n)) if n % 1000 else numero_a_letras(n)
    de = "DE " if n and n % 1_000_000 == 0 else ""
    return f"{texto} {de}PESOS M/CTE".upper()


# =============================================================================
# ACCESO A DATOS
# =============================================================================
@st.cache_resource
def obtener_lock():
    """Un único candado compartido por todas las sesiones del servidor."""
    return threading.Lock()


def ruta_datos(nombre):
    """Busca el archivo junto a la carpeta de esta página (..), junto a ella o en la carpeta de trabajo."""
    base = os.path.dirname(os.path.abspath(__file__))
    candidatos = [os.path.join(base, "..", nombre), os.path.join(base, nombre), os.path.join(os.getcwd(), nombre)]
    for c in candidatos:
        if os.path.exists(c):
            return os.path.normpath(c)
    return os.path.normpath(candidatos[0])


def _mtime(ruta):
    return os.path.getmtime(ruta) if os.path.exists(ruta) else 0.0


def _limpiar(df, columnas):
    df = df.fillna("")
    for col in columnas:
        if col not in df.columns:
            df[col] = ""
    df = df[list(columnas)].astype(str)
    for col in columnas:
        df[col] = df[col].str.strip().replace(["nan", "NaN", "None", "<NA>", "NaT"], "")
    return df


def leer_directo(ruta, columnas):
    """Lectura estricta (lanza error si falla): se usa antes de escribir para no pisar datos."""
    if not os.path.exists(ruta):
        return pd.DataFrame(columns=list(columnas))
    return _limpiar(pd.read_excel(ruta, dtype=str), columnas)


@st.cache_data(show_spinner=False)
def _leer_cache(ruta, columnas, mtime):
    try:
        return leer_directo(ruta, columnas)
    except Exception as e:
        st.error(f"❌ No se pudo leer «{os.path.basename(ruta)}»: {e}")
        return pd.DataFrame(columns=list(columnas))


def cargar_ofertas():
    ruta = ruta_datos(ARCHIVO_COT)
    df = _leer_cache(ruta, tuple(COLS_COT), _mtime(ruta)).copy()
    if not df.empty:
        df["ESTADO_FIRMA"] = df["ESTADO_FIRMA"].map(estado_norm)   # vacío o raro = PENDIENTE
    return df


@st.cache_data(show_spinner=False)
def _catalogo(ruta, mtime):
    try:
        df = pd.read_excel(ruta, dtype=str).fillna("")
    except Exception:
        return pd.DataFrame()
    df.columns = [norm_col(c) for c in df.columns]
    return df.apply(lambda c: c.str.strip())


def columna(df, *claves):
    """Primera columna cuyo nombre coincide exacto con alguna clave; si no, que la contenga."""
    for k in claves:
        if k in df.columns:
            return k
    for k in claves:
        for c in df.columns:
            if k in c:
                return c
    return None


def cargar_catalogo():
    ruta = ruta_datos(ARCHIVO_MATERIALES)
    df = _catalogo(ruta, _mtime(ruta)).copy() if os.path.exists(ruta) else pd.DataFrame()
    if df.empty:
        return df, None, None, None, None
    cols = df.columns
    c_cod = columna(df, "CODIGO", "COD MATERIAL", "COD") or cols[min(1, len(cols) - 1)]
    c_desc = columna(df, "DESCRIPCION", "DESC", "NOMBRE") or cols[min(2, len(cols) - 1)]
    return df, c_cod, c_desc, columna(df, "REFERENCIA", "REF"), columna(df, "UNIDAD", "UND")


def cargar_clientes():
    for nombre in (ARCHIVO_CLIENTES, ARCHIVO_PROVEEDORES):
        ruta = ruta_datos(nombre)
        if os.path.exists(ruta):
            df = _catalogo(ruta, _mtime(ruta)).copy()
            if not df.empty:
                c_nom = columna(df, "RAZON SOCIAL /NOMBRE", "RAZON SOCIAL", "NOMBRE", "CLIENTE", "PROVEEDOR") or df.columns[0]
                return (df, c_nom, columna(df, "NIT", "DOC"), columna(df, "DIRECCION", "DIREC"),
                        columna(df, "TELEFONO / CELULAR", "TELEFONO", "TEL"), nombre)
    return pd.DataFrame(), None, None, None, None, None


def guardar_datos(df, ruta):
    """Guarda de forma atómica. Devuelve None si todo salió bien, o el mensaje de error."""
    df = df.copy()
    for col in COLS_NUM:
        if col in df.columns:
            df[col] = df[col].map(lambda x: a_num(x) if str(x).strip() not in ("", "nan", "None") else None)
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".xlsx", dir=os.path.dirname(os.path.abspath(ruta)))
        os.close(fd)
        df.to_excel(tmp, index=False)
        os.replace(tmp, ruta)
        return None
    except Exception as e:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        return f"No se pudo guardar «{os.path.basename(ruta)}» (¿está abierto en Excel?): {e}"


def siguiente_consecutivo(df, anio):
    ultimo = 0
    if not df.empty:
        for c in df["CONSECUTIVO"].astype(str).str.strip().unique():
            m = re.fullmatch(rf"COT-{anio}-(\d+)", c)
            if m:
                ultimo = max(ultimo, int(m.group(1)))
    return f"COT-{anio}-{ultimo + 1:04d}"


def registrar_oferta(cab, lineas):
    """Genera el consecutivo y guarda, todo bajo candado y con datos recién leídos."""
    with obtener_lock():
        ruta = ruta_datos(ARCHIVO_COT)
        try:
            df = leer_directo(ruta, COLS_COT)
        except Exception as e:
            return None, f"No se pudo leer la base de cotizaciones: {e}"
        cons = siguiente_consecutivo(df, cab["fecha"].year)
        filas = [{
            "CONSECUTIVO": cons, "FECHA": cab["fecha"].isoformat(), "CLIENTE": cab["cliente"],
            "NIT_CLIENTE": cab["nit"], "DIRECCION": cab["direccion"], "TELEFONO": cab["telefono"],
            "MONEDA": cab["moneda"], "TRM": cab["trm"] if cab["moneda"] == "USD" else 0.0,
            "VALIDEZ_OFERTA": cab["validez"].strip(), "FORMA_PAGO": cab["pago"].strip(),
            "CONDICIONES": cab["condiciones"].strip(), "ELABORADO_POR": cab["elaborado"].strip(),
            "APROBADO_POR": "PENDIENTE DE FIRMA", "ESTADO_FIRMA": PENDIENTE,
            "CODIGO_MATERIAL": l["codigo"].strip().upper(), "DESCRIPCION": l["descripcion"].strip().upper(),
            "REFERENCIA": l["referencia"].strip() or "N/A", "UNIDAD": l["unidad"].strip() or "Und",
            "CANTIDAD": l["cantidad"], "COSTO_UNITARIO_COP": l["costo"], "MARGEN_PCT": cab["margen"],
            "PRECIO_UNITARIO_FINAL": l["precio"], "SUBTOTAL": l["subtotal"],
            "IVA_PCT": cab["iva_pct"], "FECHA_APROBACION": "", "MOTIVO_ANULACION": "",
        } for l in lineas]
        df = pd.concat([pd.DataFrame(filas, columns=COLS_COT), df], ignore_index=True)   # la nueva queda arriba
        error = guardar_datos(df, ruta)
        return (None, error) if error else (cons, None)


def actualizar_oferta(cons, nuevo_estado, extras=None, solo_si=None):
    """Cambia el estado de una oferta. Devuelve None si OK o el mensaje de error."""
    with obtener_lock():
        ruta = ruta_datos(ARCHIVO_COT)
        try:
            df = leer_directo(ruta, COLS_COT)
        except Exception as e:
            return f"No se pudo leer la base de cotizaciones: {e}"
        mask = df["CONSECUTIVO"] == cons
        if not mask.any():
            return "La oferta ya no existe."
        actual = estado_norm(df.loc[mask, "ESTADO_FIRMA"].iloc[0])
        if solo_si and actual != solo_si:
            return f"La oferta cambió de estado mientras la revisaba (ahora está {actual})."
        df.loc[mask, "ESTADO_FIRMA"] = nuevo_estado
        for campo, valor in (extras or {}).items():
            df.loc[mask, campo] = valor
        return guardar_datos(df, ruta)


def consecutivos_en_conflicto(df):
    """Consecutivos usados por ofertas distintas (error de la versión anterior)."""
    if df.empty:
        return []
    claves = df[CLAVE_CABECERA].agg("|".join, axis=1)
    n = pd.Series(claves.values, index=df["CONSECUTIVO"].values).groupby(level=0).nunique()
    return n[n > 1].index.tolist()


def reparar_consecutivos():
    """Conserva el número en la oferta más antigua y renumera las demás. Devuelve (cambios, error)."""
    with obtener_lock():
        ruta = ruta_datos(ARCHIVO_COT)
        try:
            df = leer_directo(ruta, COLS_COT)
        except Exception as e:
            return [], f"No se pudo leer la base de cotizaciones: {e}"
        clave = df[CLAVE_CABECERA].agg("|".join, axis=1)
        cambios = []
        for cons in df["CONSECUTIVO"].unique():
            en_cons = df["CONSECUTIVO"] == cons
            grupos = list(dict.fromkeys(clave[en_cons]))        # de arriba a abajo en el archivo
            if len(grupos) < 2:
                continue

            def antiguedad(i, grupos=grupos):
                f_txt = grupos[i].split("|")[1]
                f = pd.to_datetime(f_txt, errors="coerce", dayfirst="/" in f_txt)
                return (f if pd.notna(f) else pd.Timestamp.max, -i)   # por fecha; a igual fecha, la de más abajo

            orden = sorted(range(len(grupos)), key=antiguedad)        # de la más antigua a la más nueva
            anio = (re.search(r"COT-(\d{4})-", cons) or [None, date.today().year])[1]
            for i in orden[1:]:                                       # la más antigua conserva el número
                g = grupos[i]
                nuevo = siguiente_consecutivo(df, anio)
                df.loc[en_cons & (clave == g), "CONSECUTIVO"] = nuevo
                cambios.append(f"{cons} → {nuevo} ({g.split('|')[0]}, {fmt_fecha(g.split('|')[1])})")
        if not cambios:
            return [], None
        respaldo = f"{os.path.splitext(ruta)[0]}_respaldo_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        shutil.copy2(ruta, respaldo)
        error = guardar_datos(df, ruta)
        return ([], error) if error else (cambios, None)


def clave_gerencia():
    """Contraseña de gerencia. Se busca, en este orden, en .streamlit/secrets.toml:
    1) GERENCIA_PASSWORD (arriba de todo, antes de cualquier [tabla]);
    2) dentro de [passwords], el usuario «Gerencia» (o «GERENCIA_PASSWORD»);
    3) la variable de entorno GERENCIA_PASSWORD."""
    valor = None
    try:
        valor = st.secrets.get("GERENCIA_PASSWORD")
        if not valor:
            for nombre, clave in dict(st.secrets.get("passwords", {})).items():
                if str(nombre).strip().lower() in ("gerencia", "gerencia_password"):
                    valor = clave
                    break
    except Exception:
        pass
    valor = str(valor).strip() if valor else ""
    return valor or os.environ.get("GERENCIA_PASSWORD")


def diagnostico_clave():
    """Dice dónde está buscando la app la clave de gerencia (sin mostrar ninguna contraseña)."""
    carpeta = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    usuario = os.path.join(os.path.expanduser("~"), ".streamlit", "secrets.toml")
    partes = [f"carpeta desde donde corre la app: {os.getcwd()}",
              f"secrets.toml en esa carpeta: {'sí' if os.path.exists(carpeta) else 'NO'}",
              f"secrets.toml en la carpeta de tu usuario: {'sí' if os.path.exists(usuario) else 'NO'}"]
    try:
        suelta = bool(st.secrets.get("GERENCIA_PASSWORD"))
        nombres = [str(n).strip().lower() for n in dict(st.secrets.get("passwords", {}))]
        partes.append(f"GERENCIA_PASSWORD suelta: {'sí' if suelta else 'no'}")
        partes.append("usuario Gerencia dentro de [passwords]: "
                      + ("sí" if any(n in ("gerencia", "gerencia_password") for n in nombres) else "no"))
    except Exception as e:
        partes.append(f"Streamlit no pudo leer los secretos ({type(e).__name__})")
    return " · ".join(partes)


def verificar_clave(ingresada):
    """Devuelve None si la contraseña es correcta, o el mensaje de error."""
    clave = clave_gerencia()
    if not clave:
        return ("La contraseña de gerencia no está configurada. Defina GERENCIA_PASSWORD en "
                ".streamlit/secrets.toml o como variable de entorno. Diagnóstico: " + diagnostico_clave())
    if not hmac.compare_digest(ingresada.strip().encode(), clave.encode()):
        return "Contraseña de gerencia incorrecta."
    return None


def flash(clave, mensaje, tipo="success"):
    st.session_state[f"_flash_{clave}"] = (tipo, mensaje)


def mostrar_flash(clave):
    dato = st.session_state.pop(f"_flash_{clave}", None)
    if dato:
        getattr(st, dato[0])(dato[1])


# =============================================================================
# CÁLCULOS
# =============================================================================
def calc_precio(costo_cop, moneda, trm, margen):
    if moneda == "USD":
        if trm <= 0:
            return 0.0
        costo_cop = costo_cop / trm
    return round(costo_cop * (1 + margen / 100), 2)


def totales_oferta(d):
    """(moneda, iva_pct o None si la oferta no definía IVA, subtotal, iva, total)."""
    moneda = d["MONEDA"].iloc[0] or "COP"
    subtotal = float(d["SUBTOTAL"].map(a_num).sum())
    v = str(d["IVA_PCT"].iloc[0]).strip()
    iva_pct = a_num(v) if v else None
    iva = subtotal * iva_pct / 100 if iva_pct else 0.0
    return moneda, iva_pct, subtotal, iva, subtotal + iva


# =============================================================================
# DOCUMENTO IMPRIMIBLE
# =============================================================================
@st.cache_data(show_spinner=False)
def _logo_desde_archivo(ruta, mtime):
    with open(ruta, "rb") as f:
        datos = f.read()
    ext = os.path.splitext(ruta)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "webp": "webp"}.get(ext, "png")
    return f"data:image/{mime};base64," + base64.b64encode(datos).decode()


def obtener_logo():
    carpetas = []
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        carpetas += [base, os.path.join(base, "..")]
    except NameError:
        pass
    carpetas.append(os.getcwd())
    for carpeta in carpetas:
        for nombre in LOGOS_ARCHIVO:
            ruta = os.path.join(carpeta, nombre)
            if os.path.isfile(ruta):
                try:
                    return _logo_desde_archivo(ruta, os.path.getmtime(ruta))
                except OSError:
                    pass
    return LOGO_EMBEBIDO


CSS_OFERTA = """
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;margin:0;padding:12px;background:#fff;font-size:11px}
.doc{position:relative;padding:22px 26px;border:1px solid #d5deea;border-radius:6px;overflow:hidden;background:#fff}
table{width:100%;border-collapse:collapse}
.cab td{vertical-align:top}
.emp{display:flex;align-items:center}
.logo{max-height:62px;max-width:230px;margin-right:16px}
.emp h1{margin:0 0 4px;font-size:19px;color:#0b2a55}
.emp p{margin:1px 0;font-size:10.5px;color:#444}
.ord{border:1.5px solid #0b2a55;border-radius:6px;padding:10px 14px;text-align:right}
.ord .titulo{font-size:14px;font-weight:bold;color:#0b2a55;margin:2px 0}
.ord .num{font-size:21px;font-weight:bold;color:#000;margin:2px 0 6px}
.ord .fila{font-size:10.5px;color:#333;margin:3px 0}
.sep{border-top:3px solid #0b2a55;margin:14px 0}
.info{margin-bottom:14px;border:1px solid #c9d6e8}
.info td{padding:5px 8px;border:1px solid #dbe4f0;font-size:10.5px;vertical-align:top}
.info td.k{width:13%;background:#eef3fa;color:#0b2a55;font-weight:bold}
.items{margin-bottom:12px;font-size:10.5px}
.items thead{display:table-header-group}
.items th{background:#eef3fa;color:#0b2a55;border-top:2px solid #0b2a55;border-bottom:2px solid #0b2a55;
 padding:7px 6px;font-size:9.5px;text-transform:uppercase}
.items td{padding:7px 6px;border-bottom:1px solid #dbe4f0}
.items tr{page-break-inside:avoid}
.items tbody tr:nth-child(even) td{background:#f8fafd}
.c{text-align:center}.r{text-align:right}.l{text-align:left}.nw{white-space:nowrap}
.res{margin-bottom:10px}.res>tbody>tr>td{vertical-align:top}
.obs{border:1px solid #c9d6e8;border-radius:4px;padding:8px 10px;font-size:10.5px;min-height:70px}
.obs b{color:#0b2a55}
.tot td{padding:6px 10px;font-size:11px;border-bottom:1px solid #dbe4f0}
.tot tr.final td{border-top:2px solid #0b2a55;border-bottom:2px solid #0b2a55;background:#eef3fa;
 color:#0b2a55;font-weight:bold;font-size:13px}
.letras{border:1px solid #c9d6e8;border-radius:4px;padding:7px 10px;font-size:10.5px;margin-bottom:6px}
.letras b{color:#0b2a55}
.firmas{margin-top:8px;text-align:center;page-break-inside:avoid}
.firmas td{width:33%;padding:0 14px;vertical-align:bottom}
.firmas .esp{height:36px}
.firmas .nom{font-weight:bold;font-size:11px;color:#0b2a55;min-height:15px}
.firmas .lin{border-top:1px solid #333;padding-top:4px;font-size:10px;color:#333}
.firmas .sub{font-size:9px;color:#666;margin-top:1px;min-height:11px}
.marca{position:absolute;top:36%;left:8%;font-size:110px;color:rgba(198,40,40,.16);
 transform:rotate(-25deg);font-weight:bold;pointer-events:none}
.marca.gris{color:rgba(110,110,110,.16)}
.btn{display:block;width:100%;background:#004080;color:#fff;padding:12px;border:0;border-radius:5px;
 font-weight:bold;font-size:14px;cursor:pointer;margin-bottom:10px}
@page{size:Letter;margin:0}
@media print{.no-print{display:none!important}body{padding:0}
 .doc{border:0;border-radius:0;padding:14mm}}
"""


def generar_html_oferta(cons, d, imprimible=True):
    p = d.iloc[0]
    estado = estado_norm(p["ESTADO_FIRMA"])
    moneda, iva_pct, subtotal, iva, total = totales_oferta(d)
    trm = a_num(p["TRM"])
    moneda_txt = "COP (Peso Colombiano)" if moneda == "COP" else f"USD (TRM {fmt_dinero(trm)})"

    filas = []
    for n, (_, r) in enumerate(d.iterrows(), start=1):
        filas.append(
            f'<tr><td class="c">{n}</td><td class="c nw">{esc(r["CODIGO_MATERIAL"])}</td>'
            f'<td class="l">{esc(r["DESCRIPCION"])}</td><td class="c">{esc(r["REFERENCIA"] or "N/A")}</td>'
            f'<td class="c">{fmt_num(a_num(r["CANTIDAD"]))}</td><td class="c">{esc(r["UNIDAD"] or "Und")}</td>'
            f'<td class="r nw">{fmt_dinero(a_num(r["PRECIO_UNITARIO_FINAL"]), moneda)}</td>'
            f'<td class="r nw">{fmt_dinero(a_num(r["SUBTOTAL"]), moneda)}</td></tr>'
        )

    filas_tot = f'<tr><td><b>Subtotal</b></td><td class="r">{fmt_dinero(subtotal, moneda)}</td></tr>'
    if iva_pct is not None:
        filas_tot += f'<tr><td><b>IVA ({fmt_num(iva_pct)}%)</b></td><td class="r">{fmt_dinero(iva, moneda)}</td></tr>'
    filas_tot += f'<tr class="final"><td>VALOR TOTAL</td><td class="r">{fmt_dinero(total, moneda)}</td></tr>'

    letras = total_en_letras(total, moneda)
    bloque_letras = f'<div class="letras"><b>SON:</b> {esc(letras)}</div>' if letras else ""
    aprobada = estado == FIRMADO
    firma_aprob = esc(p["APROBADO_POR"]) if aprobada else ""
    sub_aprob = f"Aprobada el {fmt_fecha(p['FECHA_APROBACION'])}" if aprobada and p["FECHA_APROBACION"] else ""
    marca = ""
    if estado == ANULADA:
        marca = '<div class="marca">ANULADA</div>'
    elif estado == PENDIENTE:
        marca = '<div class="marca gris">BORRADOR</div>'
    boton = ('<button class="btn no-print" onclick="window.print()">🖨️ Imprimir / Guardar como PDF</button>'
             if imprimible else "")
    logo_src = obtener_logo()
    logo = f'<img class="logo" src="{logo_src}" alt="" onerror="this.remove()">' if logo_src else ""
    obs = esc(p["CONDICIONES"] or OBS_DEFECTO)
    e = EMPRESA

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>{esc(cons)}</title><style>{CSS_OFERTA}</style></head><body>
{boton}
<div class="doc">{marca}
<table class="cab"><tr>
<td style="width:58%"><div class="emp">{logo}<div>
<h1>{esc(e['nombre'])}</h1>
<p><b>Nit:</b> {esc(e['nit'])} · Régimen {esc(e['regimen'])}</p>
<p>{esc(e['direccion'])}</p>
<p>Tel. {esc(e['telefono'])} · {esc(e['correo'])}</p>
</div></div></td>
<td style="width:42%"><div class="ord">
<div class="titulo">OFERTA COMERCIAL</div>
<div class="num">{esc(cons)}</div>
<div class="fila"><b>Fecha:</b> {esc(fmt_fecha(p['FECHA']))}</div>
<div class="fila"><b>Validez de la oferta:</b> {esc(p['VALIDEZ_OFERTA'])}</div>
</div></td></tr></table>
<div class="sep"></div>
<table class="info">
<tr><td class="k">Señores</td><td style="width:42%">{esc(p['CLIENTE'])}</td>
<td class="k">Forma de pago</td><td>{esc(p['FORMA_PAGO'])}</td></tr>
<tr><td class="k">Nit / Cédula</td><td>{esc(p['NIT_CLIENTE'])}</td>
<td class="k">Moneda</td><td>{esc(moneda_txt)}</td></tr>
<tr><td class="k">Dirección</td><td>{esc(p['DIRECCION'])}</td>
<td class="k">Teléfono</td><td>{esc(p['TELEFONO'])}</td></tr>
</table>
<table class="items"><thead><tr>
<th style="width:5%">Ítem</th><th style="width:12%">Código</th><th class="l">Descripción</th>
<th style="width:8%">Ref</th><th style="width:7%">Cant.</th><th style="width:6%">Und.</th>
<th class="r" style="width:14%">Vr. Unitario</th><th class="r" style="width:14%">Vr. Total</th>
</tr></thead><tbody>{''.join(filas)}</tbody></table>
<table class="res"><tr>
<td style="width:58%"><div class="obs"><b>Observaciones / Términos:</b><br>
<div style="margin-top:4px;color:#333">{obs}</div></div></td>
<td style="width:2%"></td>
<td style="width:40%"><table class="tot">{filas_tot}</table></td></tr></table>
{bloque_letras}
<table class="firmas"><tr>
<td><div class="esp"></div><div class="nom">{esc(p['ELABORADO_POR'])}</div>
<div class="lin">Elaborado por</div><div class="sub"></div></td>
<td><div class="esp"></div><div class="nom">{firma_aprob}</div>
<div class="lin">Aprobado / Gerencia</div><div class="sub">{sub_aprob}</div></td>
<td><div class="esp"></div><div class="nom">&nbsp;</div>
<div class="lin">Aceptación del cliente (Firma y Sello)</div><div class="sub">Nombre, C.C. y fecha</div></td>
</tr></table>
</div></body></html>"""


# =============================================================================
# PESTAÑA 1: ELABORAR
# =============================================================================
def nuevo_item(codigo="", descripcion="", referencia="N/A", unidad="Und", cantidad=1.0, costo=0.0):
    return {"_id": uuid.uuid4().hex[:8], "CODIGO": codigo, "DESCRIPCION": descripcion, "REFERENCIA": referencia,
            "UNIDAD": unidad, "CANTIDAD": cantidad, "COSTO": costo}


def render_item(idx, it, ver, moneda, trm, margen):
    def k(campo):
        return f"cot_i_{campo}_{ver}_{it['_id']}"

    st.markdown(f"**Ítem #{idx + 1}**")
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1.4, 2.8, 1, 0.8, 0.8, 1.3, 0.5])
    with c1:
        cod = st.text_input(f"Código #{idx + 1}", value=it["CODIGO"], key=k("cod"))
    with c2:
        desc = st.text_input(f"Descripción #{idx + 1}", value=it["DESCRIPCION"], key=k("desc"))
    with c3:
        ref = st.text_input(f"Referencia #{idx + 1}", value=it["REFERENCIA"], key=k("ref"))
    with c4:
        cant = st.number_input(f"Cant #{idx + 1}", min_value=0.0, value=float(it["CANTIDAD"]), step=1.0, key=k("cant"))
    with c5:
        und = st.text_input(f"Und #{idx + 1}", value=it["UNIDAD"], key=k("und"))
    with c6:
        costo = st.number_input(f"Costo base COP #{idx + 1}", min_value=0.0, value=float(it["COSTO"]),
                                step=100.0, key=k("costo"))
    with c7:
        st.write("")
        eliminar = st.button("🗑️", key=k("del"), help="Quitar este ítem")

    precio = calc_precio(costo, moneda, trm, margen)
    subtotal = round(precio * cant, 2)
    st.caption(f"Precio unitario: **{fmt_dinero(precio, moneda)}** · Subtotal: **{fmt_dinero(subtotal, moneda)}**")
    nuevo = {"_id": it["_id"], "CODIGO": cod, "DESCRIPCION": desc, "REFERENCIA": ref,
             "UNIDAD": und, "CANTIDAD": cant, "COSTO": costo}
    return nuevo, precio, subtotal, eliminar


def validar_oferta(cab, items):
    errores = []
    if cab["cliente"] == SIN_CLIENTE:
        errores.append("Seleccione un cliente.")
    if not cab["elaborado"].strip():
        errores.append("Indique quién elabora la oferta.")
    if not cab["validez"].strip():
        errores.append("Indique la validez de la oferta (ej. 30 días).")
    if not cab["pago"].strip():
        errores.append("Indique la forma de pago.")
    if cab["moneda"] == "USD" and cab["trm"] <= 0:
        errores.append("Para cotizar en dólares la TRM debe ser mayor a 0.")
    if not items:
        errores.append("Agregue al menos un ítem a la oferta.")
    for n, it in enumerate(items, start=1):
        if not it["CODIGO"].strip():
            errores.append(f"Ítem #{n}: falta el código.")
        if not it["DESCRIPCION"].strip():
            errores.append(f"Ítem #{n}: falta la descripción.")
        if it["CANTIDAD"] <= 0:
            errores.append(f"Ítem #{n}: la cantidad debe ser mayor a 0.")
        if it["COSTO"] <= 0:
            errores.append(f"Ítem #{n}: el costo base debe ser mayor a 0.")
    return errores


def tab_elaborar():
    st.subheader("📋 Paso 1: Datos Generales, Cliente y Condiciones Comerciales")
    mostrar_flash("elaborar")

    ss = st.session_state
    ss.setdefault("cot_items", [])
    ss.setdefault("cot_ver", 0)

    df_cot = cargar_ofertas()
    df_cli, c_nom, c_nit, c_dir, c_tel, origen_cli = cargar_clientes()
    nombres_cli = sorted({n for n in df_cli[c_nom] if n}) if c_nom else []

    # Duplicar una oferta: se precargan los campos antes de crear los widgets
    pf = ss.pop("cot_prefill", None)
    if pf:
        ss.cot_ver += 1
        ss.cot_items = pf["items"]
        for campo, valor in pf["campos"].items():
            if campo == "cliente" and valor not in nombres_cli:
                continue
            ss[f"cot_{campo}_{ss.cot_ver}"] = valor
    ver = ss.cot_ver

    def k(n):
        return f"cot_{n}_{ver}"

    ss.setdefault(k("elab"), ss.get("username", ""))

    col1, col2, col3 = st.columns(3)
    with col1:
        proximo = siguiente_consecutivo(df_cot, date.today().year)
        st.text_input("Número de Consecutivo", value=f"{proximo} (se confirma al guardar)", disabled=True)
    with col2:
        fecha = st.date_input("Fecha de Oferta", key=k("fecha"))
    with col3:
        moneda_label = st.selectbox("Moneda", list(MONEDAS), key=k("moneda"))
    moneda = MONEDAS[moneda_label]

    col_p1, col_p2, col_p3, col_p4 = st.columns([2, 1, 1, 1])
    with col_p1:
        cliente = st.selectbox("Cliente / Tercero", [SIN_CLIENTE] + nombres_cli, key=k("cliente"))
    with col_p2:
        trm = st.number_input("TRM del día (COP/USD)", min_value=0.0, step=10.0, format="%.2f", key=k("trm"),
                              help="Solo se usa si la moneda es USD.")
    with col_p3:
        margen = st.number_input("Margen de ganancia (%)", min_value=0.0, step=1.0, format="%.2f", key=k("margen"),
                                 help="Recargo sobre el costo: precio = costo × (1 + %).")
    with col_p4:
        iva_label = st.selectbox("IVA de la oferta", list(IVA_OPCIONES), key=k("iva"))
    iva_pct = IVA_OPCIONES[iva_label]

    nit = direccion = telefono = ""
    if cliente != SIN_CLIENTE and c_nom:
        fila = df_cli[df_cli[c_nom] == cliente]
        if not fila.empty:
            f = fila.iloc[0]
            nit = f[c_nit] if c_nit else ""
            direccion = f[c_dir] if c_dir else ""
            telefono = f[c_tel] if c_tel else ""
        st.caption(f"NIT: {nit or 'N/A'} · Dirección: {direccion or 'N/A'} · Tel.: {telefono or 'N/A'}")
    if origen_cli == ARCHIVO_PROVEEDORES:
        st.caption("ℹ️ Los clientes se toman de base_proveedores.xlsx. Si creas base_clientes.xlsx con las mismas "
                   "columnas, se usará esa.")

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        validez = st.text_input("Validez de la oferta", placeholder="Ej: 30 días", key=k("validez"))
    with col_c2:
        pago = st.text_input("Forma de pago", placeholder="Ej: Contado / Crédito 30 días", key=k("pago"))
    with col_c3:
        elaborado = st.text_input("Elaborado por (responsable)", key=k("elab"))
    condiciones = st.text_area("Observaciones / Términos adicionales", key=k("cond"),
                               placeholder="Ej: Suministro cotizado bajo los términos comerciales vigentes...")

    st.markdown("---")

    # --- Catálogo y alta de ítems ---
    st.subheader("📦 Catálogo de Materiales")
    df_mat, c_cod, c_desc, c_ref, c_und = cargar_catalogo()
    opciones = {SIN_MATERIAL: None, ITEM_LIBRE: "libre"}
    if df_mat.empty:
        st.info("No hay materiales cargados en el catálogo: puede agregar ítems libres.")
    else:
        filtro = st.text_input("🔍 Filtrar catálogo (código, descripción o familia):", key=k("filtro"),
                               placeholder="Ej: andamios, SER01173...")
        df_vis = df_mat
        if filtro.strip():
            mask = df_mat.apply(lambda c: c.str.contains(filtro.strip(), case=False, regex=False)).any(axis=1)
            df_vis = df_mat[mask]
        with st.expander(f"Ver catálogo ({len(df_vis)} materiales)"):
            st.dataframe(df_vis.head(500), use_container_width=True, hide_index=True)
        for _, r in df_vis.head(500).iterrows():
            opciones[f"{r[c_cod]} — {r[c_desc]}"] = r
    if ss.get(k("mat")) not in opciones:
        ss[k("mat")] = SIN_MATERIAL

    st.subheader("➕ Agregar Ítem a la Cotización")
    col_a1, col_a2 = st.columns([4, 1])
    with col_a1:
        eleccion = st.selectbox("Material (escriba para buscar)", list(opciones), key=k("mat"))
    with col_a2:
        st.write("")
        agregar = st.button("📥 Agregar ítem", type="primary", use_container_width=True, key=k("agregar"))
    if agregar:
        sel = opciones[eleccion]
        if sel is None:
            st.error("⚠️ Seleccione un material del catálogo o elija «Ítem libre».")
        else:
            if isinstance(sel, str):          # ítem libre
                ss.cot_items.append(nuevo_item())
            else:
                ss.cot_items.append(nuevo_item(
                    sel[c_cod], sel[c_desc], (sel[c_ref] if c_ref else "") or "N/A",
                    (sel[c_und] if c_und else "") or "Und"))
            st.rerun()

    # --- Detalle ---
    st.markdown("---")
    st.subheader("📊 Detalle de la Oferta")
    if moneda == "USD" and trm <= 0:
        st.warning("⚠️ Ingrese la TRM del día: sin ella los precios en USD aparecen en 0.")

    lineas, items_vivos, quitar = [], [], False
    for idx, it in enumerate(ss.cot_items):
        nuevo, precio, subtotal, eliminar = render_item(idx, it, ver, moneda, trm, margen)
        st.markdown("---")
        if eliminar:
            quitar = True
            continue
        items_vivos.append(nuevo)
        lineas.append({"codigo": nuevo["CODIGO"], "descripcion": nuevo["DESCRIPCION"],
                       "referencia": nuevo["REFERENCIA"], "unidad": nuevo["UNIDAD"],
                       "cantidad": nuevo["CANTIDAD"], "costo": nuevo["COSTO"],
                       "precio": precio, "subtotal": subtotal})
    ss.cot_items = items_vivos
    if quitar:
        st.rerun()

    if not lineas:
        st.info("ℹ️ Agrega al menos un ítem para armar la oferta.")
        return

    subtotal_total = round(sum(l["subtotal"] for l in lineas), 2)
    iva_valor = round(subtotal_total * iva_pct / 100, 2)
    m1, m2, m3 = st.columns(3)
    m1.metric("Subtotal", fmt_dinero(subtotal_total, moneda))
    m2.metric(f"IVA ({fmt_num(iva_pct)}%)", fmt_dinero(iva_valor, moneda))
    m3.metric("TOTAL DE LA OFERTA", fmt_dinero(subtotal_total + iva_valor, moneda))

    if st.button("💾 Guardar como Elaborada (Pendiente de Firma)", type="primary", use_container_width=True,
                 key="cot_guardar"):
        cab = {"fecha": fecha, "cliente": cliente, "nit": nit, "direccion": direccion, "telefono": telefono,
               "moneda": moneda, "trm": trm, "margen": margen, "iva_pct": iva_pct, "validez": validez,
               "pago": pago, "condiciones": condiciones, "elaborado": elaborado}
        errores = validar_oferta(cab, ss.cot_items)
        if errores:
            for e in errores:
                st.error(f"❌ {e}")
            return
        cons, error = registrar_oferta(cab, lineas)
        if error:
            st.error(f"❌ {error}")
            return
        flash("elaborar", f"✅ ¡Oferta **{cons}** guardada como ELABORADA! Ve a la pestaña «Buscar, Firmar e "
                          "Imprimir» para que la gerencia la apruebe y firme.")
        ss.cot_items = []
        ss.cot_ver += 1
        st.rerun()


# =============================================================================
# PESTAÑA 2: BUSCAR, FIRMAR E IMPRIMIR
# =============================================================================
def panel_diagnostico(df):
    conflictos = consecutivos_en_conflicto(df)
    if not conflictos:
        return
    with st.expander(f"🛠️ Hay {len(conflictos)} consecutivo(s) repetidos entre ofertas distintas", expanded=True):
        st.warning("Un error de la versión anterior asignó el mismo número a ofertas diferentes: "
                   f"{', '.join(conflictos)}. Al firmar, se firman todas las que comparten número. "
                   "La reparación conserva el número en la oferta más antigua y renumera las demás "
                   "(se guarda un respaldo antes). Revise después el estado de firma de las renumeradas.")
        with st.form("form_reparar"):
            clave = st.text_input("🔑 Contraseña de Gerencia", type="password")
            enviar = st.form_submit_button("🛠️ Reparar consecutivos")
        if enviar:
            error = verificar_clave(clave)
            if error:
                st.error(f"❌ {error}")
                return
            cambios, error = reparar_consecutivos()
            if error:
                st.error(f"❌ {error}")
            else:
                flash("gestion", "✅ Consecutivos reparados: " + " · ".join(cambios))
                st.rerun()


def tab_gestion():
    st.subheader("🔍 Gestión Gerencial: Buscar, Firmar e Imprimir Ofertas")
    mostrar_flash("gestion")

    df = cargar_ofertas()
    if df.empty:
        st.info("ℹ️ Aún no hay ofertas registradas en la base de datos.")
        return
    panel_diagnostico(df)

    filtro_estado = st.radio("Mostrar", ["Pendientes de firma", "Firmadas", "Anuladas", "Todas"],
                             horizontal=True, key="cot_filtro_estado")
    estado_buscado = {"Pendientes de firma": PENDIENTE, "Firmadas": FIRMADO, "Anuladas": ANULADA}.get(filtro_estado)
    df_f = df if estado_buscado is None else df[df["ESTADO_FIRMA"] == estado_buscado]

    texto = st.text_input("🔎 Buscar por consecutivo, cliente o NIT", key="cot_buscar").strip()
    if texto:
        mask = pd.Series(False, index=df_f.index)
        for col in ("CONSECUTIVO", "CLIENTE", "NIT_CLIENTE"):
            mask |= df_f[col].str.contains(texto, case=False, regex=False, na=False)
        df_f = df_f[mask]
    if df_f.empty:
        st.warning("⚠️ No se encontraron ofertas con los filtros seleccionados.")
        return

    resumen = {}
    for cons, g in df_f.groupby("CONSECUTIVO", sort=False):
        moneda = g["MONEDA"].iloc[0] or "COP"
        resumen[cons] = f"{cons} · {g['CLIENTE'].iloc[0]} · {fmt_dinero(g['SUBTOTAL'].map(a_num).sum(), moneda)}"
    cons = st.selectbox("Seleccione la oferta", list(resumen), format_func=resumen.get, key="cot_sel")

    d = df[df["CONSECUTIVO"] == cons]
    p = d.iloc[0]
    estado = p["ESTADO_FIRMA"]
    moneda, iva_pct, subtotal, iva, total = totales_oferta(d)
    etiqueta = {PENDIENTE: "🔴 PENDIENTE DE FIRMA", FIRMADO: "🟢 APROBADA Y FIRMADA", ANULADA: "⚫ ANULADA"}[estado]

    st.markdown("---")
    st.markdown(f"### 📁 Oferta `{cons}` · {etiqueta}")
    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown(f"**Cliente:** {p['CLIENTE']}")
        st.markdown(f"**NIT:** {p['NIT_CLIENTE']}")
    with i2:
        st.markdown(f"**Fecha:** {fmt_fecha(p['FECHA'])}")
        st.markdown(f"**Validez / Pago:** {p['VALIDEZ_OFERTA']} · {p['FORMA_PAGO']}")
    with i3:
        st.markdown(f"**Elaborado por:** {p['ELABORADO_POR']}")
        if estado == FIRMADO:
            st.markdown(f"**Aprobada por:** {p['APROBADO_POR']} ({fmt_fecha(p['FECHA_APROBACION'])})")
        if estado == ANULADA and p["MOTIVO_ANULACION"]:
            st.markdown(f"**Motivo de anulación:** {p['MOTIVO_ANULACION']}")

    tabla = pd.DataFrame({
        "Código": d["CODIGO_MATERIAL"], "Descripción": d["DESCRIPCION"],
        "Cant": d["CANTIDAD"].map(lambda x: fmt_num(a_num(x))), "Und": d["UNIDAD"],
        "Vr. Unitario": d["PRECIO_UNITARIO_FINAL"].map(lambda x: fmt_dinero(a_num(x), moneda)),
        "Subtotal": d["SUBTOTAL"].map(lambda x: fmt_dinero(a_num(x), moneda)),
    })
    st.dataframe(tabla, use_container_width=True, hide_index=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Subtotal", fmt_dinero(subtotal, moneda))
    m2.metric(f"IVA ({fmt_num(iva_pct)}%)" if iva_pct is not None else "IVA", fmt_dinero(iva, moneda)
              if iva_pct is not None else "No discriminado")
    m3.metric("TOTAL", fmt_dinero(total, moneda))

    # Documento: vista previa para todos; impresión/descarga solo cuando está firmada
    with st.expander("📄 Vista previa del documento", expanded=(estado == FIRMADO)):
        components.html(generar_html_oferta(cons, d, imprimible=(estado == FIRMADO)), height=1250, scrolling=True)
    if estado == FIRMADO:
        st.download_button("⬇️ Descargar oferta (abrir y guardar como PDF)",
                           data=generar_html_oferta(cons, d).encode("utf-8"), file_name=f"{cons}.html",
                           mime="text/html", use_container_width=True, key=f"cot_dl_{cons}")
    elif estado == PENDIENTE:
        st.info("🔒 La impresión oficial se habilita cuando la gerencia firme la oferta.")

    st.markdown("---")
    col_ap, col_an = st.columns(2)
    with col_ap:
        if estado == PENDIENTE:
            with st.form(f"cot_form_aprobar_{cons}"):
                st.markdown("#### 🔒 Aprobación Gerencial")
                gerente = st.text_input("Nombre del Gerente / Aprobador")
                clave = st.text_input("Contraseña Gerencial", type="password")
                aprobar = st.form_submit_button("✍️ Firmar y Aprobar Oferta", type="primary")
            if aprobar:
                error = verificar_clave(clave)
                if error:
                    st.error(f"❌ {error}")
                elif not gerente.strip():
                    st.error("⚠️ Ingrese el nombre del gerente que aprueba.")
                else:
                    error = actualizar_oferta(cons, FIRMADO, {"APROBADO_POR": gerente.strip(),
                                                              "FECHA_APROBACION": date.today().isoformat()},
                                              solo_si=PENDIENTE)
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        flash("gestion", f"🎉 ¡Oferta **{cons}** firmada y aprobada con éxito!")
                        st.rerun()
        elif estado == FIRMADO:
            st.success(f"✅ Oferta aprobada y firmada por **{p['APROBADO_POR']}**.")
        else:
            st.warning("⚠️ Esta oferta está ANULADA y no se puede aprobar.")

    with col_an:
        if estado != ANULADA:
            with st.form(f"cot_form_anular_{cons}"):
                st.markdown("#### ⚠️ Zona de Peligro")
                motivo = st.text_input("Motivo de la anulación")
                confirmar = st.checkbox(f"Confirmo que deseo anular la oferta {cons}")
                anular = st.form_submit_button("🚫 Anular Oferta")
            if anular:
                if not confirmar:
                    st.warning("⚠️ Marque la casilla de confirmación para anular.")
                elif not motivo.strip():
                    st.warning("⚠️ Indique el motivo de la anulación.")
                else:
                    error = actualizar_oferta(cons, ANULADA, {"MOTIVO_ANULACION": motivo.strip()})
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        flash("gestion", f"🚫 La oferta **{cons}** fue ANULADA.")
                        st.rerun()

    if st.button("📄 Duplicar como nueva oferta", key=f"cot_dup_{cons}",
                 help="Copia cliente, condiciones e ítems a una oferta nueva para editarla."):
        margen = a_num(p["MARGEN_PCT"])
        campos = {"cliente": p["CLIENTE"], "moneda": next(l for l, c in MONEDAS.items() if c == moneda),
                  "trm": a_num(p["TRM"]), "margen": margen, "validez": p["VALIDEZ_OFERTA"],
                  "pago": p["FORMA_PAGO"], "cond": p["CONDICIONES"]}
        if iva_pct is not None:
            campos["iva"] = next((l for l, v in IVA_OPCIONES.items() if v == iva_pct), "19%")
        items = [nuevo_item(r["CODIGO_MATERIAL"], r["DESCRIPCION"], r["REFERENCIA"] or "N/A", r["UNIDAD"] or "Und",
                            a_num(r["CANTIDAD"]), a_num(r["COSTO_UNITARIO_COP"])) for _, r in d.iterrows()]
        st.session_state["cot_prefill"] = {"campos": campos, "items": items}
        flash("elaborar", f"📄 Oferta **{cons}** cargada como borrador nuevo. Revísala, ajusta lo necesario y guarda.",
              "info")
        st.rerun()


# =============================================================================
# PÁGINA
# =============================================================================
st.title("💼 Módulo de Cotizaciones y Ofertas Comerciales")
st.markdown("Genera, consolida, gestiona y exporta en PDF ofertas comerciales con control gerencial.")
st.markdown("---")

pestana1, pestana2 = st.tabs(["➕ Elaborar Nueva Oferta", "🔍 Buscar, Firmar e Imprimir Ofertas"])
with pestana1:
    tab_elaborar()
with pestana2:
    tab_gestion()
