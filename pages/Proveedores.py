import streamlit as st

# Validación de seguridad: Si no ha iniciado sesión, bloquea el módulo
if not st.session_state.get("password_correct", False):
    st.error("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal (Inicio / Principal).")
    st.stop()
import pandas as pd
import os
from datetime import date, datetime

st.set_page_config(page_title="Gestión de Proveedores", page_icon="🏢", layout="wide")

EXCEL_PROVEEDORES = "base_proveedores.xlsx"

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

COLS_PROV = [
    "Nit", "Razon Social /Nombre", "Contacto", 
    "Telefono / Celular", "Correo Electronico", 
    "Direccion", "Ciudad", "Condicion de Pago", "Fecha registro"
]

df_prov = cargar_datos(EXCEL_PROVEEDORES, COLS_PROV)

st.title("🏢 Gestión y Directorio de Proveedores")
st.markdown("Registro, búsqueda, edición y control de proveedores y contratistas.")

OPCIONES_PAGO = ["Contado", "Crédito 15 días", "Crédito 30 días", "Crédito 45 días", "Crédito 60 días", "Contra Entrega"]

# Inicializar estados de sesión
if "modo_op_prov" not in st.session_state:
    st.session_state.modo_op_prov = "NUEVO"
if "form_nit" not in st.session_state:
    st.session_state.form_nit = ""
if "form_razon" not in st.session_state:
    st.session_state.form_razon = ""
if "form_contacto" not in st.session_state:
    st.session_state.form_contacto = ""
if "form_tel" not in st.session_state:
    st.session_state.form_tel = ""
if "form_correo" not in st.session_state:
    st.session_state.form_correo = ""
if "form_dir" not in st.session_state:
    st.session_state.form_dir = ""
if "form_ciudad" not in st.session_state:
    st.session_state.form_ciudad = "Barrancabermeja"
if "form_pago" not in st.session_state:
    st.session_state.form_pago = "Contado"
if "form_fecha" not in st.session_state:
    st.session_state.form_fecha = str(date.today())

# --- 1. SECCIÓN DE BÚSQUEDA Y TABLA SUPERIOR ---
st.subheader("📋 Directorio de Proveedores (Último registro de primero)")

filtro_prov = st.text_input("🔍 Buscar proveedor (escribe Nit, Razón Social, Ciudad, Condición de pago...):", placeholder="Ej: 900123456, Contado, Barrancabermeja...", key="filtro_prov_input")

df_filtrado = df_prov.copy()
if filtro_prov.strip() != "":
    txt_b = filtro_prov.lower().strip()
    def cumple_filtro_prov(row):
        for col in COLS_PROV:
            if txt_b in str(row.get(col, "")).lower():
                return True
        return False
    if not df_filtrado.empty:
        df_filtrado = df_filtrado[df_filtrado.apply(cumple_filtro_prov, axis=1)]

nit_seleccionado_tabla = None

if not df_filtrado.empty:
    cols_mostrar = [c for c in COLS_PROV if c in df_filtrado.columns]
    column_config = {
        "Nit": st.column_config.TextColumn("Nit", width="small"),
        "Razon Social /Nombre": st.column_config.TextColumn("Razon Social /Nombre", width="large"),
        "Contacto": st.column_config.TextColumn("Contacto", width="medium"),
        "Telefono / Celular": st.column_config.TextColumn("Telefono / Celular", width="small"),
        "Correo Electronico": st.column_config.TextColumn("Correo Electronico", width="medium"),
        "Direccion": st.column_config.TextColumn("Direccion", width="medium"),
        "Ciudad": st.column_config.TextColumn("Ciudad", width="small"),
        "Condicion de Pago": st.column_config.TextColumn("Condicion de Pago", width="small"),
        "Fecha registro": st.column_config.TextColumn("Fecha registro", width="small")
    }

    evento_seleccion = st.dataframe(
        df_filtrado[cols_mostrar], 
        use_container_width=True, 
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="tabla_proveedores",
        column_config=column_config
    )

    if evento_seleccion and "selection" in evento_seleccion:
        rows_sel = evento_seleccion.selection.get("rows", [])
        if rows_sel:
            idx_sel = rows_sel[0]
            fila_sel = df_filtrado.iloc[idx_sel]
            nit_seleccionado_tabla = str(fila_sel.get("Nit", "")).strip()
