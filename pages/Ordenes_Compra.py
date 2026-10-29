import streamlit as st
import pandas as pd
import os
import re
import base64
from html import escape as esc
from datetime import date

# ---------------- LOGO INCRUSTADO (no editar esta línea) ----------------
LOGO_EMBEBIDO = "data:image/png;base64,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"

st.set_page_config(page_title="Órdenes de Compra y Servicios", page_icon="📦", layout="wide")

EXCEL_OC = "base_ordenes_compra.xlsx"
EXCEL_PROVEEDORES = "base_proveedores.xlsx"
EXCEL_REQUISICIONES = "base_requisiciones.xlsx"
EXCEL_CENTROS_COSTOS = "base_centros_costos.xlsx"
EXCEL_MATERIALES = "base_materiales.xlsx"

def cargar_datos(archivo, columnas_default):
    if os.path.exists(archivo):
        df = pd.read_excel(archivo, dtype=str)
        df = df.fillna("")
        for col in columnas_default:
            if col not in df.columns:
                df[col] = ""
        for col in columnas_default:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(["nan", "NaN", "None", "<NA>"], "")
        return df[columnas_default]
    else:
        return pd.DataFrame(columns=columnas_default)

def guardar_datos(df, archivo):
    df.to_excel(archivo, index=False)

COLS_OC = [
    "ORDEN", "FECHA", "PROVEEDOR", "NIT", "REQUISICIO", 
    "CODIGO", "DESCRIPCION", "REFERENCIA", "CANT", "UND", 
    "IVA", "V. UNIT", "V.TOTAL", "ESTADO", "N. PEDIDO"
]

# Prefijos FIJOS de numeración (igual que en el Excel): OC-202604NN y OS-202605NN
PREFIJO_OC = "OC-202604"
PREFIJO_OS = "OS-202605"

def siguiente_consecutivo(df, prefijo):
    """Busca en TODA la tabla el mayor número de las órdenes que empiezan por el
    prefijo y devuelve el siguiente. Ignora sufijos no numéricos (ej. OC-20260427A)."""
    ultimo = 0
    if not df.empty and "ORDEN" in df.columns:
        for orden in df["ORDEN"].astype(str).str.strip().unique():
            if orden.startswith(prefijo):
                sufijo = orden[len(prefijo):]
                if sufijo.isdigit():
                    ultimo = max(ultimo, int(sufijo))
    if ultimo == 0:
        ultimo = 99          # si no hay ninguna previa, arranca en 100 (como en Excel)
    return ultimo + 1

# ---------------- DATOS DE LA EMPRESA (encabezado del PDF) ----------------
EMPRESA = {
    "nombre": "Asuserviciosss SAS",
    "nit": "901224239-3",
    "direccion": "CL 67 22 62 CA 14 BRR PARNASO",
    "telefono": "3186565776",
    "correo": "asuserviciosss@hotmail.com",
    "regimen": "COMUN",
}
# Si junto a este archivo (o en la carpeta desde donde se ejecuta) hay una imagen cuyo nombre
# empiece por "logo" (logo.png, logo_asuservicios.png, Logo Empresa.jpg...), se usa esa.
# Si no hay ninguna, se usa el logo incrustado más abajo (LOGO_EMBEBIDO), así SIEMPRE sale el logo.
def cargar_logo():
    tipos = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}
    carpetas = []
    try:
        carpetas.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    carpetas.append(os.getcwd())
    for carpeta in carpetas:
        try:
            nombres = sorted(os.listdir(carpeta))
        except OSError:
            continue
        for nombre in nombres:
            base, ext = os.path.splitext(nombre)
            if base.lower().startswith("logo") and ext.lower() in tipos:
                with open(os.path.join(carpeta, nombre), "rb") as fh:
                    return f"data:{tipos[ext.lower()]};base64," + base64.b64encode(fh.read()).decode()
    return LOGO_EMBEBIDO

