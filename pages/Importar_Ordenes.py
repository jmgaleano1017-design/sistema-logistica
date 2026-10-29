import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Importar Órdenes", page_icon="📁", layout="wide")

EXCEL_OC = "base_ordenes_compra.xlsx"

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
        # Leer el archivo sin cabecera fija primero para detectar dónde están los títulos reales
        df_raw = pd.read_excel(archivo_subido, header=None, dtype=str)
        df_raw = df_raw.fillna("")
        
        # Buscar la fila que contenga la palabra "orden" o "proveedor"
        fila_cabecera = 0
        for idx, row in df_raw.iterrows():
            fila_str = " ".join(row.values).lower()
            if "orden" in fila_str or "proveedor" in fila_str:
                fila_cabecera = idx
                break
        
        # Leer el Excel usando la fila correcta como cabecera
        df_importado = pd.read_excel(archivo_subido, header=fila_cabecera, dtype=str)
        df_importado = df_importado.fillna("")
        
        df_importado.columns = [str(c).strip().upper() for c in df_importado.columns]
        
        st.success(f"¡Archivo leído con éxito! Se detectaron los encabezados en la fila {fila_cabecera + 1}. Vista previa:")
        st.dataframe(df_importado.head(5), use_container_width=True)
        
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

        df_procesado = df_procesado[df_procesado["ORDEN"].str.strip() != ""]
        df_procesado = df_procesado.replace(["nan", "NaN", "None", "<NA>"], "")

        st.markdown(f"**Registros válidos listos para importar:** {len(df_procesado)}")
        
        if st.button("🚀 Procesar e Importar Órdenes a la Base de Datos", type="primary"):
            df_actual = cargar_datos(EXCEL_OC, COLS_OC_ESPERADAS)
            
            if not df_actual.empty:
                df_combinado = pd.concat([df_procesado, df_actual], ignore_index=True)
                # Opcional: conservar manteniendo orden si se desea
            else:
                df_combinado = df_procesado
                
            guardar_datos(df_combinado, EXCEL_OC)
            st.success(f"¡Importación completada con éxito! Se han integrado {len(df_procesado)} órdenes/servicios correctamente.")
            st.balloons()

    except Exception as e:
        st.error(f"⚠️ Ocurrió un error al procesar el archivo Excel: {e}")
