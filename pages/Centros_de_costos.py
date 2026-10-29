import streamlit as st

# Validación de seguridad: Si no ha iniciado sesión, bloquea el módulo
if not st.session_state.get("password_correct", False):
    st.error("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal (Inicio / Principal).")
    st.stop()
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Centros de Costos", page_icon="🏢", layout="wide")

EXCEL_CENTROS_COSTOS = "base_centros_costos.xlsx"

def cargar_datos(archivo, columnas_default):
    if os.path.exists(archivo):
        df = pd.read_excel(archivo, dtype=str)
        for col in columnas_default:
            if col not in df.columns:
                df[col] = ""
        return df[columnas_default]
    else:
        return pd.DataFrame(columns=columnas_default)

def guardar_datos(df, archivo):
    df.to_excel(archivo, index=False)

COLS_CC = [
    "Cod_Cliente_Proyecto", 
    "Cliente / Proyecto", 
    "Cod_Area", 
    "Area_Departamento", 
    "CECO", 
    "Objeto_Centro_Costo", 
    "Responsable"
]

df_cc = cargar_datos(EXCEL_CENTROS_COSTOS, COLS_CC)

st.title("🏢 Gestión de Centros de Costos (CeCo)")

MAESTRO_AREAS = {
    "01": "Admon",
    "02": "Logística",
    "03": "Mantenimiento",
    "04": "Sistemas",
    "05": "Contabilidad",
    "06": "Calidad"
}

accion_cc = st.radio(
    "Seleccione la operación a realizar:", 
    ["➕ Nuevo Registro", "✏️ Editar Registro", "🗑️ Eliminar Registro"], 
    horizontal=True
)
st.markdown("---")

if accion_cc == "➕ Nuevo Registro":
    st.subheader("Crear Nuevo Centro de Costo")
    with st.form("form_cc_nuevo"):
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### 1. Cliente / Proyecto")
            input_cliente = st.text_input("Nombre del Cliente / Proyecto", placeholder="Ej: Asuserviciosss, Sulzer...")
            
            cod_cli = "01"
            cliente_limpio = input_cliente.strip()
            
            if cliente_limpio != "":
                if not df_cc.empty and "Cliente / Proyecto" in df_cc.columns and "Cod_Cliente_Proyecto" in df_cc.columns:
                    existente = df_cc[df_cc["Cliente / Proyecto"].str.lower() == cliente_limpio.lower()]
                    if not existente.empty:
                        cod_cli = str(existente["Cod_Cliente_Proyecto"].values[0]).zfill(2)
                    else:
                        try:
                            srs_nums = pd.to_numeric(df_cc["Cod_Cliente_Proyecto"], errors='coerce').dropna()
                            next_val = int(srs_nums.max()) + 1 if not srs_nums.empty else 1
                            cod_cli = f"{next_val:02d}"
                        except:
                            cod_cli = f"{len(df_cc['Cliente / Proyecto'].unique()) + 1:02d}"
                else:
                    cod_cli = "01"

            st.info(f"📌 Código asignado al cliente: **{cod_cli}**")

        with c2:
            st.markdown("#### 2. Área / Departamento")
            cod_area = st.selectbox("Seleccione el Área", list(MAESTRO_AREAS.keys()), format_func=lambda x: f"{x} - {MAESTRO_AREAS[x]}")
            nom_area = MAESTRO_AREAS[cod_area]
            st.info(f"📌 Área seleccionada: **{nom_area}**")

        ceco_generado = f"{cod_cli}{cod_area}"
        
        st.markdown("---")
        st.success(f"🔢 **Código CeCo Resultante (Concatenado):** `'{ceco_generado}`  *({cliente_limpio} - {nom_area})*")
        
        st.markdown("#### 3. Detalle del Centro de Costo")
        objeto_contrato = st.text_area("Objeto Centro de Costo", value=f"{nom_area} {cliente_limpio}".strip(), placeholder="Describa el objeto...")
        responsable = st.text_input("Responsable", value="Juan Galeano")
            
        btn_guardar = st.form_submit_button("💾 Guardar Nuevo CeCo")
        
        if btn_guardar:
            if cliente_limpio and ceco_generado and objeto_contrato:
                if not df_cc.empty and ceco_generado in df_cc["CECO"].values:
                    st.error(f"⚠️ El código CECO '{ceco_generado}' ya existe en la base de datos.")
                else:
                    nuevo_cc = pd.DataFrame([{
                        "Cod_Cliente_Proyecto": str(cod_cli),
                        "Cliente / Proyecto": str(cliente_limpio),
                        "Cod_Area": str(cod_area),
                        "Area_Departamento": str(nom_area),
                        "CECO": str(ceco_generado),
                        "Objeto_Centro_Costo": str(objeto_contrato),
                        "Responsable": str(responsable)
                    }])
                    
                    if not df_cc.empty:
                        df_cc = pd.concat([nuevo_cc, df_cc], ignore_index=True)
                    else:
                        df_cc = nuevo_cc
                        
                    guardar_datos(df_cc, EXCEL_CENTROS_COSTOS)
                    st.success(f"¡CeCo **{ceco_generado}** registrado con éxito!")
                    st.rerun()
            else:
                st.error("Por favor completa el nombre del cliente y el objeto del centro de costo.")

