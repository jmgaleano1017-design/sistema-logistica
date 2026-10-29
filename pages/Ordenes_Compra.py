import streamlit as st

# Validación de seguridad: Si no ha iniciado sesión, bloquea el módulo
if not st.session_state.get("password_correct", False):
    st.error("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal (Inicio / Principal).")
    st.stop()

import pandas as pd
import os
import re
import base64
from html import escape as esc
from datetime import date

# ---------------- LOGO EMBEBIDO (no editar esta línea) ----------------
LOGO_EMBEBIDO = "data:image/png;base64,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"

EXCEL_OC = "Ordenes.xlsx"
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
    try:
        df.to_excel(archivo, index=False)
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar en el archivo: {e}")
        return False

COLS_OC = [
    "ORDEN", "FECHA", "PROVEEDOR", "NIT", "REQUISICIO", 
    "CODIGO", "DESCRIPCION", "REFERENCIA", "CANT", "UND", 
    "IVA", "V. UNIT", "V.TOTAL", "ESTADO", "N. PEDIDO",
    "OBSERVACIONES", "ELABORADO_POR", "APROBADO_POR"
]

PREFIJO_OC = "OC-202604"
PREFIJO_OS = "OS-202605"

def siguiente_consecutivo(df, prefijo):
    ultimo = 0
    if not df.empty and "ORDEN" in df.columns:
        for orden in df["ORDEN"].astype(str).str.strip().unique():
            if orden.startswith(prefijo):
                sufijo = orden[len(prefijo):]
                if sufijo.isdigit():
                    ultimo = max(ultimo, int(sufijo))
    if ultimo == 0:
        ultimo = 99
    return ultimo + 1

EMPRESA = {
    "nombre": "Asuserviciosss SAS",
    "nit": "901224239-3",
    "direccion": "CL 67 22 62 CA 14 BRR PARNASO",
    "telefono": "3186565776",
    "correo": "asuserviciosss@hotmail.com",
    "regimen": "COMUN",
}

logo_actual = LOGO_EMBEBIDO

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

def parse_iva(x, defecto=0.19):
    try:
        v = float(str(x).strip().replace("%", "").replace(",", "."))
    except ValueError:
        return defecto
    return v / 100 if v > 1 else v

def fmt_cop(v):
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
    return str(codigo).strip().upper().startswith("SER")

def fecha_dt(x):
    t = str(x).strip()
    try:
        return pd.to_datetime(t, dayfirst="/" in t)
    except Exception:
        return pd.NaT

def ordenar_recientes(df):
    if df.empty or "FECHA" not in df.columns:
        return df
    num = df["ORDEN"].map(lambda o: int(re.sub(r"\D", "", str(o)) or 0))
    return (df.assign(_f=df["FECHA"].map(fecha_dt), _n=num)
              .sort_values(["_f", "_n"], ascending=[False, False], na_position="last")
              .drop(columns=["_f", "_n"])
              .reset_index(drop=True))

df_oc = cargar_datos(EXCEL_OC, COLS_OC)
df_prov = cargar_datos(EXCEL_PROVEEDORES, ["Nit", "Razon Social /Nombre", "Contacto", "Telefono / Celular", "Correo Electronico", "Direccion", "Ciudad", "Condicion de Pago", "Fecha registro"])
df_req = cargar_datos(EXCEL_REQUISICIONES, ["Requisicion", "Tipo Requisicion", "Fecha De Creacion", "Orden De Pedido", "Cec", "Cliente/Proyecto", "Area/Deprtamento", "Solicitante", "Cod Material", "Descripcion", "Ref", "Cant.", "Und.", "Observaciones"])
df_cc = cargar_datos(EXCEL_CENTROS_COSTOS, ["CECO", "Cliente / Proyecto", "Area_Departamento"])
df_mat = cargar_datos(EXCEL_MATERIALES, ["Familia", "Código", "Descripción", "Referencia", "Unidad"])

st.title("📦 Órdenes de Compra y/o Servicios Multi-Ítem")
st.markdown("Generación integrada desde Requisiciones con múltiples materiales, cálculo de IVA y formato PDF.")

pestana1, pestana2, pestana3, pestana4 = st.tabs([
    "➕ Emitir Nueva Orden", 
    "🖨️ Consultar, Imprimir y Guardar PDF", 
    "📋 Ver Todas las Órdenes",
    "🔍 Buscar, Aprobar y Anular"
])

