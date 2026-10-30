"""
Órdenes de Compra y/o Servicios (multi-ítem) - módulo Streamlit.

Cambios clave frente a la versión anterior:
- Contraseña de gerencia fuera del código (st.secrets / variable de entorno).
- Escritura segura: relee el Excel justo antes de guardar, con candado y archivo temporal
  (evita perder órdenes de otros usuarios y consecutivos duplicados).
- "Anular" ya no borra: marca la orden como ANULADA (queda auditoría y no se reutiliza el consecutivo).
- Se eliminó st.stop() dentro de la pestaña 1 (dejaba las demás pestañas sin dibujar).
- Impresión con st.components + botón de descarga (los enlaces data: los bloquea Chrome).
- Todo el HTML escapado, cálculos centralizados, caché de lecturas, validaciones completas.
"""
import base64
import hmac
import io
import os
import re
import tempfile
import threading
import uuid
from datetime import date
from html import escape as esc

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Validación de seguridad: si no ha iniciado sesión, bloquea el módulo
if not st.session_state.get("password_correct", False):
    st.error("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal (Inicio / Principal).")
    st.stop()

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
# Logo embebido (AsuservicioSSS). Si existe un archivo logo.png junto a la app, ese tiene prioridad.
LOGO_EMBEBIDO = "data:image/png;base64,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"

EXCEL_OC = "Ordenes.xlsx"
EXCEL_PROVEEDORES = "base_proveedores.xlsx"
EXCEL_REQUISICIONES = "base_requisiciones.xlsx"

COLS_OC = [
    "ORDEN", "FECHA", "PROVEEDOR", "NIT", "REQUISICIO",
    "CODIGO", "DESCRIPCION", "REFERENCIA", "CANT", "UND",
    "IVA", "V. UNIT", "V.TOTAL", "ESTADO", "N. PEDIDO",
    "OBSERVACIONES", "ELABORADO_POR", "APROBADO_POR",
    "FECHA_APROBACION", "MOTIVO_ANULACION",  # columnas nuevas (se crean solas)
]
COLS_PROV = ["Nit", "Razon Social /Nombre", "Contacto", "Telefono / Celular", "Correo Electronico",
             "Direccion", "Ciudad", "Condicion de Pago", "Fecha registro"]
COLS_REQ = ["Requisicion", "Tipo Requisicion", "Fecha De Creacion", "Orden De Pedido", "Cec",
            "Cliente/Proyecto", "Area/Deprtamento", "Solicitante", "Cod Material", "Descripcion",
            "Ref", "Cant.", "Und.", "Observaciones"]

PREFIJO_OC = "OC-202604"
PREFIJO_OS = "OS-202605"
CONSECUTIVO_INICIAL = 100

ESTADO_ELABORADA = "ELABORADA"
ESTADO_APROBADA = "APROBADA"
ESTADO_ANULADA = "ANULADA"

IVA_OPCIONES = [0.0, 0.05, 0.19]
IVA_DEFECTO = 0.19
SIN_RQ = "-- Ninguna (Ingreso Manual) --"
SIN_PROV = "-- Seleccione Proveedor --"
OBS_DEFECTO = "Suministro autorizado bajo los términos contractuales vigentes."

EMPRESA = {
    "nombre": "Asuserviciosss SAS",
    "nit": "901224239-3",
    "direccion": "CL 67 22 62 CA 14 BRR PARNASO",
    "telefono": "3186565776",
    "correo": "asuserviciosss@hotmail.com",
    "regimen": "COMUN",
}


# =============================================================================
# ACCESO A DATOS
# =============================================================================
@st.cache_resource
def obtener_lock():
    """Un único candado compartido por todas las sesiones del servidor."""
    return threading.Lock()


def _limpiar(df, columnas):
    df = df.fillna("")
    for col in columnas:
        if col not in df.columns:
            df[col] = ""
    df = df[list(columnas)].astype(str)
    for col in columnas:
        df[col] = df[col].str.strip().replace(["nan", "NaN", "None", "<NA>"], "")
    return df


def leer_directo(archivo, columnas):
    """Lectura estricta (lanza error si falla). Se usa antes de escribir para no pisar datos."""
    if not os.path.exists(archivo):
        return pd.DataFrame(columns=list(columnas))
    return _limpiar(pd.read_excel(archivo, dtype=str), columnas)


@st.cache_data(show_spinner=False)
def _leer_cache(archivo, columnas, mtime):
    try:
        return leer_directo(archivo, columnas)
    except Exception as e:
        st.error(f"❌ No se pudo leer «{archivo}»: {e}")
        return pd.DataFrame(columns=list(columnas))


def cargar_datos(archivo, columnas):
    """Lectura para mostrar en pantalla; se recarga solo cuando cambia el archivo."""
    mtime = os.path.getmtime(archivo) if os.path.exists(archivo) else 0.0
    return _leer_cache(archivo, tuple(columnas), mtime).copy()