else:
    st.info("No se encontraron proveedores que coincidan con la búsqueda.")

st.markdown("---")

# --- 2. BOTONES DE ACCIÓN ---
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("➕ Crear Nuevo Proveedor"):
        st.session_state.modo_op_prov = "NUEVO"
        st.session_state.form_nit = ""
        st.session_state.form_razon = ""
        st.session_state.form_contacto = ""
        st.session_state.form_tel = ""
        st.session_state.form_correo = ""
        st.session_state.form_dir = ""
        st.session_state.form_ciudad = "Barrancabermeja"
        st.session_state.form_pago = "Contado"
        st.session_state.form_fecha = str(date.today())
        st.rerun()

with col_b2:
    if st.button("✏️ Cargar Proveedor Seleccionado para Editar"):
        if nit_seleccionado_tabla:
            match_prov = df_prov[df_prov["Nit"].astype(str).str.strip().str.lower() == nit_seleccionado_tabla.lower()]
            if not match_prov.empty:
                r = match_prov.iloc[0]
                st.session_state.modo_op_prov = "EDITAR"
                st.session_state.form_nit = str(r.get("Nit", ""))
                st.session_state.form_razon = str(r.get("Razon Social /Nombre", ""))
                st.session_state.form_contacto = str(r.get("Contacto", ""))
                st.session_state.form_tel = str(r.get("Telefono / Celular", ""))
                st.session_state.form_correo = str(r.get("Correo Electronico", ""))
                st.session_state.form_dir = str(r.get("Direccion", ""))
                st.session_state.form_ciudad = str(r.get("Ciudad", "Barrancabermeja"))
                st.session_state.form_pago = str(r.get("Condicion de Pago", "Contado"))
                
                # Limpieza robusta de fecha almacenada
                f_str = str(r.get("Fecha registro", "")).strip()
                if f_str == "" or f_str.lower() in ["nan", "nat", "none"]:
                    st.session_state.form_fecha = str(date.today())
                else:
                    st.session_state.form_fecha = f_str[:10]  # Tomar solo YYYY-MM-DD

                st.success(f"¡Proveedor {st.session_state.form_razon} cargado para edición!")
                st.rerun()
            else:
                st.error("No se encontró el proveedor seleccionado en la base de datos.")
        else:
            st.warning("⚠️ Primero haz clic en una fila de la tabla superior para seleccionarla.")

with col_b3:
    if st.button("🔄 Recargar Directorio"):
        st.rerun()

# --- 3. FORMULARIO DE REGISTRO / EDICIÓN ---
titulo_form = f"✍️ Editando Proveedor (Nit: {st.session_state.form_nit})" if st.session_state.modo_op_prov == "EDITAR" else "✍️ Registrar Nuevo Proveedor"
st.subheader(titulo_form)