with pestana1:
    st.subheader("✍️ Formulario de Emisión de Orden")

    msg_ok = st.session_state.pop("oc_msg_ok", None)
    if msg_ok:
        st.success(msg_ok)

    col_rq, col_tipo = st.columns([2, 1])
    with col_tipo:
        tipo_orden = st.selectbox("Tipo de Orden", ["OS (Orden de Servicios)", "OC (Orden de Compra)"], key="oc_tipo")

    es_servicio = tipo_orden.startswith("OS")
    if es_servicio:
        st.caption("ℹ️ Las Órdenes de Servicio (OS) solo admiten códigos que empiecen por **SER** (ej. SER01001).")

    opciones_req = ["-- Ninguna (Ingreso Manual) --"]
    if not df_req.empty and "Requisicion" in df_req.columns:
        df_req_filtrado = df_req.copy()
        if "Tipo Requisicion" in df_req_filtrado.columns:
            tipo_buscado = "Servicio" if es_servicio else "Compra"
            df_req_filtrado = df_req_filtrado[df_req_filtrado["Tipo Requisicion"].str.strip().str.lower() == tipo_buscado.lower()]
        opciones_req += list(df_req_filtrado["Requisicion"].unique())

    with col_rq:
        req_seleccionada = st.selectbox("📂 Cargar datos desde Requisición (RQ)", opciones_req)

    # =========================================================================
    # 🚫 VALIDACIÓN: BLOQUEAR SI LA REQUISICIÓN YA TIENE ORDEN EMITIDA
    # =========================================================================
    rq_ya_tiene_oc = False
    orden_existente_asociada = ""

    if req_seleccionada != "-- Ninguna (Ingreso Manual) --" and not df_oc.empty and "REQUISICIO" in df_oc.columns:
        match_existente = df_oc[df_oc["REQUISICIO"].str.strip().str.lower() == req_seleccionada.strip().lower()]
        if not match_existente.empty:
            rq_ya_tiene_oc = True
            orden_existente_asociada = str(match_existente.iloc[0].get("ORDEN", ""))

    if rq_ya_tiene_oc:
        st.error(f"❌ **La Requisición [{req_seleccionada}] ya cuenta con una Orden de Compra/Servicio emitida previamente ({orden_existente_asociada}).** No se permite generar una nueva orden para la misma requisición.")
        st.stop()
    # =========================================================================

    if "items_orden_temp" not in st.session_state:
        st.session_state.items_orden_temp = []

    if "ultima_req_sel" not in st.session_state:
        st.session_state.ultima_req_sel = ""

    if "oc_ver" not in st.session_state:
        st.session_state.oc_ver = 0

    if req_seleccionada == "-- Ninguna (Ingreso Manual) --":
        firma_sel = req_seleccionada                        
    else:
        firma_sel = f"{req_seleccionada}|{tipo_orden}"     

    pedido_sugerido = "Pendiente"
    if req_seleccionada != "-- Ninguna (Ingreso Manual) --" and not df_req.empty:
        match_req_ped = df_req[df_req["Requisicion"].str.lower() == req_seleccionada.lower()]
        if not match_req_ped.empty and "Orden De Pedido" in match_req_ped.columns:
            val_ped = str(match_req_ped.iloc[0].get("Orden De Pedido", "")).strip()
            if val_ped and val_ped not in ("nan", "None", ""):
                pedido_sugerido = val_ped

    if firma_sel != st.session_state.ultima_req_sel:
        st.session_state.ultima_req_sel = firma_sel
        st.session_state.items_orden_temp = []
        st.session_state.oc_ver += 1
        st.session_state.oc_omitidos = 0
        
        keys_a_borrar = [k for k in st.session_state.keys() if k.startswith("ord_")]
        for k in keys_a_borrar:
            del st.session_state[k]

        if req_seleccionada != "-- Ninguna (Ingreso Manual) --" and not df_req.empty:
            match_reqs = df_req[df_req["Requisicion"].str.lower() == req_seleccionada.lower()]
            
            for _, r_item in match_reqs.iterrows():
                cod_mat = str(r_item.get("Cod Material", "")).strip()
                desc_mat = str(r_item.get("Descripcion", "")).strip()
                ref_val = str(r_item.get("Ref", "NA")).strip()
                
                if es_servicio and not es_codigo_ser(cod_mat):
                    st.session_state.oc_omitidos = st.session_state.get("oc_omitidos", 0) + 1
                    continue

                cant_val = parse_cant(r_item.get("Cant.", 1))
                und_val = str(r_item.get("Und.", "Und")).strip() or "Und"
                
                st.session_state.items_orden_temp.append({
                    "CODIGO": cod_mat,
                    "DESCRIPCION": desc_mat,
                    "REFERENCIA": ref_val,
                    "CANT": cant_val,
                    "UND": und_val,
                    "IVA": 0.19,
                    "V. UNIT": 0.0,
                    "V.TOTAL": 0.0
                })

    if st.session_state.get("oc_omitidos", 0) > 0:
        st.warning(f"⚠️ Se omitieron {st.session_state.oc_omitidos} ítem(s) de la RQ que no empiezan por SER, ya que seleccionó Orden de Servicio (OS).")

    col_fec, col_prov, col_est = st.columns([1, 2, 1])
    with col_fec:
        fecha_emision = st.text_input("Fecha de Emisión", value=str(date.today()), disabled=True)
    with col_prov:
        opciones_prov = ["-- Seleccione Proveedor --"]
        if not df_prov.empty and "Razon Social /Nombre" in df_prov.columns:
            opciones_prov += list(df_prov["Razon Social /Nombre"].unique())
        prov_seleccionado = st.selectbox("Proveedor", opciones_prov, key=f"oc_prov_{st.session_state.oc_ver}")
    with col_est:
        estado_orden = st.selectbox("Estado Inicial", ["ELABORADA"], disabled=True, key=f"oc_est_{st.session_state.oc_ver}")

    col_ped, col_vacio = st.columns([2, 1])
    with col_ped:
        n_pedido = st.text_input("N. Pedido / Referencia SAP", value=pedido_sugerido, key=f"oc_ped_{st.session_state.oc_ver}")

    st.markdown("---")
    st.markdown("### 📝 Observaciones y Firmas de Autorización")
    
    col_obs1, col_obs2 = st.columns(2)
    with col_obs1:
        observaciones_orden = st.text_area(
            "Observaciones / Términos",
            value="Suministro autorizado bajo los términos contractuales vigentes.",
            help="Ingrese notas, términos o condiciones especiales para el proveedor.",
            key=f"input_obs_{st.session_state.oc_ver}"
        )
    with col_obs2:
        elaborado_por = st.text_input(
            "Elaborado por", 
            value=st.session_state.get("username", "Juan Galeano"),
            key=f"input_elab_{st.session_state.oc_ver}"
        )
        aprobado_por = st.text_input(
            "Aprobado / Gerencia (Nombre)", 
            value="Gerencia Logística",
            key=f"input_aprob_por_{st.session_state.oc_ver}"
        )
    st.markdown("---")

    st.markdown("### 📋 Detalle de los Ítems de la Orden e Impuestos")

    if st.button("➕ Agregar Nuevo Ítem Manual", key=f"btn_add_item_{st.session_state.oc_ver}"):
        st.session_state.items_orden_temp.append({
            "CODIGO": "", "DESCRIPCION": "", "REFERENCIA": "NA", "CANT": 1.0, "UND": "Und", "IVA": 0.19, "V. UNIT": 0.0, "V.TOTAL": 0.0
        })
        st.rerun()

    subtotal_acumulado = 0.0
    iva_total_acumulado = 0.0
    items_actualizados = []

    for idx, item in enumerate(st.session_state.items_orden_temp):
        st.markdown(f"**Ítem #{idx + 1}**")
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 2.5, 1, 0.8, 0.8, 1.2, 1])
        
        with c1:
            cod_val = st.text_input(f"Código #{idx+1}", value=item["CODIGO"], key=f"ord_cod_{st.session_state.oc_ver}_{idx}")
        with c2:
            desc_val = st.text_input(f"Descripción #{idx+1}", value=item["DESCRIPCION"], key=f"ord_desc_{st.session_state.oc_ver}_{idx}")
        with c3:
            ref_val = st.text_input(f"Referencia #{idx+1}", value=item["REFERENCIA"], key=f"ord_ref_{st.session_state.oc_ver}_{idx}")
        with c4:
            cant_val = st.number_input(f"Cant #{idx+1}", min_value=0.01, value=float(item["CANT"]), step=1.0, key=f"ord_cant_{st.session_state.oc_ver}_{idx}")
        with c5:
            und_val = st.text_input(f"Und #{idx+1}", value=item["UND"], key=f"ord_und_{st.session_state.oc_ver}_{idx}")
        with c6:
            v_unit_val = st.number_input(f"V. Unit ($) #{idx+1}", min_value=0.0, value=float(item["V. UNIT"]), step=1000.0, key=f"ord_unit_{st.session_state.oc_ver}_{idx}")
        with c7:
            iva_opciones = [0.0, 0.05, 0.19]
            iva_actual = float(item["IVA"])
            iva_idx = iva_opciones.index(iva_actual) if iva_actual in iva_opciones else 2
            iva_val = st.selectbox(f"IVA #{idx+1}", options=iva_opciones, format_func=lambda x: f"{int(x*100)}%", index=iva_idx, key=f"ord_iva_{st.session_state.oc_ver}_{idx}")

        v_parcial = cant_val * v_unit_val
        v_iva_item = v_parcial * iva_val
        v_total_item = v_parcial + v_iva_item

        subtotal_acumulado += v_parcial
        iva_total_acumulado += v_iva_item

        items_actualizados.append({
            "CODIGO": cod_val,
            "DESCRIPCION": desc_val,
            "REFERENCIA": ref_val,
            "CANT": cant_val,
            "UND": und_val,
            "IVA": iva_val,
            "V. UNIT": v_unit_val,
            "V.TOTAL": v_total_item
        })
        st.markdown("---")

    st.session_state.items_orden_temp = items_actualizados
    v_total_final = subtotal_acumulado + iva_total_acumulado

    st.markdown(f"#### Subtotal Acumulado: `{fmt_cop(subtotal_acumulado)}` | IVA Total: `{fmt_cop(iva_total_acumulado)}` | V.TOTAL FINAL: `{fmt_cop(v_total_final)}`")

    if st.button("💾 Guardar y Emitir Orden", type="primary", use_container_width=True):
        if prov_seleccionado == "-- Seleccione Proveedor --":
            st.error("❌ Debe seleccionar un proveedor válido.")
        elif not st.session_state.items_orden_temp:
            st.error("❌ Debe agregar al menos un ítem a la orden.")
        else:
            estado_final = "ELABORADA"

            prefijo = PREFIJO_OS if es_servicio else PREFIJO_OC
            nuevo_num = siguiente_consecutivo(df_oc, prefijo)
            id_orden = f"{prefijo}{nuevo_num}"

            nit_prov = ""
            if prov_seleccionado != "-- Seleccione Proveedor --" and not df_prov.empty:
                p_row = df_prov[df_prov["Razon Social /Nombre"].str.strip().str.lower() == prov_seleccionado.strip().lower()]
                if not p_row.empty:
                    nit_prov = str(p_row.iloc[0].get("Nit", ""))

            nuevas_filas = []
            for it in st.session_state.items_orden_temp:
                nuevas_filas.append({
                    "ORDEN": id_orden,
                    "FECHA": str(date.today()),
                    "PROVEEDOR": prov_seleccionado,
                    "NIT": nit_prov,
                    "REQUISICIO": req_seleccionada if req_seleccionada != "-- Ninguna (Ingreso Manual) --" else "MANUAL",
                    "CODIGO": it["CODIGO"],
                    "DESCRIPCION": it["DESCRIPCION"],
                    "REFERENCIA": it["REFERENCIA"],
                    "CANT": it["CANT"],
                    "UND": it["UND"],
                    "IVA": f"{int(it['IVA']*100)}%",
                    "V. UNIT": it["V. UNIT"],
                    "V.TOTAL": it["V.TOTAL"],
                    "ESTADO": estado_final,
                    "N. PEDIDO": n_pedido,
                    "OBSERVACIONES": observaciones_orden,
                    "ELABORADO_POR": elaborado_por,
                    "APROBADO_POR": aprobado_por
                })

            df_nuevos = pd.DataFrame(nuevas_filas)
            df_oc = pd.concat([df_oc, df_nuevos], ignore_index=True)
            guardar_datos(df_oc, EXCEL_OC)

            st.session_state.oc_msg_ok = f"✅ ¡Orden **{id_orden}** guardada con éxito en estado **{estado_final}** (Pendiente de Firma)!"
            st.session_state.items_orden_temp = []
            st.session_state.oc_ver += 1
            st.rerun()