def guardar_datos(df, archivo):
    """Guarda de forma atómica. Devuelve None si todo salió bien, o el mensaje de error."""
    df = df.copy()
    for col in ("CANT", "V. UNIT", "V.TOTAL"):
        if col in df.columns:
            df[col] = df[col].map(parse_cant if col == "CANT" else parse_valor)
    tmp = None
    try:
        carpeta = os.path.dirname(os.path.abspath(archivo))
        fd, tmp = tempfile.mkstemp(suffix=".xlsx", dir=carpeta)
        os.close(fd)
        df.to_excel(tmp, index=False)
        os.replace(tmp, archivo)
        return None
    except Exception as e:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        return f"No se pudo guardar «{archivo}» (¿está abierto en Excel?): {e}"


def a_excel_bytes(df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()


# =============================================================================
# PARSEO Y FORMATO
# =============================================================================
def parse_valor(x, defecto=0.0):
    t = str(x).strip().replace("$", "").replace(" ", "")
    if t in ("", "nan", "None"):
        return defecto
    if "." in t and "," in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    elif "," in t:
        t = t.replace(",", "") if re.fullmatch(r"\d{1,3}(,\d{3})+", t) else t.replace(",", ".")
    elif "." in t and re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return defecto


def parse_cant(x, defecto=1.0):
    try:
        return float(str(x).strip().replace(",", "."))
    except ValueError:
        return defecto


def parse_iva(x, defecto=IVA_DEFECTO):
    t = str(x).strip()
    try:
        v = float(t.replace("%", "").replace(",", "."))
    except ValueError:
        return defecto
    if "%" in t:
        return v / 100
    return v / 100 if v > 1 else v


def fmt_cop(v):
    t = f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if t.endswith(",00"):
        t = t[:-3]
    return f"${t}"


def fmt_num(v):
    v = float(v)
    return str(int(v)) if v.is_integer() else f"{v:g}".replace(".", ",")


def fmt_pct(v):
    return f"{round(float(v) * 100)}%"


def fmt_fecha(x):
    t = str(x).strip()
    if not t:
        return ""
    try:
        return pd.to_datetime(t, dayfirst="/" in t).strftime("%d/%m/%Y")
    except Exception:
        return t


def fecha_dt(x):
    t = str(x).strip()
    try:
        return pd.to_datetime(t, dayfirst="/" in t)
    except Exception:
        return pd.NaT


def es_codigo_ser(codigo):
    return str(codigo).strip().upper().startswith("SER")


# =============================================================================
# LÓGICA DE NEGOCIO
# =============================================================================
def siguiente_consecutivo(df, prefijo):
    ultimo = 0
    if not df.empty:
        for orden in df["ORDEN"].astype(str).str.strip().unique():
            if orden.startswith(prefijo):
                sufijo = orden[len(prefijo):]
                if sufijo.isdigit():
                    ultimo = max(ultimo, int(sufijo))
    return max(ultimo, CONSECUTIVO_INICIAL - 1) + 1


def con_calculos(df):
    """Agrega columnas numéricas (_cant, _unit, _ivap, _base, _ivav, _total) a un DataFrame de ítems."""
    d = df.copy()
    d["_cant"] = d["CANT"].map(parse_cant)
    d["_unit"] = d["V. UNIT"].map(parse_valor)
    d["_ivap"] = d["IVA"].map(parse_iva)
    d["_base"] = d["_cant"] * d["_unit"]
    d["_ivav"] = d["_base"] * d["_ivap"]
    d["_total"] = d["_base"] + d["_ivav"]
    return d


def ordenar_recientes(df):
    if df.empty:
        return df
    nums = pd.to_numeric(df["ORDEN"].str.replace(r"\D", "", regex=True), errors="coerce").fillna(0)
    return (df.assign(_f=df["FECHA"].map(fecha_dt), _n=nums)
              .sort_values(["_f", "_n"], ascending=[False, False], na_position="last")
              .drop(columns=["_f", "_n"])
              .reset_index(drop=True))


def datos_proveedor(df_prov, nombre):
    info = {"Direccion": "N/A", "Telefono / Celular": "N/A", "Correo Electronico": "N/A",
            "Condicion de Pago": "Contado", "Nit": ""}
    if df_prov.empty or not nombre:
        return info
    m = df_prov[df_prov["Razon Social /Nombre"].str.lower() == nombre.strip().lower()]
    if not m.empty:
        fila = m.iloc[0]
        for k in info:
            if fila.get(k, ""):
                info[k] = fila[k]
    return info


def requisiciones_disponibles(df_req, df_oc, es_servicio):
    """RQ del tipo correcto que aún no tienen una orden activa (las ANULADAS no cuentan)."""
    if df_req.empty:
        return []
    tipo = "servicio" if es_servicio else "compra"
    d = df_req[df_req["Tipo Requisicion"].str.lower() == tipo]
    ocupadas = set()
    if not df_oc.empty:
        activas = df_oc[df_oc["ESTADO"].str.upper() != ESTADO_ANULADA]
        ocupadas = set(activas["REQUISICIO"].str.lower())
    return [r for r in d["Requisicion"].unique() if r and r.lower() not in ocupadas]


def validar_orden(proveedor, items, es_servicio):
    errores = []
    if proveedor == SIN_PROV:
        errores.append("Debe seleccionar un proveedor válido.")
    if not items:
        errores.append("Debe agregar al menos un ítem a la orden.")
    for n, it in enumerate(items, start=1):
        if not it["CODIGO"].strip():
            errores.append(f"Ítem #{n}: falta el código.")
        elif es_servicio and not es_codigo_ser(it["CODIGO"]):
            errores.append(f"Ítem #{n}: una Orden de Servicio solo admite códigos que empiecen por SER.")
        if not it["DESCRIPCION"].strip():
            errores.append(f"Ítem #{n}: falta la descripción.")
        if it["V. UNIT"] <= 0:
            errores.append(f"Ítem #{n}: el valor unitario debe ser mayor a 0.")
    return errores


def registrar_orden(es_servicio, req, proveedor, items, n_pedido, obs, elaborado, aprobado):
    """Genera el consecutivo y guarda, todo bajo candado y con datos recién leídos."""
    with obtener_lock():
        try:
            df = leer_directo(EXCEL_OC, COLS_OC)
            df_prov = leer_directo(EXCEL_PROVEEDORES, COLS_PROV)
        except Exception as e:
            return None, f"No se pudo leer la base de datos: {e}"

        if req != SIN_RQ and not df.empty:
            previas = df[(df["REQUISICIO"].str.lower() == req.lower())
                         & (df["ESTADO"].str.upper() != ESTADO_ANULADA)]
            if not previas.empty:
                return None, (f"La requisición {req} ya tiene la orden {previas.iloc[0]['ORDEN']}. "
                              "No se permite emitir otra para la misma requisición.")

        prefijo = PREFIJO_OS if es_servicio else PREFIJO_OC
        id_orden = f"{prefijo}{siguiente_consecutivo(df, prefijo)}"
        nit = datos_proveedor(df_prov, proveedor)["Nit"]
        hoy = date.today().isoformat()

        filas = [{
            "ORDEN": id_orden, "FECHA": hoy, "PROVEEDOR": proveedor, "NIT": nit,
            "REQUISICIO": req if req != SIN_RQ else "MANUAL",
            "CODIGO": it["CODIGO"].strip(), "DESCRIPCION": it["DESCRIPCION"].strip(),
            "REFERENCIA": it["REFERENCIA"].strip() or "NA", "CANT": it["CANT"],
            "UND": it["UND"].strip() or "Und", "IVA": fmt_pct(it["IVA"]),
            "V. UNIT": it["V. UNIT"], "V.TOTAL": round(it["V.TOTAL"], 2),
            "ESTADO": ESTADO_ELABORADA, "N. PEDIDO": n_pedido.strip(),
            "OBSERVACIONES": obs.strip(), "ELABORADO_POR": elaborado.strip(),
            "APROBADO_POR": aprobado.strip(), "FECHA_APROBACION": "", "MOTIVO_ANULACION": "",
        } for it in items]

        df = pd.concat([df, pd.DataFrame(filas)], ignore_index=True)
        error = guardar_datos(df, EXCEL_OC)
        return (None, error) if error else (id_orden, None)


def actualizar_orden(orden, nuevo_estado, extras=None, solo_si_estado=None):
    """Cambia el estado de una orden. Devuelve None si OK o el mensaje de error."""
    with obtener_lock():
        try:
            df = leer_directo(EXCEL_OC, COLS_OC)
        except Exception as e:
            return f"No se pudo leer la base de datos: {e}"
        mask = df["ORDEN"] == orden
        if not mask.any():
            return "La orden ya no existe."
        actual = df.loc[mask, "ESTADO"].iloc[0].upper()
        if solo_si_estado and actual != solo_si_estado:
            return f"La orden cambió de estado mientras la revisaba (ahora está {actual})."
        df.loc[mask, "ESTADO"] = nuevo_estado
        for campo, valor in (extras or {}).items():
            df.loc[mask, campo] = valor
        return guardar_datos(df, EXCEL_OC)


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


def flash(clave, mensaje, tipo="success"):
    st.session_state[f"_flash_{clave}"] = (tipo, mensaje)


def mostrar_flash(clave):
    dato = st.session_state.pop(f"_flash_{clave}", None)
    if dato:
        getattr(st, dato[0])(dato[1])


# =============================================================================
# DOCUMENTO IMPRIMIBLE
# =============================================================================
LOGOS_ARCHIVO = ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp")


@st.cache_data(show_spinner=False)
def _logo_desde_archivo(ruta, mtime):
    with open(ruta, "rb") as f:
        datos = f.read()
    ext = os.path.splitext(ruta)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "webp": "webp"}.get(ext, "png")
    return f"data:image/{mime};base64," + base64.b64encode(datos).decode()


