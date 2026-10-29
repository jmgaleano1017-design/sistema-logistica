import streamlit as st
import pandas as pd
import os

# Validación de seguridad
if not st.session_state.get("password_correct", False):
    st.error("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal.")
    st.stop()

# Definir la ruta correcta del archivo oficial
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
EXCEL_OC = os.path.join(DIRECTORIO_ACTUAL, "..", "base_ordenes_compra.xlsx")

st.title("📁 Importación Masiva y Descarga de Base Oficial")
st.markdown("Sube tu archivo Excel con las órdenes anteriores o descarga la base de datos actual sincronizada.")

# Sección de Carga Masiva
uploaded_file = st.file_uploader("Selecciona tu archivo Excel de órdenes (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df_import = pd.read_excel(uploaded_file, header=8, dtype=str)
        df_import = df_import.fillna("")
        
        st.success(f"¡Archivo leído con éxito! Se detectaron los registros en la vista previa.")
        st.dataframe(df_import.head())
        
        registros_validos = len(df_import)
        st.info(f"Registros válidos listos para importar: {registros_validos}")
        
        if st.button("🚀 Procesar e Importar Órdenes a la Base de Datos", type="primary"):
            # Guardar directamente en el archivo oficial base_ordenes_compra.xlsx
            df_import.to_excel(EXCEL_OC, index=False)
            st.success(f"¡Importación completada con éxito! Se han integrado {registros_validos} órdenes/servicios correctamente.")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

st.markdown("---")
st.subheader("📥 Sincronización y Descarga Local")
st.markdown("Haz clic en el siguiente botón para descargar el archivo oficial **`base_ordenes_compra.xlsx`** actualizado con todo el historial completo para guardarlo directamente en tu carpeta de OneDrive.")

# Botón de descarga directa de la base oficial actual
if os.path.exists(EXCEL_OC):
    with open(EXCEL_OC, "rb") as f:
        st.download_button(
            label="📥 Descargar Base Oficial Actualizada (.xlsx)",
            data=f,
            file_name="base_ordenes_compra.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
else:
    st.warning("⚠️ Aún no se encuentra el archivo base de órdenes en la ruta oficial.")