def parse_valor(x, defecto=0.0):
    """Convierte '$3,000.00', '1600000', '1.600.000' o '1.600.000,50' en número."""
    t = str(x).strip().replace("$", "").replace(" ", "")
    if t in ("", "nan", "None"):
        return defecto
    if "." in t and "," in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")      # 1.600.000,50
        else:
            t = t.replace(",", "")                        # 1,600,000.50
    elif "," in t:
        t = t.replace(",", "") if re.fullmatch(r"\d{1,3}(,\d{3})+", t) else t.replace(",", ".")
    elif "." in t and re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")                            # 1.600.000
    try:
        return float(t)
    except ValueError:
        return defecto

def parse_cant(x, defecto=1.0):
    try:
        return float(str(x).strip().replace(",", "."))
    except ValueError:
        return defecto

def parse_iva(x, defecto=0.19):
    """0.19, '19' o '19%' -> 0.19"""
    try:
        v = float(str(x).strip().replace("%", "").replace(",", "."))
    except ValueError:
        return defecto
    return v / 100 if v > 1 else v

def fmt_cop(v):
    """Pesos colombianos: $1.600.000 (con coma decimal solo si hay centavos)."""
    t = f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if t.endswith(",00"):
        t = t[:-3]
    return f"${t}"

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

def es_codigo_ser(codigo):
    """True si el código es de servicio (empieza por SER)."""
    return str(codigo).strip().upper().startswith("SER")

df_oc = cargar_datos(EXCEL_OC, COLS_OC)
df_prov = cargar_datos(EXCEL_PROVEEDORES, ["Nit", "Razon Social /Nombre", "Contacto", "Telefono / Celular", "Correo Electronico", "Direccion", "Ciudad", "Condicion de Pago", "Fecha registro"])
df_req = cargar_datos(EXCEL_REQUISICIONES, ["Requisicion", "Cec", "Cod Material", "Descripcion", "Cant.", "Und.", "Solicitante", "Ref"])
df_cc = cargar_datos(EXCEL_CENTROS_COSTOS, ["CECO", "Cliente / Proyecto", "Area_Departamento"])
df_mat = cargar_datos(EXCEL_MATERIALES, ["Familia", "Código", "Descripción", "Referencia", "Unidad"])

st.title("📦 Órdenes de Compra y/o Servicios Multi-Ítem")
st.markdown("Generación integrada desde Requisiciones con múltiples materiales, cálculo de IVA y formato PDF.")

pestana1, pestana2, pestana3 = st.tabs(["➕ Emitir Nueva Orden", "🖨️ Consultar, Imprimir y Guardar PDF", "📋 Ver Todas las Órdenes"])