with pestana2:
    st.subheader("🖨️ Consultar, Imprimir y Guardar PDF")
    
    df_oc_actual = cargar_datos(EXCEL_OC, COLS_OC)
    if df_oc_actual.empty or "ORDEN" not in df_oc_actual.columns:
        st.info("No hay órdenes de compra registradas para consultar o imprimir.")
    else:
        df_oc_ordenado = ordenar_recientes(df_oc_actual)
        lista_ordenes = df_oc_ordenado["ORDEN"].astype(str).unique().tolist()
        orden_a_consultar = st.selectbox("Seleccione la Orden a Consultar e Imprimir", lista_ordenes, key="sel_imprimir_orden")
        
        if orden_a_consultar:
            df_sel = df_oc_actual[df_oc_actual["ORDEN"].astype(str) == str(orden_a_consultar)]
            if not df_sel.empty:
                primera_fila = df_sel.iloc[0]
                
                f_prov = primera_fila.get("PROVEEDOR", "")
                f_nit = primera_fila.get("NIT", "")
                f_fecha = fmt_fecha(primera_fila.get("FECHA", ""))
                f_estado = primera_fila.get("ESTADO", "")
                f_req = primera_fila.get("REQUISICIO", "")
                f_pedido = primera_fila.get("N. PEDIDO", "")
                f_obs = primera_fila.get("OBSERVACIONES", "Suministro autorizado bajo los términos contractuales vigentes.")
                f_elab = primera_fila.get("ELABORADO_POR", "Juan Galeano")
                f_aprob = primera_fila.get("APROBADO_POR", "Gerencia Logística")
                
                p_dir = "N/A"
                p_tel = "N/A"
                p_correo = "N/A"
                p_fpago = "Contado"
                if not df_prov.empty and f_prov:
                    p_match = df_prov[df_prov["Razon Social /Nombre"].str.strip().str.lower() == f_prov.strip().lower()]
                    if not p_match.empty:
                        p_dir = p_match.iloc[0].get("Direccion", "N/A")
                        p_tel = p_match.iloc[0].get("Telefono / Celular", "N/A")
                        p_correo = p_match.iloc[0].get("Correo Electronico", "N/A")
                        p_fpago = p_match.iloc[0].get("Condicion de Pago", "Contado")

                tipo_titulo = "ORDEN DE SERVICIO" if orden_a_consultar.startswith("OS") else "ORDEN DE COMPRA"
                
                filas_tabla_html = ""
                subtotal_print = 0.0
                iva_print = 0.0
                
                for idx_i, row in df_sel.iterrows():
                    c_cant = parse_cant(row.get("CANT", 1))
                    c_unit = parse_valor(row.get("V. UNIT", 0))
                    c_parcial = c_cant * c_unit
                    c_iva_porc = parse_iva(row.get("IVA", "19%"))
                    c_iva_val = c_parcial * c_iva_porc
                    c_tot_item = c_parcial + c_iva_val
                    
                    subtotal_print += c_parcial
                    iva_print += c_iva_val
                    
                    filas_tabla_html += f"""<tr>
<td style="padding: 6px; border: 1px solid #ddd; text-align: center;">{idx_i + 1}</td>
<td style="padding: 6px; border: 1px solid #ddd; text-align: center;">{esc(str(row.get('REQUISICIO', f_req)))}</td>
<td style="padding: 6px; border: 1px solid #ddd; text-align: center;">{esc(str(row.get('CODIGO','')))}</td>
<td style="padding: 6px; border: 1px solid #ddd; text-align: left;">{esc(str(row.get('DESCRIPCION','')))}</td>
<td style="padding: 6px; border: 1px solid #ddd; text-align: center;">{esc(str(row.get('REFERENCIA','NA')))}</td>
<td style="padding: 6px; border: 1px solid #ddd; text-align: center;">{fmt_num(c_cant)}</td>
<td style="padding: 6px; border: 1px solid #ddd; text-align: center;">{esc(str(row.get('UND','Und')))}</td>
<td style="padding: 6px; border: 1px solid #ddd; text-align: center;">{int(c_iva_porc*100)}%</td>
<td style="padding: 6px; border: 1px solid #ddd; text-align: right;">{fmt_cop(c_unit)}</td>
<td style="padding: 6px; border: 1px solid #ddd; text-align: right;">{fmt_cop(c_tot_item)}</td>
</tr>"""
                
                total_general_print = subtotal_print + iva_print
                texto_firma_aprobado = esc(f_aprob) if f_estado.upper() == "APROBADA" else ""
                
                html_orden = f"""<div style="background-color: white; color: black; padding: 25px; font-family: Arial, sans-serif; border: 1px solid #ccc; border-radius: 8px;">
<table style="width: 100%; border-collapse: collapse; margin-bottom: 10px;">
<tr>
<td style="width: 45%; vertical-align: top;">
<h3 style="margin: 0; color: #002D62; font-size: 18px;">{EMPRESA['nombre']}</h3>
<p style="margin: 2px 0; font-size: 11px; color: #333;"><b>Nit:</b> {EMPRESA['nit']}</p>
<p style="margin: 2px 0; font-size: 11px; color: #333;">{EMPRESA['direccion']}</p>
<p style="margin: 2px 0; font-size: 11px; color: #333;">Tel. {EMPRESA['telefono']}</p>
<p style="margin: 2px 0; font-size: 11px; color: #333;">Correo: {EMPRESA['correo']}</p>
<p style="margin: 2px 0; font-size: 11px; color: #333;">Régimen: {EMPRESA['regimen']}</p>
</td>
<td style="width: 25%; text-align: center; vertical-align: middle;">
<img src="{logo_actual}" style="max-height: 65px; max-width: 120px;" />
</td>
<td style="width: 30%; text-align: right; vertical-align: top;">
<p style="margin: 0; font-size: 14px; font-weight: bold; color: #777;">ORIGINAL</p>
<h4 style="margin: 5px 0; color: #004080; font-size: 14px;">{tipo_titulo}</h4>
<p style="margin: 0; font-size: 15px; font-weight: bold; color: #000;">{orden_a_consultar}</p>
<p style="margin: 3px 0; font-size: 11px; color: #333;"><b>Fecha de creación:</b> {f_fecha}</p>
<p style="margin: 3px 0; font-size: 11px; color: #2e7d32;"><b>Estado:</b> {f_estado}</p>
<p style="margin: 3px 0; font-size: 11px; color: #333;"><b>N. Pedido:</b> {f_pedido}</p>
</td>
</tr>
</table>
<hr style="border: 1px solid #004080; margin: 10px 0 15px 0;">
<table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 15px; border: 1px solid #b0c4de;">
<tr style="background-color: #f0f4f8;">
<td style="padding: 6px; width: 65%; border: 1px solid #b0c4de;"><b>Señores:</b> {esc(f_prov)}</td>
<td style="padding: 6px; width: 35%; border: 1px solid #b0c4de;"><b>Correo:</b> {esc(p_correo)}</td>
</tr>
<tr>
<td style="padding: 6px; border: 1px solid #b0c4de;"><b>Nit/Cédula:</b> {esc(f_nit)}</td>
<td style="padding: 6px; border: 1px solid #b0c4de;"><b>Forma de pago:</b> {esc(p_fpago)}</td>
</tr>
<tr style="background-color: #f0f4f8;">
<td style="padding: 6px; border: 1px solid #b0c4de;"><b>Dirección:</b> {esc(p_dir)}</td>
<td style="padding: 6px; border: 1px solid #b0c4de;"><b>Requisición:</b> {esc(f_req)}</td>
</tr>
<tr>
<td style="padding: 6px; border: 1px solid #b0c4de;" colspan="2"><b>Tel.:</b> {esc(p_tel)}</td>
</tr>
</table>
<table style="width: 100%; border-collapse: collapse; font-size: 10px; margin-bottom: 15px;">
<thead>
<tr style="background-color: #004080; color: white;">
<th style="padding: 6px; border: 1px solid #ddd; text-align: center;">Ítem</th>
<th style="padding: 6px; border: 1px solid #ddd; text-align: center;">Requisición</th>
<th style="padding: 6px; border: 1px solid #ddd; text-align: center;">Cód. Material</th>
<th style="padding: 6px; border: 1px solid #ddd; text-align: left;">Descripción</th>
<th style="padding: 6px; border: 1px solid #ddd; text-align: center;">Ref</th>
<th style="padding: 6px; border: 1px solid #ddd; text-align: center;">Cant.</th>
<th style="padding: 6px; border: 1px solid #ddd; text-align: center;">Und.</th>
<th style="padding: 6px; border: 1px solid #ddd; text-align: center;">IVA</th>
<th style="padding: 6px; border: 1px solid #ddd; text-align: right;">Precio</th>
<th style="padding: 6px; border: 1px solid #ddd; text-align: right;">Total</th>
</tr>
</thead>
<tbody>
{filas_tabla_html}
</tbody>
</table>
<table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 25px;">
<tr>
<td style="width: 58%; vertical-align: top; border: 1px solid #b0c4de; padding: 8px;">
<b>Observaciones / Términos:</b><br>
<div style="margin-top: 5px; font-size: 10px; color: #333;">
{esc(f_obs)}
</div>
</td>
<td style="width: 2%;"></td>
<td style="width: 40%; vertical-align: top; border: 1px solid #b0c4de; padding: 0;">
<table style="width: 100%; border-collapse: collapse; font-size: 11px;">
<tr style="background-color: #f0f4f8; border-bottom: 1px solid #b0c4de;">
<td style="padding: 6px; text-align: left;"><b>Subtotal</b></td>
<td style="padding: 6px; text-align: right;">{fmt_cop(subtotal_print)}</td>
</tr>
<tr style="border-bottom: 1px solid #b0c4de;">
<td style="padding: 6px; text-align: left;"><b>IVA</b></td>
<td style="padding: 6px; text-align: right;">{fmt_cop(iva_print)}</td>
</tr>
<tr style="background-color: #004080; color: white; font-weight: bold;">
<td style="padding: 8px; text-align: left;">VALOR TOTAL</td>
<td style="padding: 8px; text-align: right;">{fmt_cop(total_general_print)}</td>
</tr>
</table>
</td>
</tr>
</table>
<table style="width: 100%; font-size: 10px; margin-top: 40px; text-align: center;">
<tr>
<td style="width: 33%;">
<div style="font-weight: bold; font-size: 11px; margin-bottom: 3px; color: #002D62;">{esc(f_elab)}</div>
<div style="border-top: 1px solid #333; width: 80%; margin: 0 auto; padding-top: 5px;">
Elaborado por
</div>
</td>
<td style="width: 33%;">
<div style="font-weight: bold; font-size: 11px; margin-bottom: 3px; color: #002D62;">{texto_firma_aprobado}</div>
<div style="border-top: 1px solid #333; width: 80%; margin: 0 auto; padding-top: 5px;">
Aprobado / Gerencia
</div>
</td>
<td style="width: 34%;">
<div style="margin-bottom: 3px; color: transparent;">&nbsp;</div>
<div style="border-top: 1px solid #333; width: 80%; margin: 0 auto; padding-top: 5px;">
Recibido Proveedor (Firma y Sello)
</div>
</td>
</tr>
</table>
</div>"""
                
                st.markdown(html_orden, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                b64_html = base64.b64encode(html_orden.encode("utf-8")).decode("utf-8")
                link_impresion = f'<a href="data:text/html;base64,{b64_html}" target="_blank" style="display: block; text-align: center; background-color: #004080; color: white; padding: 12px; border-radius: 5px; text-decoration: none; font-weight: bold; font-family: Arial;">🖨️ Abrir Vista de Impresión / Guardar PDF</a>'
                st.markdown(link_impresion, unsafe_allow_html=True)

with pestana3:
    st.subheader("📋 Ver Todas las Órdenes Registradas")
    df_oc_actual = cargar_datos(EXCEL_OC, COLS_OC)
    if not df_oc_actual.empty:
        df_oc_ordenado = ordenar_recientes(df_oc_actual)
        st.dataframe(df_oc_ordenado, use_container_width=True)
    else:
        st.info("No hay órdenes registradas todavía.")

with pestana4:
    st.subheader("🔍 Búsqueda, Revisión y Aprobación de Órdenes")
    
    df_oc_actual = cargar_datos(EXCEL_OC, COLS_OC)
    if df_oc_actual.empty:
        st.info("No hay órdenes registradas para administrar.")
    else:
        ver_solo_elaboradas = st.checkbox("📌 Mostrar únicamente órdenes ELABORADAS (Pendientes por firma)", value=True)
        
        df_filtrado = df_oc_actual.copy()
        if ver_solo_elaboradas:
            df_filtrado = df_filtrado[df_filtrado["ESTADO"].str.upper() == "ELABORADA"]
            
        texto_busqueda = st.text_input("🔎 Buscar por N° de Orden, Proveedor o Requisición", "").strip().lower()
        if texto_busqueda:
            df_filtrado = df_filtrado[
                df_filtrado["ORDEN"].str.lower().str.contains(texto_busqueda) |
                df_filtrado["PROVEEDOR"].str.lower().str.contains(texto_busqueda) |
                df_filtrado["REQUISICIO"].str.lower().str.contains(texto_busqueda) |
                df_filtrado["N. PEDIDO"].str.lower().str.contains(texto_busqueda)
            ]
        
        lista_ordenes_filtro = df_filtrado["ORDEN"].astype(str).unique().tolist()
        
        if not lista_ordenes_filtro:
            st.warning("⚠️ No se encontraron órdenes con los filtros seleccionados.")
        else:
            orden_admin = st.selectbox("Seleccione la Orden a Revisar y Firmar", lista_ordenes_filtro, key="sel_admin_orden")
            
            if orden_admin:
                df_item_sel = df_oc_actual[df_oc_actual["ORDEN"].astype(str) == str(orden_admin)]
                if not df_item_sel.empty:
                    primera_fila = df_item_sel.iloc[0]
                    estado_actual = str(primera_fila.get("ESTADO", "ELABORADA"))
                    prov_actual = str(primera_fila.get("PROVEEDOR", ""))
                    nit_actual = str(primera_fila.get("NIT", ""))
                    req_actual = str(primera_fila.get("REQUISICIO", ""))
                    pedido_actual = str(primera_fila.get("N. PEDIDO", ""))
                    obs_actual = str(primera_fila.get("OBSERVACIONES", ""))
                    
                    st.markdown("---")
                    st.markdown(f"### 📄 Detalle de la Orden: **{orden_admin}**")
                    
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.markdown(f"**Proveedor:** {prov_actual}")
                        st.markdown(f"**NIT:** {nit_actual}")
                    with col_info2:
                        st.markdown(f"**Requisición:** {req_actual}")
                        st.markdown(f"**N. Pedido:** {pedido_actual}")
                    with col_info3:
                        st.markdown(f"**Estado Actual:** `{estado_actual}`")
                        st.markdown(f"**Observaciones:** {obs_actual}")
                    
                    st.markdown("#### 📦 Ítems y Precios a Firmar:")
                    subtotal_rev = 0.0
                    iva_rev = 0.0
                    
                    tabla_items_revi = []
                    for _, row_it in df_item_sel.iterrows():
                        c_cant = parse_cant(row_it.get("CANT", 1))
                        c_unit = parse_valor(row_it.get("V. UNIT", 0))
                        c_parcial = c_cant * c_unit
                        c_iva_porc = parse_iva(row_it.get("IVA", "19%"))
                        c_iva_val = c_parcial * c_iva_porc
                        c_tot = c_parcial + c_iva_val
                        
                        subtotal_rev += c_parcial
                        iva_rev += c_iva_val
                        
                        tabla_items_revi.append({
                            "Código": row_it.get("CODIGO", ""),
                            "Descripción": row_it.get("DESCRIPCION", ""),
                            "Ref": row_it.get("REFERENCIA", ""),
                            "Cant": fmt_num(c_cant),
                            "Und": row_it.get("UND", ""),
                            "V. Unitario": fmt_cop(c_unit),
                            "IVA": f"{int(c_iva_porc*100)}%",
                            "Total Ítem": fmt_cop(c_tot)
                        })
                    
                    df_tabla_revi = pd.DataFrame(tabla_items_revi)
                    st.dataframe(df_tabla_revi, use_container_width=True)
                    
                    total_general_rev = subtotal_rev + iva_rev
                    st.markdown(f"**Subtotal:** `{fmt_cop(subtotal_rev)}` | **IVA Total:** `{fmt_cop(iva_rev)}` | **VALOR TOTAL GENERAL:** `{fmt_cop(total_general_rev)}`")
                    st.markdown("---")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    
                    with c_btn1:
                        if estado_actual == "ELABORADA":
                            st.markdown("### ✍️ Firma y Aprobación Gerencial")
                            pass_aprobacion = st.text_input("🔑 Contraseña de Gerencia", type="password", key=f"pass_aprob_{orden_admin}")
                            if st.button("✅ Firmar y Aprobar Orden", type="primary"):
                                if pass_aprobacion.strip() == "gerencia2026":
                                    df_oc_actual.loc[df_oc_actual["ORDEN"].astype(str) == str(orden_admin), "ESTADO"] = "APROBADA"
                                    guardar_datos(df_oc_actual, EXCEL_OC)
                                    st.success(f"🎉 ¡La orden **{orden_admin}** ha sido APROBADA y firmada con éxito!")
                                    st.rerun()
                                else:
                                    st.error("❌ Contraseña de gerencia incorrecta.")
                        elif estado_actual == "APROBADA":
                            st.info("ℹ️ Esta orden ya se encuentra **APROBADA** y firmada.")
                        else:
                            st.warning("⚠️ Esta orden está **ANULADA** y no se puede aprobar.")

                    with c_btn2:
                        st.markdown("### ⚠️ Zona de Peligro")
                        confirmar_eliminar = st.checkbox(f"Confirmar anulación / eliminación de {orden_admin}", key=f"chk_del_{orden_admin}")
                        if st.button("🗑️ Eliminar / Anular Orden de la Base de Datos", type="secondary"):
                            if confirmar_eliminar:
                                df_oc_actual = df_oc_actual[df_oc_actual["ORDEN"].astype(str) != str(orden_admin)]
                                guardar_datos(df_oc_actual, EXCEL_OC)
                                st.success(f"🗑️ La orden **{orden_admin}** fue eliminada correctamente.")
                                st.rerun()
                            else:
                                st.warning("⚠️ Debe marcar la casilla de confirmación para eliminar la orden.")