elif accion_cc == "✏️ Editar Registro":
    st.subheader("Modificar Centro de Costo Existente")
    if not df_cc.empty:
        cecos_disponibles = df_cc["CECO"].tolist()
        ceco_a_editar = st.selectbox("Seleccione el CECO que desea editar:", cecos_disponibles)
        
        fila_actual = df_cc[df_cc["CECO"] == ceco_a_editar].iloc[0]
        
        with st.form("form_cc_editar"):
            c1, c2 = st.columns(2)
            with c1:
                edit_cliente = st.text_input("Nombre del Cliente / Proyecto", value=str(fila_actual["Cliente / Proyecto"]))
                edit_cod_cli = st.text_input("Código Cliente", value=str(fila_actual["Cod_Cliente_Proyecto"]))
            with c2:
                edit_cod_area = st.text_input("Código Área", value=str(fila_actual["Cod_Area"]))
                edit_area_depto = st.text_input("Área / Departamento", value=str(fila_actual["Area_Departamento"]))
            
            edit_ceco = st.text_input("Código CECO", value=str(fila_actual["CECO"]))
            edit_objeto = st.text_area("Objeto Centro de Costo", value=str(fila_actual["Objeto_Centro_Costo"]))
            edit_resp = st.text_input("Responsable", value=str(fila_actual["Responsable"]))
            
            btn_actualizar = st.form_submit_button("🔄 Actualizar Cambios")
            
            if btn_actualizar:
                df_cc.loc[df_cc["CECO"] == ceco_a_editar, "Cod_Cliente_Proyecto"] = edit_cod_cli
                df_cc.loc[df_cc["CECO"] == ceco_a_editar, "Cliente / Proyecto"] = edit_cliente
                df_cc.loc[df_cc["CECO"] == ceco_a_editar, "Cod_Area"] = edit_cod_area
                df_cc.loc[df_cc["CECO"] == ceco_a_editar, "Area_Departamento"] = edit_area_depto
                df_cc.loc[df_cc["CECO"] == ceco_a_editar, "CECO"] = edit_ceco
                df_cc.loc[df_cc["CECO"] == ceco_a_editar, "Objeto_Centro_Costo"] = edit_objeto
                df_cc.loc[df_cc["CECO"] == ceco_a_editar, "Responsable"] = edit_resp
                
                guardar_datos(df_cc, EXCEL_CENTROS_COSTOS)
                st.success(f"¡Centro de Costo {ceco_a_editar} actualizado con éxito!")
                st.rerun()
    else:
        st.info("No hay centros de costos registrados para editar.")

elif accion_cc == "🗑️ Eliminar Registro":
    st.subheader("Eliminar Centro de Costo")
    if not df_cc.empty:
        cecos_eliminar = df_cc["CECO"].tolist()
        ceco_sel_elim = st.selectbox("Seleccione el CECO que desea eliminar:", cecos_eliminar)
        
        st.warning(f"⚠️ Está a punto de eliminar el CECO: **{ceco_sel_elim}**.")
        
        if st.button("🗑️ Confirmar y Eliminar"):
            df_cc = df_cc[df_cc["CECO"] != ceco_sel_elim]
            guardar_datos(df_cc, EXCEL_CENTROS_COSTOS)
            st.success(f"¡El CECO {ceco_sel_elim} ha sido eliminado con éxito!")
            st.rerun()
    else:
        st.info("No hay centros de costos registrados para eliminar.")

st.markdown("### 📋 Tabla General de Centros de Costo")
if not df_cc.empty:
    st.dataframe(df_cc, use_container_width=True)
else:
    st.info("No hay centros de costos registrados actualmente.")