with pestana1:
    st.subheader("✍️ Formulario de Emisión de Orden")
    
    opciones_req = ["-- Ninguna (Ingreso Manual) --"]
    if not df_req.empty and "Requisicion" in df_req.columns:
        opciones_req += list(df_req["Requisicion"].unique())
        
    col_rq, col_tipo = st.columns([2, 1])
    with col_rq:
        req_seleccionada = st.selectbox("📂 Cargar datos desde Requisición (RQ)", opciones_req)
    with col_tipo:
        tipo_orden = st.selectbox("Tipo de Orden", ["OS (Orden de Servicios)", "OC (Orden de Compra)"], key="oc_tipo")

    es_servicio = tipo_orden.startswith("OS")
    if es_servicio:
        st.caption("ℹ️ Las Órdenes de Servicio (OS) solo admiten códigos que empiecen por **SER** (ej. SER01001).")
    
    if "items_orden_temp" not in st.session_state:
        st.session_state.items_orden_temp = []

    if "ultima_req_sel" not in st.session_state:
        st.session_state.ultima_req_sel = ""

    # Versión de los campos de ítems: cada vez que cambia la RQ (o se guarda una orden)
    # se sube, para que Streamlit cree campos NUEVOS y no reutilice los viejos.
    if "oc_ver" not in st.session_state:
        st.session_state.oc_ver = 0

    # Detección de cambio en la RQ seleccionada
    if req_seleccionada == "-- Ninguna (Ingreso Manual) --":
        firma_sel = req_seleccionada                       # ingreso manual: no se borra al cambiar el tipo
    else:
        firma_sel = f"{req_seleccionada}|{tipo_orden}"     # RQ: se recarga al cambiar RQ o tipo

    if firma_sel != st.session_state.ultima_req_sel:
        st.session_state.ultima_req_sel = firma_sel
        st.session_state.items_orden_temp = []
        st.session_state.oc_ver += 1
        st.session_state.oc_omitidos = 0
        
        # Limpiar llaves anteriores del session_state para evitar conflictos visuales
        keys_a_borrar = [k for k in st.session_state.keys() if k.startswith("ord_")]
        for k in keys_a_borrar:
            del st.session_state[k]

        if req_seleccionada != "-- Ninguna (Ingreso Manual) --" and not df_req.empty:
            match_reqs = df_req[df_req["Requisicion"].str.lower() == req_seleccionada.lower()]
            
            for _, r_item in match_reqs.iterrows():
                cod_mat = str(r_item.get("Cod Material", "")).strip()
                desc_mat = str(r_item.get("Descripcion", "")).strip()
                ref_val = str(r_item.get("Ref", "NA")).strip()
                
                # Omitir filas vacías o donde el código sea exactamente el nombre de la cabecera
                if not cod_mat or cod_mat.lower() in ["nan", "none", "", "cod material"]:
                    continue

                # Orden de Servicio: solo códigos SER
                if es_servicio and not cod_mat.upper().startswith("SER"):
                    st.session_state.oc_omitidos += 1
                    continue

                if not ref_val or ref_val.lower() in ["nan", "none", "", "n.a", "ref"]:
                    if not df_mat.empty:
                        m_mat = df_mat[df_mat["Código"].str.lower() == cod_mat.lower()]
                        if not m_mat.empty:
                            ref_val = str(m_mat.iloc[0].get("Referencia", "NA"))
                    if not ref_val:
                        ref_val = "NA"
                
                try:
                    cant_val = float(r_item.get("Cant.", 1.0))
                except:
                    cant_val = 1.0

                st.session_state.items_orden_temp.append({
                    "CODIGO": cod_mat,
                    "DESCRIPCION": desc_mat,
                    "REFERENCIA": ref_val,
                    "CANT": cant_val,
                    "UND": str(r_item.get("Und.", "Und")).strip() or "Und",
                    "V. UNIT": 0.0,
                    "IVA": 0.19
                })

    if es_servicio and st.session_state.get("oc_omitidos", 0) > 0:
        st.warning(
            f"Se omitieron {st.session_state.oc_omitidos} ítem(s) de la requisición porque su código no empieza por SER. "
            "Una Orden de Servicio solo admite códigos SER. Para esos ítems emita una Orden de Compra (OC)."
        )

    if len(st.session_state.items_orden_temp) == 0:
        st.session_state.items_orden_temp.append({
            "CODIGO": "",
            "DESCRIPCION": "",
            "REFERENCIA": "NA",
            "CANT": 1.0,
            "UND": "Und",
            "V. UNIT": 0.0,
            "IVA": 0.19
        })

    # CONTROL: una Orden de Compra (OC) NO puede contener códigos SER (servicios)
    codigos_ser_en_oc = []
    if not es_servicio:
        codigos_ser_en_oc = [str(it["CODIGO"]).strip() for it in st.session_state.items_orden_temp
                             if es_codigo_ser(it["CODIGO"])]

    if codigos_ser_en_oc:
        st.error(
            f"⛔ La requisición {req_seleccionada} contiene códigos de servicio (SER): "
            f"{', '.join(codigos_ser_en_oc)}. "
            "Una Orden de Compra (OC) no puede incluir códigos SER, por eso no es posible iniciar ni continuar. "
            "Cambie el tipo a «OS (Orden de Servicios)» o seleccione otra requisición."
        )
    else:
        with st.form("form_emitir_oc"):
            c1, c2, c3 = st.columns(3)
            with c1:
                fecha_emision = date.today()
                st.text_input("Fecha de Emisión", value=str(fecha_emision), disabled=True)
            
            with c2:
                opciones_proveedores = ["-- Seleccione Proveedor --"]
                if not df_prov.empty:
                    opciones_proveedores += [f"{row['Nit']} - {row['Razon Social /Nombre']}" for _, row in df_prov.iterrows()]
                prov_sel = st.selectbox("Proveedor", opciones_proveedores)
            
            with c3:
                estado_orden = st.selectbox("Estado", ["APROBADA", "PENDIENTE", "ANULADA"])
                n_pedido_in = st.text_input("N. Pedido / Referencia SAP", value="Pendiente", placeholder="Ej: 4500158110 o Pendiente")

            st.markdown("---")
            st.markdown("#### 📋 Detalle de los Ítems de la Orden e Impuestos")
        
            nuevos_items_editados = []
            subtotal_general = 0.0
            iva_general = 0.0

            ver = st.session_state.oc_ver
            for idx, item in enumerate(st.session_state.items_orden_temp):
                st.markdown(f"**Ítem #{idx + 1}**")
                i1, i2, i3, i4, i5, i6, i7 = st.columns([2, 3, 2, 1, 1, 2, 2])
            
                with i1:
                    c_cod = st.text_input(f"Código #{idx+1}", value=item["CODIGO"], key=f"ord_cod_{ver}_{idx}")
                with i2:
                    c_desc = st.text_input(f"Descripción #{idx+1}", value=item["DESCRIPCION"], key=f"ord_desc_{ver}_{idx}")
                with i3:
                    c_ref = st.text_input(f"Referencia #{idx+1}", value=item["REFERENCIA"], key=f"ord_ref_{ver}_{idx}")
                with i4:
                    c_cant = st.number_input(f"Cant #{idx+1}", min_value=0.01, step=1.0, value=float(item["CANT"]), key=f"ord_cant_{ver}_{idx}")
                with i5:
                    c_und = st.text_input(f"Und #{idx+1}", value=item["UND"], key=f"ord_und_{ver}_{idx}")
                with i6:
                    c_vunit = st.number_input(f"V. Unit ($) #{idx+1}", min_value=0.0, step=1000.0, value=float(item["V. UNIT"]), key=f"ord_vunit_{ver}_{idx}")
                with i7:
                    c_iva = st.selectbox(f"IVA #{idx+1}", [0.0, 0.05, 0.19], index=2 if float(item["IVA"]) == 0.19 else (1 if float(item["IVA"]) == 0.05 else 0), key=f"ord_iva_{ver}_{idx}", format_func=lambda x: f"{int(x*100)}%")

                sub_item = c_cant * c_vunit
                iva_item = sub_item * c_iva
                subtotal_general += sub_item
                iva_general += iva_item

                nuevos_items_editados.append({
                    "CODIGO": c_cod,
                    "DESCRIPCION": c_desc,
                    "REFERENCIA": c_ref if c_ref else "NA",
                    "CANT": c_cant,
                    "UND": c_und,
                    "V. UNIT": c_vunit,
                    "IVA": c_iva
                })
                st.markdown("---")

            total_general = subtotal_general + iva_general
            st.markdown(f"**Subtotal Acumulado:** \\${subtotal_general:,.2f} | **IVA Total:** \\${iva_general:,.2f} | **V.TOTAL FINAL:** <span style='color: #27ae60; font-size: 20px;'>**\\${total_general:,.2f}**</span>", unsafe_allow_html=True)

            btn_guardar = st.form_submit_button("💾 Guardar y Emitir Orden Completa", type="primary")

            if btn_guardar:
                st.session_state.items_orden_temp = nuevos_items_editados

                if prov_sel == "-- Seleccione Proveedor --":
                    st.error("Por favor seleccione un Proveedor válido.")
                elif any(not str(it["CODIGO"]).strip() for it in st.session_state.items_orden_temp):
                    st.error("Todos los ítems deben tener un Código de Material especificado.")
                elif es_servicio and any(not str(it["CODIGO"]).strip().upper().startswith("SER") for it in st.session_state.items_orden_temp):
                    codigos_malos = [str(it["CODIGO"]).strip() for it in st.session_state.items_orden_temp
                                     if not str(it["CODIGO"]).strip().upper().startswith("SER")]
                    st.error(
                        "Una Orden de Servicio solo admite códigos SER (ej. SER01001). "
                        f"Códigos no válidos: {', '.join(codigos_malos)}. "
                        "Cámbielos por códigos SER o seleccione 'OC (Orden de Compra)'."
                    )
                elif (not es_servicio) and any(es_codigo_ser(it["CODIGO"]) for it in st.session_state.items_orden_temp):
                    codigos_ser = [str(it["CODIGO"]).strip() for it in st.session_state.items_orden_temp
                                   if es_codigo_ser(it["CODIGO"])]
                    st.error(
                        "⛔ Una Orden de Compra (OC) no admite códigos SER (servicios). "
                        f"Códigos no válidos: {', '.join(codigos_ser)}. "
                        "Cámbielos o seleccione 'OS (Orden de Servicios)'. La orden NO se guardó."
                    )
                else:
                    nit_puro = prov_sel.split(" - ")[0].strip()
                    nombre_prov = prov_sel.split(" - ")[1].strip() if " - " in prov_sel else prov_sel
                
                    prefijo_orden = PREFIJO_OS if tipo_orden.startswith("OS") else PREFIJO_OC
                    siguiente_num = siguiente_consecutivo(df_oc, prefijo_orden)
                    nro_orden_gen = f"{prefijo_orden}{siguiente_num:02d}"
                    req_asignada = req_seleccionada if req_seleccionada != "-- Ninguna (Ingreso Manual) --" else "MANUAL"

                    filas_nuevas_oc = []
                    for it in st.session_state.items_orden_temp:
                        sub_it = it["CANT"] * it["V. UNIT"]
                        tot_it = sub_it + (sub_it * it["IVA"])
                    
                        filas_nuevas_oc.append({
                            "ORDEN": str(nro_orden_gen),
                            "FECHA": fecha_emision.strftime("%d/%m/%Y"),
                            "PROVEEDOR": str(nombre_prov),
                            "NIT": str(nit_puro),
                            "REQUISICIO": str(req_asignada),
                            "CODIGO": str(it["CODIGO"]).strip(),
                            "DESCRIPCION": str(it["DESCRIPCION"]).strip(),
                            "REFERENCIA": str(it["REFERENCIA"]).strip() if str(it["REFERENCIA"]).strip() else "NA",
                            "CANT": str(it["CANT"]),
                            "UND": str(it["UND"]),
                            "IVA": str(it["IVA"]),
                            "V. UNIT": f"${it['V. UNIT']:,.2f}",
                            "V.TOTAL": f"${tot_it:,.2f}",
                            "ESTADO": str(estado_orden),
                            "N. PEDIDO": str(n_pedido_in)
                        })

                    df_nuevas = pd.DataFrame(filas_nuevas_oc)

                    if not df_oc.empty:
                        df_oc = pd.concat([df_nuevas, df_oc], ignore_index=True)
                    else:
                        df_oc = df_nuevas

                    guardar_datos(df_oc, EXCEL_OC)
                    st.session_state.items_orden_temp = []
                    st.session_state.oc_ver += 1
                    st.success(f"¡Orden **{nro_orden_gen}** con {len(filas_nuevas_oc)} ítems emitida con éxito y ubicada al inicio!")
                    st.balloons()
                    st.rerun()

