import streamlit as st

# Validación de seguridad: Si no ha iniciado sesión, bloquea el módulo
if not st.session_state.get("password_correct", False):
    st.error("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal (Inicio / Principal).")
    st.stop()
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Gestión de Requisiciones", page_icon="🛒", layout="wide")

EXCEL_REQUISICIONES = "base_requisiciones.xlsx"
EXCEL_CENTROS_COSTOS = "base_centros_costos.xlsx"
EXCEL_PROVEEDORES = "base_proveedores.xlsx"
EXCEL_MATERIALES = "base_materiales.xlsx"

def cargar_datos(archivo, columnas_default):
    if os.path.exists(archivo):
        df = pd.read_excel(archivo, dtype=str)
        df = df.fillna("")
        for col in columnas_default:
            if col not in df.columns:
                df[col] = ""
        return df[columnas_default]
    else:
        return pd.DataFrame(columns=columnas_default)

def guardar_datos(df, archivo):
    df.to_excel(archivo, index=False)

COLS_REQ = [
    "Requisicion", "Fecha De Creacion", "Orden De Pedido", "Cec", 
    "Cliente/Proyecto", "Area/Deprtamento", "Solicitante", 
    "Cod Material", "Descripcion", "Ref", "Cant.", "Und.", "Observaciones"
]

df_req = cargar_datos(EXCEL_REQUISICIONES, COLS_REQ)
df_cc = cargar_datos(EXCEL_CENTROS_COSTOS, ["CECO", "Cliente / Proyecto", "Area_Departamento"])
df_mat = cargar_datos(EXCEL_MATERIALES, ["Familia", "Código", "Descripción", "Referencia", "Unidad"])

st.title("🛒 Gestión de Requisiciones Multi-Ítem")
st.markdown("Generación de requisiciones con múltiples materiales y búsqueda avanzada.")

# Inicializar estados de sesión para los ítems temporales
if "items_req" not in st.session_state:
    st.session_state.items_req = []
if "modo_busqueda_req" not in st.session_state:
    st.session_state.modo_busqueda_req = False
if "txt_buscar_req" not in st.session_state:
    st.session_state.txt_buscar_req = ""