with st.form("form_gestion_proveedor"):
    c1, c2 = st.columns(2)
    with c1:
        disabled_nit = (st.session_state.modo_op_prov == "EDITAR")
        nit_input = st.text_input("Nit", value=st.session_state.form_nit, disabled=disabled_nit, placeholder="Ej: 900123456-1")
        razon_input = st.text_input("Razon Social /Nombre", value=st.session_state.form_razon, placeholder="Ej: Suministros Industriales S.A.S.")
        contacto_input = st.text_input("Contacto", value=st.session_state.form_contacto, placeholder="Ej: Carlos Pérez")
        tel_input = st.text_input("Telefono / Celular", value=st.session_state.form_tel, placeholder="Ej: 3001234567")

    with c2:
        correo_input = st.text_input("Correo Electronico", value=st.session_state.form_correo, placeholder="Ej: ventas@suministros.com")
        dir_input = st.text_input("Direccion", value=st.session_state.form_dir, placeholder="Ej: Calle 50 # 10-20")
        ciudad_input = st.text_input("Ciudad", value=st.session_state.form_ciudad, placeholder="Ej: Barrancabermeja")
        
        pago_actual = st.session_state.form_pago
        idx_pago = OPCIONES_PAGO.index(pago_actual) if pago_actual in OPCIONES_PAGO else 0
        cond_pago_input = st.selectbox("Condicion de Pago", OPCIONES_PAGO, index=idx_pago)
        
        # Validación segura para el selector de fecha
        try:
            val_fecha = datetime.strptime(str(st.session_state.form_fecha)[:10], "%Y-%m-%d").date()
        except:
            val_fecha = date.today()
            
        fecha_input = st.date_input("Fecha registro", value=val_fecha)

    btn_guardar_prov = st.form_submit_button("💾 Guardar Proveedor en Base de Datos", type="primary")

    if btn_guardar_prov:
        if not nit_input.strip() or not razon_input.strip():
            st.error("El Nit y la Razón Social / Nombre son campos obligatorios.")
        else:
            nit_limpio = nit_input.strip()
            
            if st.session_state.modo_op_prov == "NUEVO":
                if not df_prov.empty and nit_limpio in df_prov["Nit"].values:
                    st.error(f"⚠️ Ya existe un proveedor registrado con el Nit '{nit_limpio}'.")
                else:
                    nueva_fila = pd.DataFrame([{
                        "Nit": nit_limpio,
                        "Razon Social /Nombre": str(razon_input).strip(),
                        "Contacto": str(contacto_input).strip(),
                        "Telefono / Celular": str(tel_input).strip(),
                        "Correo Electronico": str(correo_input).strip(),
                        "Direccion": str(dir_input).strip(),
                        "Ciudad": str(ciudad_input).strip(),
                        "Condicion de Pago": str(cond_pago_input),
                        "Fecha registro": str(fecha_input)
                    }])
                    
                    if not df_prov.empty:
                        df_prov = pd.concat([nueva_fila, df_prov], ignore_index=True)
                    else:
                        df_prov = nueva_fila
                        
                    guardar_datos(df_prov, EXCEL_PROVEEDORES)
                    st.success(f"¡Proveedor **{razon_input}** creado con éxito y ubicado al inicio!")
                    st.session_state.modo_op_prov = "NUEVO"
                    st.session_state.form_nit = ""
                    st.session_state.form_razon = ""
                    st.session_state.form_contacto = ""
                    st.session_state.form_tel = ""
                    st.session_state.form_correo = ""
                    st.session_state.form_dir = ""
                    st.session_state.form_ciudad = "Barrancabermeja"
                    st.session_state.form_pago = "Contado"
                    st.session_state.form_fecha = str(date.today())
                    st.rerun()
            else:
                mask = df_prov["Nit"].astype(str).str.strip().str.lower() == nit_limpio.lower()
                if not df_prov.empty and mask.any():
                    df_prov.loc[mask, "Razon Social /Nombre"] = str(razon_input).strip()
                    df_prov.loc[mask, "Contacto"] = str(contacto_input).strip()
                    df_prov.loc[mask, "Telefono / Celular"] = str(tel_input).strip()
                    df_prov.loc[mask, "Correo Electronico"] = str(correo_input).strip()
                    df_prov.loc[mask, "Direccion"] = str(dir_input).strip()
                    df_prov.loc[mask, "Ciudad"] = str(ciudad_input).strip()
                    df_prov.loc[mask, "Condicion de Pago"] = str(cond_pago_input)
                    df_prov.loc[mask, "Fecha registro"] = str(fecha_input)
                    
                    guardar_datos(df_prov, EXCEL_PROVEEDORES)
                    st.success(f"¡Proveedor con Nit **{nit_limpio}** actualizado correctamente!")
                    st.session_state.modo_op_prov = "NUEVO"
                    st.session_state.form_nit = ""
                    st.session_state.form_razon = ""
                    st.session_state.form_contacto = ""
                    st.session_state.form_tel = ""
                    st.session_state.form_correo = ""
                    st.session_state.form_dir = ""
                    st.session_state.form_ciudad = "Barrancabermeja"
                    st.session_state.form_pago = "Contado"
                    st.session_state.form_fecha = str(date.today())
                    st.rerun()
                else:
                    st.error(f"No se encontró el Nit '{nit_limpio}' para actualizar.")