with pestana2:
    st.subheader("🖨️ Visualizar, Imprimir y Guardar como PDF")

    if df_oc.empty:
        st.info("No hay órdenes emitidas todavía.")
    else:
        lista_ordenes = df_oc["ORDEN"].unique().tolist()
        orden_elegida = st.selectbox("Seleccione el Número de Orden a Imprimir", lista_ordenes)

        match_ordenes = df_oc[df_oc["ORDEN"] == orden_elegida]
        if not match_ordenes.empty:
            r_primero = match_ordenes.iloc[0]

            # ---- Datos del proveedor ----
            nit_p = str(r_primero.get("NIT", "")).strip()
            dir_prov = tel_prov = email_prov = ""
            cond_pago_prov = "Contado"
            if not df_prov.empty:
                mp = df_prov[df_prov["Nit"] == nit_p]
                if not mp.empty:
                    dir_prov = str(mp.iloc[0].get("Direccion", ""))
                    tel_prov = str(mp.iloc[0].get("Telefono / Celular", ""))
                    email_prov = str(mp.iloc[0].get("Correo Electronico", ""))
                    cond_pago_prov = str(mp.iloc[0].get("Condicion de Pago", "")) or "Contado"

            # ---- Filas de ítems y totales ----
            filas_tabla_html = ""
            subtotal_orden_calc = 0.0
            iva_orden_calc = 0.0

            for n_item, (_, it_row) in enumerate(match_ordenes.iterrows(), start=1):
                v_u = parse_valor(it_row.get("V. UNIT", 0))
                cant_u = parse_cant(it_row.get("CANT", 1))
                iva_u = parse_iva(it_row.get("IVA", 0.19))

                sub_i = cant_u * v_u
                subtotal_orden_calc += sub_i
                iva_orden_calc += sub_i * iva_u

                filas_tabla_html += f"""
                <tr>
                    <td class="c">{n_item}</td>
                    <td class="c">{esc(str(it_row.get('REQUISICIO', '')))}</td>
                    <td class="c">{esc(str(it_row.get('CODIGO', '')))}</td>
                    <td class="l">{esc(str(it_row.get('DESCRIPCION', '')))}</td>
                    <td class="c">{esc(str(it_row.get('REFERENCIA', '')))}</td>
                    <td class="c">{fmt_num(cant_u)}</td>
                    <td class="c">{esc(str(it_row.get('UND', '')))}</td>
                    <td class="c">{int(round(iva_u * 100))}%</td>
                    <td class="r">{fmt_cop(v_u)}</td>
                    <td class="r">{fmt_cop(sub_i)}</td>
                </tr>
                """

            total_orden_calc = subtotal_orden_calc + iva_orden_calc

            # ---- Encabezado ----
            nro_orden = str(r_primero.get("ORDEN", ""))
            titulo_doc = "ORDEN DE SERVICIO" if nro_orden.upper().startswith("OS") else "ORDEN DE COMPRA"
            estado_txt = str(r_primero.get("ESTADO", "")).strip().upper()
            color_estado = "#c00000" if estado_txt == "ANULADA" else "#1e7e34"
            marca_anulada = '<div class="marca">ANULADA</div>' if estado_txt == "ANULADA" else ""

            logo_uri = cargar_logo()
            if logo_uri:
                logo_html = f'<img class="logo" src="{logo_uri}" alt="{esc(EMPRESA["nombre"])}">'
            else:
                logo_html = f'<div class="logo-texto">{esc(EMPRESA["nombre"])}</div>'

            css = """
                @page { size: A4; margin: 10mm; }
                * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                body { font-family: Arial, Helvetica, sans-serif; font-size: 12px; color: #000; background: #fff; margin: 0; padding: 10px; }
                .container { position: relative; background: #fff; padding: 18px 22px; border: 1px solid #ddd; max-width: 900px; margin: auto; }
                table { width: 100%; border-collapse: collapse; }
                .cab td { border: none; vertical-align: top; padding: 0; }
                .empresa { width: 34%; line-height: 1.55; font-size: 11.5px; }
                .empresa .nombre { font-size: 17px; font-weight: bold; color: #1f4e78; margin-bottom: 1px; }
                .empresa .nit { font-size: 12px; font-weight: bold; color: #1f4e78; margin-bottom: 4px; }
                .centro { width: 33%; text-align: center; vertical-align: middle !important; }
                .logo { max-width: 100%; max-height: 82px; }
                .logo-texto { font-size: 20px; font-weight: bold; color: #1f4e78; }
                .orden { width: 33%; text-align: right; line-height: 1.6; }
                .orden .original { font-size: 20px; font-weight: bold; color: #9a9a9a; letter-spacing: 1px; }
                .orden .titulo { font-size: 13px; font-weight: bold; color: #1f4e78; }
                .orden .numero { font-size: 17px; font-weight: bold; color: #222; }
                .linea { border: none; border-top: 3px solid #1f4e78; margin: 10px 0 12px 0; }
                .caja td { border: 1px solid #cfd6de; padding: 6px 9px; vertical-align: top; background: #f7f9fb; line-height: 1.55; }
                .caja .tit { font-weight: bold; color: #1f4e78; }
                .items { margin-top: 12px; }
                .items th { background: #1f4e78; color: #fff; padding: 6px 4px; font-size: 11px; border: 1px solid #1f4e78; }
                .items td { padding: 6px 5px; border: 1px solid #d5dbe2; font-size: 11.5px; }
                .items thead { display: table-header-group; }
                .items tr { page-break-inside: avoid; }
                .c { text-align: center; } .l { text-align: left; } .r { text-align: right; white-space: nowrap; }
                .resumen { margin-top: 12px; }
                .resumen td { vertical-align: top; }
                .obs { border: 1px solid #d5dbe2; padding: 8px 10px; background: #fdfdfd; min-height: 70px; }
                .totales td { border: 1px solid #d5dbe2; padding: 6px 9px; }
                .totales .et { background: #f1f1f1; font-weight: bold; width: 45%; }
                .totales .tot td { background: #1f4e78; color: #fff; font-weight: bold; font-size: 13px; }
                .firmas { margin-top: 46px; }
                .firmas td { width: 33%; text-align: center; border: none; border-top: 1px solid #000; padding-top: 5px; font-size: 11.5px; }
                .pie { margin-top: 18px; text-align: center; font-size: 10px; color: #777; border-top: 1px solid #ddd; padding-top: 6px; }
                .marca { position: absolute; top: 38%; left: 12%; font-size: 120px; font-weight: bold; color: rgba(192,0,0,0.13); transform: rotate(-25deg); pointer-events: none; }
                .no-print { margin-top: 20px; text-align: center; }
                .btn-print { background-color: #1f4e78; color: white; border: none; padding: 12px 25px; font-size: 15px; font-weight: bold; cursor: pointer; border-radius: 5px; }
                .btn-print:hover { background-color: #16365c; }
                @media print {
                    .no-print { display: none; }
                    body { padding: 0; }
                    .container { border: none; padding: 0; max-width: none; }
                }
            """

            html_orden = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>{css}</style>
            </head>
            <body>
                <div class="container">
                    {marca_anulada}
                    <table class="cab">
                        <tr>
                            <td class="empresa">
                                <div class="nombre">{esc(EMPRESA['nombre'])}</div>
                                <div class="nit">Nit: {esc(EMPRESA['nit'])}</div>
                                {esc(EMPRESA['direccion'])}<br>
                                Tel. {esc(EMPRESA['telefono'])}<br>
                                Correo: {esc(EMPRESA['correo'])}<br>
                                Régimen: {esc(EMPRESA['regimen'])}
                            </td>
                            <td class="centro">{logo_html}</td>
                            <td class="orden">
                                <div class="original">ORIGINAL</div>
                                <div class="titulo">{titulo_doc}</div>
                                <div class="numero">{esc(nro_orden)}</div>
                                <div><b>Fecha de creación:</b> {fmt_fecha(r_primero.get('FECHA', ''))}</div>
                                <div><b>Estado:</b> <span style="color: {color_estado}; font-weight: bold;">{esc(estado_txt)}</span></div>
                                <div><b>N. Pedido:</b> {esc(str(r_primero.get('N. PEDIDO', '')))}</div>
                            </td>
                        </tr>
                    </table>

                    <hr class="linea">

                    <table class="caja">
                        <tr>
                            <td style="width: 55%;">
                                <span class="tit">Señores:</span> {esc(str(r_primero.get('PROVEEDOR', '')))}<br>
                                <span class="tit">Nit/Cédula:</span> {esc(nit_p)}<br>
                                <span class="tit">Dirección:</span> {esc(dir_prov)}<br>
                                <span class="tit">Tel:</span> {esc(tel_prov)}
                            </td>
                            <td style="width: 45%;">
                                <span class="tit">Correo:</span> {esc(email_prov)}<br>
                                <span class="tit">Forma de pago:</span> {esc(cond_pago_prov)}<br>
                                <span class="tit">Requisición:</span> {esc(str(r_primero.get('REQUISICIO', '')))}
                            </td>
                        </tr>
                    </table>

                    <table class="items">
                        <thead>
                            <tr>
                                <th style="width: 5%;">Ítem</th>
                                <th style="width: 10%;">Requisición</th>
                                <th style="width: 10%;">Cód. Material</th>
                                <th>Descripción</th>
                                <th style="width: 6%;">Ref</th>
                                <th style="width: 6%;">Cant.</th>
                                <th style="width: 6%;">Und.</th>
                                <th style="width: 5%;">IVA</th>
                                <th style="width: 11%;">Precio</th>
                                <th style="width: 12%;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_tabla_html}
                        </tbody>
                    </table>

                    <table class="resumen">
                        <tr>
                            <td style="width: 58%; padding-right: 12px;">
                                <div class="obs">
                                    <b>Observaciones / Términos:</b><br>
                                    Suministro autorizado bajo los términos contractuales vigentes.
                                </div>
                            </td>
                            <td style="width: 42%;">
                                <table class="totales">
                                    <tr><td class="et">Subtotal</td><td class="r">{fmt_cop(subtotal_orden_calc)}</td></tr>
                                    <tr><td class="et">IVA</td><td class="r">{fmt_cop(iva_orden_calc)}</td></tr>
                                    <tr class="tot"><td>VALOR TOTAL</td><td class="r">{fmt_cop(total_orden_calc)}</td></tr>
                                </table>
                            </td>
                        </tr>
                    </table>

                    <table class="firmas">
                        <tr>
                            <td>Elaborado por</td>
                            <td>Aprobado / Gerencia</td>
                            <td>Recibido Proveedor (Firma y Sello)</td>
                        </tr>
                    </table>

                    <div class="pie">
                        {esc(EMPRESA['nombre'])} · Nit {esc(EMPRESA['nit'])} · {esc(EMPRESA['direccion'])} · Tel. {esc(EMPRESA['telefono'])} · {esc(EMPRESA['correo'])}
                    </div>

                    <div class="no-print">
                        <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Guardar en PDF</button>
                    </div>
                </div>
            </body>
            </html>
            """

            st.components.v1.html(html_orden, height=1150, scrolling=True)

with pestana3:
    st.subheader("📋 Base de Datos General de Órdenes (Último registro de primero)")
    filtro_oc = st.text_input("🔍 Buscar orden (escribe Nro Orden, Proveedor, Nit, Estado...):", placeholder="Ej: OS-20260562, TRANSPORTES, APROBADA...")
    
    df_mostrar_oc = df_oc.copy()
    if filtro_oc.strip() != "":
        txt_b = filtro_oc.lower().strip()
        def cumple_filtro(row):
            for col in COLS_OC:
                if txt_b in str(row.get(col, "")).lower():
                    return True
            return False
        if not df_mostrar_oc.empty:
            df_mostrar_oc = df_mostrar_oc[df_mostrar_oc.apply(cumple_filtro, axis=1)]
            
    if not df_mostrar_oc.empty:
        st.markdown(f"**Total de registros encontrados:** {len(df_mostrar_oc)}")
        st.dataframe(df_mostrar_oc, use_container_width=True, hide_index=True)
    else:
        st.info("No se encontraron órdenes registradas o que coincidan con la búsqueda.")