def limpiar_formulario_req():
    st.session_state.items_req = []
    keys_to_clear = ["req_orden", "req_solicitante", "req_ceco", "req_obs_gral"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

col_b1, col_b2 = st.columns(2)
with col_b1:
    if st.button("➕ Nuevo Registro / Limpiar"):
        st.session_state.modo_busqueda_req = False
        st.session_state.txt_buscar_req = ""
        limpiar_formulario_req()
        st.rerun()
with col_b2:
    if st.button("🔍 Modo Buscar / Filtrar"):
        st.session_state.modo_busqueda_req = True
        st.rerun()

st.markdown("---")

if st.session_state.modo_busqueda_req:
    st.subheader("🔍 Buscar o Filtrar Requisiciones")
    c_bus1, c_bus2 = st.columns([3, 1])
    with c_bus1:
        filtro_busqueda = st.text_input("Escriba número de requisición, CeCo, cliente, material o solicitante:", value=st.session_state.txt_buscar_req)
    with c_bus2:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_ejecutar_busqueda = st.button("Filtrar Tabla")

    if btn_ejecutar_busqueda or filtro_busqueda:
        st.session_state.txt_buscar_req = filtro_busqueda

    df_filtrado = df_req.copy()
    if st.session_state.txt_buscar_req.strip() != "":
        texto_busq = st.session_state.txt_buscar_req.lower().strip()
        def cumple_busqueda(row):
            for col in COLS_REQ:
                if texto_busq in str(row.get(col, "")).lower():
                    return True
            return False
        if not df_filtrado.empty:
            df_filtrado = df_filtrado[df_filtrado.apply(cumple_busqueda, axis=1)]

    st.markdown(f"### 📋 Resultados de Búsqueda ({len(df_filtrado)} registros encontrados)")
    if not df_filtrado.empty:
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.info("No se encontraron requisiciones que coincidan con la búsqueda.")

else:
    st.subheader("➕ Crear Nueva Requisición (Múltiples Ítems)")
    
    # Cabecera general de la Requisición
    c1, c2, c3 = st.columns(3)
    with c1:
        fecha_req = st.date_input("Fecha De Creacion", value=date.today())
        solicitante = st.text_input("Solicitante", key="req_solicitante", placeholder="Nombre del solicitante")
    with c2:
        opciones_ceco = ["-- Seleccione un Centro de Costos --"]
        if not df_cc.empty:
            opciones_ceco += [
                f"{row['CECO']} - {row['Cliente / Proyecto']} ({row['Area_Departamento']})" 
                for _, row in df_cc.iterrows()
            ]
        ceco_sel = st.selectbox("Centro de Costos (CeCo)", opciones_ceco, key="req_ceco")
    with c3:
        orden_pedido = st.text_input("Orden De Pedido", key="req_orden", placeholder="Ej: Pendiente")

    st.markdown("---")
    st.markdown("#### 📚 Catálogo y Adición de Materiales")
    
    # Catálogo desplegable para consultar códigos
    with st.expander("Ver y Buscar en el Catálogo de Códigos de Materiales"):
        if not df_mat.empty:
            filtro_cat_req = st.text_input("🔍 Buscar material (código, descripción o familia):", placeholder="Ej: andamios, PAP10001...")
            df_mat_filtrado = df_mat.copy()
            if filtro_cat_req.strip() != "":
                texto_busq_cat = filtro_cat_req.lower().strip()
                def cumple_filtro_mat(row):
                    for col in df_mat.columns:
                        if texto_busq_cat in str(row.get(col, "")).lower():
                            return True
                    return False
                df_mat_filtrado = df_mat_filtrado[df_mat_filtrado.apply(cumple_filtro_mat, axis=1)]
            st.dataframe(df_mat_filtrado, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay materiales registrados en el catálogo.")

    # Formulario para agregar ítems uno a uno al carrito temporal
    with st.form("form_agregar_item"):
        d1, d2, d3, d4, d5 = st.columns(5)
        with d1:
            cod_item_in = st.text_input("Cod Material", placeholder="Ej: PAP10001")
        
        # Autocompletar datos del material si existe
        desc_auto = ""
        ref_auto = "N.A"
        und_auto = "Und"
        if cod_item_in.strip() != "" and not df_mat.empty:
            match_m = df_mat[df_mat["Código"].str.lower() == cod_item_in.strip().lower()]
            if not match_m.empty:
                desc_auto = str(match_m.iloc[0].get("Descripción", ""))
                ref_auto = str(match_m.iloc[0].get("Referencia", "N.A"))
                und_auto = str(match_m.iloc[0].get("Unidad", "Und"))

        with d2:
            desc_item_in = st.text_input("Descripcion", value=desc_auto)
        with d3:
            ref_item_in = st.text_input("Ref", value=ref_auto)
        with d4:
            cant_item_in = st.number_input("Cant.", min_value=0.01, step=1.0, value=1.0)
        with d5:
            und_item_in = st.text_input("Und.", value=und_auto)

        btn_add_item = st.form_submit_button("➕ Agregar este Ítem a la Lista")
        if btn_add_item:
            if cod_item_in.strip() == "":
                st.error("Ingrese el código del material.")
            else:
                st.session_state.items_req.append({
                    "Cod Material": cod_item_in.strip(),
                    "Descripcion": desc_item_in,
                    "Ref": ref_item_in if ref_item_in else "N.A",
                    "Cant.": str(cant_item_in),
                    "Und.": und_item_in if und_item_in else "Und"
                })
                st.success("¡Ítem agregado a la lista temporal!")
                st.rerun()

    # Mostrar la tabla temporal de ítems agregados
    if len(st.session_state.items_req) > 0:
        st.markdown(f"#### 🛒 Ítems Agregados para esta Requisición ({len(st.session_state.items_req)})")
        df_temporal = pd.DataFrame(st.session_state.items_req)
        st.dataframe(df_temporal, use_container_width=True, hide_index=True)

        if st.button("🗑️ Limpiar / Borrar Lista de Ítems"):
            st.session_state.items_req = []
            st.rerun()

    observaciones_gral = st.text_area("Observaciones Generales", placeholder="Detalle o justificación de la requisición...", key="req_obs_gral")

    # Botón maestro para guardar toda la requisición con sus múltiples ítems
    if st.button("💾 Guardar y Generar Requisición Completa", type="primary"):
        if ceco_sel == "-- Seleccione un Centro de Costos --" or not ceco_sel:
            st.error("Por favor seleccione un Centro de Costos válido.")
        elif len(st.session_state.items_req) == 0:
            st.error("Debe agregar al menos un ítem / material a la requisición.")
        else:
            ceco_puro = ceco_sel.split(" - ")[0].strip()
            cliente_proy = ""
            area_depto = ""
            if not df_cc.empty:
                match_cc = df_cc[df_cc["CECO"] == ceco_puro]
                if not match_cc.empty:
                    cliente_proy = str(match_cc.iloc[0]["Cliente / Proyecto"])
                    area_depto = str(match_cc.iloc[0]["Area_Departamento"])

            # Calcular consecutivo basado en cuántas requisiciones existen para este CeCo
            consecutivo_num = 1
            if not df_req.empty and "Requisicion" in df_req.columns:
                reqs_mismo_ceco = df_req[df_req["Requisicion"].str.startswith(ceco_puro)]
                consecutivo_num = len(reqs_mismo_ceco.drop_duplicates(subset=["Requisicion"])) + 1
                
            n_requisicion = f"{ceco_puro}-{consecutivo_num:04d}"

            # Construir filas para cada ítem de la lista temporal
            nuevas_filas = []
            for item in st.session_state.items_req:
                nuevas_filas.append({
                    "Requisicion": str(n_requisicion),
                    "Fecha De Creacion": str(fecha_req),
                    "Orden De Pedido": str(orden_pedido),
                    "Cec": str(ceco_puro),
                    "Cliente/Proyecto": str(cliente_proy),
                    "Area/Deprtamento": str(area_depto),
                    "Solicitante": str(solicitante),
                    "Cod Material": str(item["Cod Material"]),
                    "Descripcion": str(item["Descripcion"]),
                    "Ref": str(item["Ref"]),
                    "Cant.": str(item["Cant."]),
                    "Und.": str(item["Und."]),
                    "Observaciones": str(observaciones_gral)
                })

            df_nuevas = pd.DataFrame(nuevas_filas)

            # Insertar al inicio de la tabla principal (último registro de primero)
            if not df_req.empty:
                df_req = pd.concat([df_nuevas, df_req], ignore_index=True)
            else:
                df_req = df_nuevas
                
            guardar_datos(df_req, EXCEL_REQUISICIONES)
            limpiar_formulario_req()
            
            st.success(f"¡Requisición **{n_requisicion}** con {len(nuevas_filas)} ítems generada con éxito y ubicada al inicio de la tabla!")
            st.balloons()
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Historial General de Requisiciones (Último registro de primero)")
    if not df_req.empty:
        st.dataframe(df_req, use_container_width=True, hide_index=True)
    else:
        st.info("No hay requisiciones registradas actualmente.")