def obtener_logo():
    """Usa logo.png (o .jpg) junto a la app; si no existe, usa LOGO_EMBEBIDO."""
    carpetas = []
    try:
        carpetas.append(os.path.dirname(os.path.abspath(__file__)))
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


def total_en_letras(valor):
    n = int(round(valor))
    if n >= 10 ** 12:
        return ""
    if n == 1:
        return "UN PESO M/CTE"
    texto = _apocope(numero_a_letras(n)) if n % 1000 else numero_a_letras(n)
    de = "DE " if n and n % 1_000_000 == 0 else ""
    return f"{texto} {de}PESOS M/CTE".upper()


CSS_ORDEN = """
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
.ord .tipo{font-size:9px;letter-spacing:1.5px;color:#777;font-weight:bold}
.ord .titulo{font-size:14px;font-weight:bold;color:#0b2a55;margin:2px 0}
.ord .num{font-size:21px;font-weight:bold;color:#000;margin:2px 0 6px}
.ord .fila{font-size:10.5px;color:#333;margin:3px 0}
.estado{display:inline-block;border:1.5px solid;border-radius:10px;padding:1px 10px;font-weight:bold;font-size:10px}
.ok{color:#1b7a3a}.bad{color:#c62828}.pend{color:#b26a00}
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
.marca{position:absolute;top:36%;left:10%;font-size:120px;color:rgba(198,40,40,.16);
 transform:rotate(-25deg);font-weight:bold;pointer-events:none}
.btn{display:block;width:100%;background:#004080;color:#fff;padding:12px;border:0;border-radius:5px;
 font-weight:bold;font-size:14px;cursor:pointer;margin-bottom:10px}
@page{size:Letter;margin:0}
@media print{.no-print{display:none!important}body{padding:0}
 .doc{border:0;border-radius:0;padding:14mm}}
"""


