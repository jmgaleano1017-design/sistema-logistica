import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Importar Órdenes", page_icon="📁", layout="wide")

# Validación de seguridad
if not st.session_state.get("password_correct", False):
    st.error("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal (Inicio / Principal).")
    st.stop()

EXCEL_OC = "Ordenes.xlsx"

COLS_OC_ESPERADAS = [
    "ORDEN", "FECHA", "PROVEEDOR", "NIT", "REQUISICIO", 
    "CODIGO", "DESCRIPCION", "REFERENCIA", "CANT", "UND", 
    "IVA", "V. UNIT", "V.TOTAL", "ESTADO", "N. PEDIDO"
]

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

st.title("📁 Importación Masiva de Órdenes y Servicios")
st.markdown("Sube tu archivo Excel con las órdenes anteriores para integrarlas a la base de datos oficial del sistema.")

archivo_subido = st.file_uploader("📂 Selecciona tu archivo Excel de órdenes (.xlsx)", type=["xlsx"])

if archivo_subido is not None:
    try:
        # Leer el archivo sin cabecera para buscar la fila exacta de los títulos
        df_raw = pd.read_excel(archivo_subido, header=None, dtype=str)
        df_raw = df_raw.fillna("")
        
        # 🔑 BUSCAR CON PRECISIÓN: La fila de encabezados debe contener "ORDEN" y "FECHA"
        fila_cabecera = 0
        for idx, row in df_raw.iterrows():
            fila_textos = [str(val).strip().upper() for val in row.values]
            if "ORDEN" in fila_textos and "FECHA" in fila_textos:
                fila_cabecera = idx
                break
        
        # Leer el Excel usando la fila correcta como cabecera
        df_importado = pd.read_excel(archivo_subido, header=fila_cabecera, dtype=str)
        df_importado = df_importado.fillna("")
        
        # Limpiar nombres de columnas
        df_importado.columns = [str(c).strip().upper() for c in df_importado.columns]
        
        # Eliminar filas completamente vacías
        df_importado = df_importado.dropna(how="all")
        df_importado = df_importado[df_importado.astype(str).ne("").any(axis=1)]

        # Rellenar celdas vacías hacia abajo (ffill) para las órdenes multi-ítem
        cols_a_rellenar = ["ORDEN", "FECHA", "PROVEEDOR", "NIT", "REQUISICIO", "ESTADO", "N. PEDIDO"]
        for col in cols_a_rellenar:
            if col in df_importado.columns:
                df_importado[col] = df_importado[col].replace(r'^\s*$', pd.NA, regex=True)
                df_importado[col] = df_importado[col].ffill().fillna("")
        
        columnas_actuales = {c.upper().strip(): c for c in df_importado.columns}
        df_procesado = pd.DataFrame(columns=COLS_OC_ESPERADAS)
        
        mapa_columnas = {
            "ORDEN": ["ORDEN", "NRO ORDEN", "NUMERO ORDEN"],
            "FECHA": ["FECHA", "FECHA EMISION"],
            "PROVEEDOR": ["PROVEEDOR", "RAZON SOCIAL", "TERCERO"],
            "NIT": ["NIT", "NIT PROVEEDOR", "C.C"],
            "REQUISICIO": ["REQUISICIO", "REQUISICION", "RQ"],
            "CODIGO": ["CODIGO", "COD MATERIAL", "COD"],
            "DESCRIPCION": ["DESCRIPCION", "DETALLE"],
            "REFERENCIA": ["REFERENCIA", "REF"],
            "CANT": ["CANT", "CANTIDAD"],
            "UND": ["UND", "UNIDAD"],
            "IVA": ["IVA", "IMPUESTO"],
            "V. UNIT": ["V. UNIT", "VALOR UNITARIO", "V UNIT"],
            "V.TOTAL": ["V.TOTAL", "VALOR TOTAL", "TOTAL", "V TOTAL"],
            "ESTADO": ["ESTADO", "STATUS"],
            "N. PEDIDO": ["N. PEDIDO", "PEDIDO", "N PEDIDO", "SAP"]
        }
        
        for col_dest in COLS_OC_ESPERADAS:
            encontrada = False
            for variante in mapa_columnas.get(col_dest, [col_dest]):
                if variante in columnas_actuales:
                    df_procesado[col_dest] = df_importado[columnas_actuales[variante]].astype(str).str.strip()
                    encontrada = True
                    break
            if not encontrada:
                df_procesado[col_dest] = ""

        # Filtrar solo filas que tengan un número de orden válido
        df_procesado = df_procesado[df_procesado["ORDEN"].str.strip() != ""]
        df_procesado = df_procesado.replace(["nan", "NaN", "None", "<NA>"], "")

        st.success(f"¡Archivo leído con éxito! Se detectaron los encabezados en la fila real {fila_cabecera + 1}. Vista previa:")
        st.dataframe(df_procesado.head(5), use_container_width=True)

        st.markdown(f"**Registros válidos listos para importar:** {len(df_procesado)}")
        
        if st.button("🚀 Procesar e Importar Órdenes a la Base de Datos", type="primary"):
            df_actual = cargar_datos(EXCEL_OC, COLS_OC_ESPERADAS)
            
            if not df_actual.empty:
                df_combinado = pd.concat([df_procesado, df_actual], ignore_index=True)
            else:
                df_combinado = df_procesado
                
            guardar_datos(df_combinado, EXCEL_OC)
            st.success(f"¡Importación completada con éxito! Se han integrado {len(df_procesado)} órdenes/servicios correctamente.")
            st.balloons()

    except Exception as e:
        st.error(f"⚠️ Ocurrió un error al procesar el archivo Excel: {e}")