def generar_html_orden(orden, df_orden, prov):
    d = con_calculos(df_orden)
    p = d.iloc[0]
    estado = str(p["ESTADO"]).strip().upper()
    titulo = "ORDEN DE SERVICIO" if orden.upper().startswith("OS") else "ORDEN DE COMPRA"
    clase_estado = {ESTADO_APROBADA: "ok", ESTADO_ANULADA: "bad"}.get(estado, "pend")
    fecha_aprob = fmt_fecha(p["FECHA_APROBACION"]) if estado == ESTADO_APROBADA else ""

    filas = []
    for n, (_, r) in enumerate(d.iterrows(), start=1):
        filas.append(
            f'<tr><td class="c">{n}</td><td class="c nw">{esc(r["CODIGO"])}</td>'
            f'<td class="l">{esc(r["DESCRIPCION"])}</td><td class="c">{esc(r["REFERENCIA"] or "NA")}</td>'
            f'<td class="c">{fmt_num(r["_cant"])}</td><td class="c">{esc(r["UND"] or "Und")}</td>'
            f'<td class="r nw">{fmt_cop(r["_unit"])}</td><td class="c">{fmt_pct(r["_ivap"])}</td>'
            f'<td class="r nw">{fmt_cop(r["_total"])}</td></tr>'
        )

    subtotal, iva, total = d["_base"].sum(), d["_ivav"].sum(), d["_total"].sum()
    letras = total_en_letras(total)
    bloque_letras = f'<div class="letras"><b>SON:</b> {esc(letras)}</div>' if letras else ""
    firma_aprob = esc(p["APROBADO_POR"]) if estado == ESTADO_APROBADA else ""
    sub_aprob = f"Aprobada el {fecha_aprob}" if fecha_aprob else ""
    marca = '<div class="marca">ANULADA</div>' if estado == ESTADO_ANULADA else ""
    logo_src = obtener_logo()
    logo = f'<img class="logo" src="{logo_src}" alt="" onerror="this.remove()">' if logo_src else ""
    obs = esc(p["OBSERVACIONES"] or OBS_DEFECTO)
    e = EMPRESA

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>{esc(orden)}</title><style>{CSS_ORDEN}</style></head><body>
<button class="btn no-print" onclick="window.print()">🖨️ Imprimir / Guardar como PDF</button>
<div class="doc">{marca}
<table class="cab"><tr>
<td style="width:58%"><div class="emp">{logo}<div>
<h1>{esc(e['nombre'])}</h1>
<p><b>Nit:</b> {esc(e['nit'])} · Régimen {esc(e['regimen'])}</p>
<p>{esc(e['direccion'])}</p>
<p>Tel. {esc(e['telefono'])} · {esc(e['correo'])}</p>
</div></div></td>
<td style="width:42%"><div class="ord">
<div class="tipo">ORIGINAL</div>
<div class="titulo">{titulo}</div>
<div class="num">{esc(orden)}</div>
<div class="fila"><b>Fecha de creación:</b> {esc(fmt_fecha(p['FECHA']))}</div>
<div class="fila"><span class="estado {clase_estado}">{esc(estado)}</span></div>
</div></td></tr></table>
<div class="sep"></div>
<table class="info">
<tr><td class="k">Señores</td><td style="width:42%">{esc(p['PROVEEDOR'])}</td>
<td class="k">Requisición</td><td>{esc(p['REQUISICIO'])}</td></tr>
<tr><td class="k">Nit / Cédula</td><td>{esc(p['NIT'])}</td>
<td class="k">N. Pedido</td><td>{esc(p['N. PEDIDO'])}</td></tr>
<tr><td class="k">Dirección</td><td>{esc(prov['Direccion'])}</td>
<td class="k">Forma de pago</td><td>{esc(prov['Condicion de Pago'])}</td></tr>
<tr><td class="k">Teléfono</td><td>{esc(prov['Telefono / Celular'])}</td>
<td class="k">Correo</td><td>{esc(prov['Correo Electronico'])}</td></tr>
</table>
<table class="items"><thead><tr>
<th style="width:5%">Ítem</th><th style="width:11%">Código</th><th class="l">Descripción</th>
<th style="width:8%">Ref</th><th style="width:7%">Cant.</th><th style="width:6%">Und.</th>
<th class="r" style="width:12%">Vr. Unitario</th><th style="width:6%">IVA</th>
<th class="r" style="width:13%">Vr. Total</th>
</tr></thead><tbody>{''.join(filas)}</tbody></table>
<table class="res"><tr>
<td style="width:58%"><div class="obs"><b>Observaciones / Términos:</b><br>
<div style="margin-top:4px;color:#333">{obs}</div></div></td>
<td style="width:2%"></td>
<td style="width:40%"><table class="tot">
<tr><td><b>Subtotal</b></td><td class="r">{fmt_cop(subtotal)}</td></tr>
<tr><td><b>IVA</b></td><td class="r">{fmt_cop(iva)}</td></tr>
<tr class="final"><td>VALOR TOTAL</td><td class="r">{fmt_cop(total)}</td></tr>
</table></td></tr></table>
{bloque_letras}
<table class="firmas"><tr>
<td><div class="esp"></div><div class="nom">{esc(p['ELABORADO_POR'])}</div>
<div class="lin">Elaborado por</div><div class="sub"></div></td>
<td><div class="esp"></div><div class="nom">{firma_aprob}</div>
<div class="lin">Aprobado / Gerencia</div><div class="sub">{sub_aprob}</div></td>
<td><div class="esp"></div><div class="nom">&nbsp;</div>
<div class="lin">Recibido Proveedor (Firma y Sello)</div><div class="sub">Nombre, C.C. y fecha</div></td>
</tr></table>
</div></body></html>"""


# =============================================================================
# PESTAÑA 1: EMITIR
# =============================================================================
def nuevo_item(cod="", desc="", ref="NA", cant=1.0, und="Und", iva=IVA_DEFECTO, unit=0.0):
    return {"_id": uuid.uuid4().hex[:8], "CODIGO": cod, "DESCRIPCION": desc, "REFERENCIA": ref,
            "CANT": cant, "UND": und, "IVA": iva, "V. UNIT": unit, "V.TOTAL": 0.0}


def render_item(idx, item, ver):
    def k(campo):
        return f"ord_{campo}_{ver}_{item['_id']}"

    st.markdown(f"**Ítem #{idx + 1}**")
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.5, 2.5, 1, 0.8, 0.8, 1.2, 1, 0.5])
    with c1:
        cod = st.text_input(f"Código #{idx + 1}", value=item["CODIGO"], key=k("cod"))
    with c2:
        desc = st.text_input(f"Descripción #{idx + 1}", value=item["DESCRIPCION"], key=k("desc"))
    with c3:
        ref = st.text_input(f"Referencia #{idx + 1}", value=item["REFERENCIA"], key=k("ref"))
    with c4:
        cant = st.number_input(f"Cant #{idx + 1}", min_value=0.01, value=max(float(item["CANT"]), 0.01),
                               step=1.0, key=k("cant"))
    with c5:
        und = st.text_input(f"Und #{idx + 1}", value=item["UND"], key=k("und"))
    with c6:
        unit = st.number_input(f"V. Unit ($) #{idx + 1}", min_value=0.0, value=float(item["V. UNIT"]),
                               step=1000.0, key=k("unit"))
    with c7:
        iva_actual = float(item["IVA"])
        iva_idx = IVA_OPCIONES.index(iva_actual) if iva_actual in IVA_OPCIONES else IVA_OPCIONES.index(IVA_DEFECTO)
        iva = st.selectbox(f"IVA #{idx + 1}", IVA_OPCIONES, index=iva_idx, format_func=fmt_pct, key=k("iva"))
    with c8:
        st.write("")
        eliminar = st.button("🗑️", key=k("del"), help="Quitar este ítem")

    base = cant * unit
    iva_valor = base * iva
    actualizado = {"_id": item["_id"], "CODIGO": cod, "DESCRIPCION": desc, "REFERENCIA": ref, "CANT": cant,
                   "UND": und, "IVA": iva, "V. UNIT": unit, "V.TOTAL": base + iva_valor}
    return actualizado, base, iva_valor, eliminar


def tab_emitir():
    st.subheader("✍️ Formulario de Emisión de Orden")
    mostrar_flash("emision")

    df_oc = cargar_datos(EXCEL_OC, COLS_OC)
    df_prov = cargar_datos(EXCEL_PROVEEDORES, COLS_PROV)
    df_req = cargar_datos(EXCEL_REQUISICIONES, COLS_REQ)

    ss = st.session_state
    ss.setdefault("items_orden_temp", [])
    ss.setdefault("ultima_req_sel", "")
    ss.setdefault("oc_ver", 0)
    ss.setdefault("oc_omitidos", 0)

    col_rq, col_tipo = st.columns([2, 1])
    with col_tipo:
        tipo_orden = st.selectbox("Tipo de Orden", ["OS (Orden de Servicios)", "OC (Orden de Compra)"], key="oc_tipo")
    es_servicio = tipo_orden.startswith("OS")
    if es_servicio:
        st.caption("ℹ️ Las Órdenes de Servicio (OS) solo admiten códigos que empiecen por **SER** (ej. SER01001).")

    opciones_req = [SIN_RQ] + requisiciones_disponibles(df_req, df_oc, es_servicio)
    if ss.get("oc_req_sel", SIN_RQ) not in opciones_req:   # p. ej. la RQ ya quedó con orden
        ss["oc_req_sel"] = SIN_RQ
    with col_rq:
        req_sel = st.selectbox("📂 Cargar datos desde Requisición (RQ)", opciones_req, key="oc_req_sel",
                               help="Solo se listan requisiciones del tipo elegido que aún no tienen orden activa.")

    # Al cambiar de RQ o de tipo se recargan los ítems desde la requisición
    firma_sel = req_sel if req_sel == SIN_RQ else f"{req_sel}|{tipo_orden}"
    pedido_sugerido = "Pendiente"
    items_rq = pd.DataFrame()
    if req_sel != SIN_RQ:
        items_rq = df_req[df_req["Requisicion"].str.lower() == req_sel.lower()]
        if not items_rq.empty:
            pedido_sugerido = items_rq.iloc[0]["Orden De Pedido"] or "Pendiente"

    if firma_sel != ss.ultima_req_sel:
        ss.ultima_req_sel = firma_sel
        ss.items_orden_temp = []
        ss.oc_ver += 1
        ss.oc_omitidos = 0
        for key in [k for k in ss.keys() if k.startswith("ord_")]:
            del ss[key]
        for _, r in items_rq.iterrows():
            cod = r["Cod Material"]
            if es_servicio and not es_codigo_ser(cod):
                ss.oc_omitidos += 1
                continue
            ss.items_orden_temp.append(nuevo_item(cod, r["Descripcion"], r["Ref"] or "NA",
                                                  parse_cant(r["Cant."]), r["Und."] or "Und"))

    if ss.oc_omitidos > 0:
        st.warning(f"⚠️ Se omitieron {ss.oc_omitidos} ítem(s) de la RQ que no empiezan por SER, "
                   "ya que seleccionó Orden de Servicio (OS).")

    ver = ss.oc_ver
    col_fec, col_prov, col_est = st.columns([1, 2, 1])
    with col_fec:
        st.text_input("Fecha de Emisión", value=str(date.today()), disabled=True)
    with col_prov:
        nombres = sorted({n for n in df_prov["Razon Social /Nombre"] if n}) if not df_prov.empty else []
        proveedor = st.selectbox("Proveedor", [SIN_PROV] + nombres, key=f"oc_prov_{ver}")
    with col_est:
        st.selectbox("Estado Inicial", [ESTADO_ELABORADA], disabled=True, key=f"oc_est_{ver}")

    col_ped, _ = st.columns([2, 1])
    with col_ped:
        n_pedido = st.text_input("N. Pedido / Referencia SAP", value=pedido_sugerido, key=f"oc_ped_{ver}")

    st.markdown("---")
    st.markdown("### 📝 Observaciones y Firmas de Autorización")
    col_obs1, col_obs2 = st.columns(2)
    with col_obs1:
        observaciones = st.text_area("Observaciones / Términos", value=OBS_DEFECTO, key=f"input_obs_{ver}",
                                     help="Notas, términos o condiciones especiales para el proveedor.")
    with col_obs2:
        elaborado_por = st.text_input("Elaborado por", value=ss.get("username", "Juan Galeano"),
                                      key=f"input_elab_{ver}")
        aprobado_por = st.text_input("Aprobado / Gerencia (Nombre)", value="Gerencia Logística",
                                     key=f"input_aprob_por_{ver}")
    st.markdown("---")

    st.markdown("### 📋 Detalle de los Ítems de la Orden e Impuestos")
    if st.button("➕ Agregar Nuevo Ítem Manual", key=f"btn_add_item_{ver}"):
        ss.items_orden_temp.append(nuevo_item())
        st.rerun()

    subtotal = iva_total = 0.0
    actualizados, hubo_eliminado = [], False
    for idx, item in enumerate(ss.items_orden_temp):
        nuevo, base, iva_valor, eliminar = render_item(idx, item, ver)
        st.markdown("---")
        if eliminar:
            hubo_eliminado = True
            continue
        actualizados.append(nuevo)
        subtotal += base
        iva_total += iva_valor
    ss.items_orden_temp = actualizados
    if hubo_eliminado:
        st.rerun()

    m1, m2, m3 = st.columns(3)
    m1.metric("Subtotal", fmt_cop(subtotal))
    m2.metric("IVA total", fmt_cop(iva_total))
    m3.metric("VALOR TOTAL", fmt_cop(subtotal + iva_total))

    if st.button("💾 Guardar y Emitir Orden", type="primary", use_container_width=True, key="btn_emitir"):
        errores = validar_orden(proveedor, ss.items_orden_temp, es_servicio)
        if errores:
            for e in errores:
                st.error(f"❌ {e}")
            return
        id_orden, error = registrar_orden(es_servicio, req_sel, proveedor, ss.items_orden_temp,
                                          n_pedido, observaciones, elaborado_por, aprobado_por)
        if error:
            st.error(f"❌ {error}")
            return
        flash("emision", f"✅ ¡Orden **{id_orden}** guardada con éxito en estado **{ESTADO_ELABORADA}** "
                         "(Pendiente de Firma)!")
        ss.items_orden_temp = []
        ss.oc_ver += 1
        st.rerun()


# =============================================================================
# PESTAÑA 2: CONSULTAR / IMPRIMIR
# =============================================================================
def tab_consultar():
    st.subheader("🖨️ Consultar, Imprimir y Guardar PDF")
    df_oc = cargar_datos(EXCEL_OC, COLS_OC)
    if df_oc.empty:
        st.info("No hay órdenes de compra registradas para consultar o imprimir.")
        return

    lista = ordenar_recientes(df_oc)["ORDEN"].unique().tolist()
    orden = st.selectbox("Seleccione la Orden a Consultar e Imprimir", lista, key="sel_imprimir_orden")
    df_sel = df_oc[df_oc["ORDEN"] == orden]
    if df_sel.empty:
        return

    prov = datos_proveedor(cargar_datos(EXCEL_PROVEEDORES, COLS_PROV), df_sel.iloc[0]["PROVEEDOR"])
    html = generar_html_orden(orden, df_sel, prov)
    components.html(html, height=1200, scrolling=True)
    st.download_button("⬇️ Descargar documento (abrir y guardar como PDF)", data=html.encode("utf-8"),
                       file_name=f"{orden}.html", mime="text/html", use_container_width=True)


# =============================================================================
# PESTAÑA 3: TODAS LAS ÓRDENES
# =============================================================================
def tab_todas():
    st.subheader("📋 Ver Todas las Órdenes Registradas")
    df_oc = cargar_datos(EXCEL_OC, COLS_OC)
    if df_oc.empty:
        st.info("No hay órdenes registradas todavía.")
        return

    df = ordenar_recientes(df_oc)
    c1, c2 = st.columns([2, 1])
    with c1:
        estados = st.multiselect("Estado", [ESTADO_ELABORADA, ESTADO_APROBADA, ESTADO_ANULADA],
                                 default=[ESTADO_ELABORADA, ESTADO_APROBADA], key="todas_estados")
    with c2:
        ver_detalle = st.toggle("Ver detalle por ítem", value=False, key="todas_detalle")
    df = df[df["ESTADO"].str.upper().isin(estados)]

    if ver_detalle:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Descargar detalle (Excel)", a_excel_bytes(df), "ordenes_detalle.xlsx")
        return

    d = con_calculos(df)
    resumen = (d.groupby("ORDEN", sort=False)
                .agg(FECHA=("FECHA", "first"), PROVEEDOR=("PROVEEDOR", "first"),
                     REQUISICION=("REQUISICIO", "first"), ESTADO=("ESTADO", "first"),
                     ITEMS=("CODIGO", "count"), SUBTOTAL=("_base", "sum"),
                     IVA=("_ivav", "sum"), TOTAL=("_total", "sum"))
                .reset_index())
    moneda = st.column_config.NumberColumn(format="$%.0f")
    st.dataframe(resumen, use_container_width=True, hide_index=True,
                 column_config={"SUBTOTAL": moneda, "IVA": moneda, "TOTAL": moneda})
    st.caption(f"{len(resumen)} orden(es) · Total listado: {fmt_cop(resumen['TOTAL'].sum())}")
    st.download_button("⬇️ Descargar resumen (Excel)", a_excel_bytes(resumen), "ordenes_resumen.xlsx")


# =============================================================================
# PESTAÑA 4: BUSCAR, APROBAR Y ANULAR
# =============================================================================
def tab_admin():
    st.subheader("🔍 Búsqueda, Revisión y Aprobación de Órdenes")
    mostrar_flash("admin")

    df_oc = cargar_datos(EXCEL_OC, COLS_OC)
    if df_oc.empty:
        st.info("No hay órdenes registradas para administrar.")
        return

    filtro = st.radio("Estado", [ESTADO_ELABORADA, ESTADO_APROBADA, ESTADO_ANULADA, "Todas"],
                      horizontal=True, key="adm_estado",
                      help="ELABORADA = pendientes por firma de gerencia.")
    df = df_oc if filtro == "Todas" else df_oc[df_oc["ESTADO"].str.upper() == filtro]

    texto = st.text_input("🔎 Buscar por N° de Orden, Proveedor, Requisición o N. Pedido", "").strip().lower()
    if texto:
        mask = pd.Series(False, index=df.index)
        for col in ("ORDEN", "PROVEEDOR", "REQUISICIO", "N. PEDIDO"):
            mask |= df[col].str.lower().str.contains(texto, regex=False, na=False)
        df = df[mask]

    lista = ordenar_recientes(df)["ORDEN"].unique().tolist() if not df.empty else []
    if not lista:
        st.warning("⚠️ No se encontraron órdenes con los filtros seleccionados.")
        return

    orden = st.selectbox("Seleccione la Orden a Revisar", lista, key="sel_admin_orden")
    df_sel = df_oc[df_oc["ORDEN"] == orden]
    if df_sel.empty:
        return
    p = df_sel.iloc[0]
    estado = p["ESTADO"].upper()

    st.markdown("---")
    st.markdown(f"### 📄 Detalle de la Orden: **{orden}**")
    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown(f"**Proveedor:** {p['PROVEEDOR']}")
        st.markdown(f"**NIT:** {p['NIT']}")
    with i2:
        st.markdown(f"**Requisición:** {p['REQUISICIO']}")
        st.markdown(f"**N. Pedido:** {p['N. PEDIDO']}")
    with i3:
        st.markdown(f"**Estado Actual:** `{estado}`")
        st.markdown(f"**Observaciones:** {p['OBSERVACIONES']}")
        if estado == ESTADO_ANULADA and p["MOTIVO_ANULACION"]:
            st.markdown(f"**Motivo de anulación:** {p['MOTIVO_ANULACION']}")

    d = con_calculos(df_sel)
    st.markdown("#### 📦 Ítems y Precios")
    tabla = pd.DataFrame({
        "Código": d["CODIGO"], "Descripción": d["DESCRIPCION"], "Ref": d["REFERENCIA"],
        "Cant": d["_cant"].map(fmt_num), "Und": d["UND"], "V. Unitario": d["_unit"].map(fmt_cop),
        "IVA": d["_ivap"].map(fmt_pct), "Total Ítem": d["_total"].map(fmt_cop),
    })
    st.dataframe(tabla, use_container_width=True, hide_index=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Subtotal", fmt_cop(d["_base"].sum()))
    m2.metric("IVA total", fmt_cop(d["_ivav"].sum()))
    m3.metric("VALOR TOTAL GENERAL", fmt_cop(d["_total"].sum()))
    st.markdown("---")

    col_aprobar, col_anular = st.columns(2)

    with col_aprobar:
        if estado == ESTADO_ELABORADA:
            with st.form(f"form_aprobar_{orden}"):
                st.markdown("### ✍️ Firma y Aprobación Gerencial")
                clave_ingresada = st.text_input("🔑 Contraseña de Gerencia", type="password")
                aprobar = st.form_submit_button("✅ Firmar y Aprobar Orden", type="primary")
            if aprobar:
                clave = clave_gerencia()
                if not clave:
                    st.error("❌ La contraseña de gerencia no está configurada. Defina GERENCIA_PASSWORD "
                             "en .streamlit/secrets.toml o como variable de entorno. Diagnóstico: " + diagnostico_clave())
                elif not hmac.compare_digest(clave_ingresada.strip().encode(), clave.encode()):
                    st.error("❌ Contraseña de gerencia incorrecta.")
                else:
                    error = actualizar_orden(orden, ESTADO_APROBADA,
                                             {"FECHA_APROBACION": date.today().isoformat()},
                                             solo_si_estado=ESTADO_ELABORADA)
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        flash("admin", f"🎉 ¡La orden **{orden}** ha sido APROBADA y firmada con éxito!")
                        st.rerun()
        elif estado == ESTADO_APROBADA:
            st.info(f"ℹ️ Esta orden ya se encuentra **APROBADA** y firmada"
                    f"{' el ' + fmt_fecha(p['FECHA_APROBACION']) if p['FECHA_APROBACION'] else ''}.")
        else:
            st.warning("⚠️ Esta orden está **ANULADA** y no se puede aprobar.")

    with col_anular:
        if estado != ESTADO_ANULADA:
            with st.form(f"form_anular_{orden}"):
                st.markdown("### ⚠️ Zona de Peligro")
                motivo = st.text_input("Motivo de la anulación")
                confirmar = st.checkbox(f"Confirmo que deseo anular la orden {orden}")
                anular = st.form_submit_button("🚫 Anular Orden")
            if anular:
                if not confirmar:
                    st.warning("⚠️ Debe marcar la casilla de confirmación para anular la orden.")
                elif not motivo.strip():
                    st.warning("⚠️ Indique el motivo de la anulación.")
                else:
                    error = actualizar_orden(orden, ESTADO_ANULADA, {"MOTIVO_ANULACION": motivo.strip()})
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        flash("admin", f"🚫 La orden **{orden}** fue ANULADA. La requisición queda libre "
                                       "para emitir una nueva orden.")
                        st.rerun()


# =============================================================================
# PÁGINA
# =============================================================================
st.title("📦 Órdenes de Compra y/o Servicios Multi-Ítem")
st.markdown("Generación integrada desde Requisiciones con múltiples materiales, cálculo de IVA y formato PDF.")

t1, t2, t3, t4 = st.tabs([
    "➕ Emitir Nueva Orden",
    "🖨️ Consultar, Imprimir y Guardar PDF",
    "📋 Ver Todas las Órdenes",
    "🔍 Buscar, Aprobar y Anular",
])
with t1:
    tab_emitir()
with t2:
    tab_consultar()
with t3:
    tab_todas()
with t4:
    tab_admin()
