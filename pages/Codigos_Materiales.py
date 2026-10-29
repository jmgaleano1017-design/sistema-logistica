import streamlit as st

# Validación de seguridad: Si no ha iniciado sesión, bloquea el módulo
if not st.session_state.get("password_correct", False):
    st.error("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal (Inicio / Principal).")
    st.stop()
import pandas as pd
import os

st.set_page_config(page_title="Códigos de Materiales", page_icon="🏷️", layout="wide")

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

COLS_MAT = ["Familia", "Código", "Descripción", "Referencia", "Unidad"]
df_mat = cargar_datos(EXCEL_MATERIALES, COLS_MAT)

st.title("🏷️ Catálogo de Códigos de Materiales")
st.markdown("Gestión, búsqueda filtrada y creación de códigos de materiales.")

FAMILIAS_DATA = [
    ("Servicios", "SER", "01"),
    ("Insumos", "INS", "02"),
    ("Epp", "EPP", "03"),
    ("Dotacion", "DOT", "04"),
    ("Herramientas", "HER", "05"),
    ("Equipos", "EQU", "06"),
    ("Materiales", "MAT", "07"),
    ("Electricos", "ELE", "08"),
    ("Seguridad Industrial", "SEG", "09"),
    ("Papeleria", "PAP", "10"),
    ("Accesorios", "ACC", "11")
]
nombres_familias = [f[0] for f in FAMILIAS_DATA]
dict_prefijos = {f[0]: f[1] for f in FAMILIAS_DATA}
dict_ids = {f[0]: f[2] for f in FAMILIAS_DATA}

def generar_siguiente_codigo(familia_sel, df_actual):
    pref = dict_prefijos.get(familia_sel, "GEN")
    id_fam = dict_ids.get(familia_sel, "99")
    base_pref = pref + id_fam
    max_num = 0
    if not df_actual.empty and "Código" in df_actual.columns:
        for cod in df_actual["Código"].astype(str):
            if cod.startswith(base_pref):
                try:
                    num_str = cod[len(base_pref):]
                    n = int(num_str)
                    if n > max_num:
                        max_num = n
                except:
                    pass
    return f"{base_pref}{max_num + 1:03d}"

# Inicializar variables de sesión
if "modo_operacion" not in st.session_state:
    st.session_state.modo_operacion = "NUEVO"  # "NUEVO" o "EDITAR"
if "form_fam" not in st.session_state:
    st.session_state.form_fam = "Servicios"
if "form_codigo" not in st.session_state:
    st.session_state.form_codigo = generar_siguiente_codigo("Servicios", df_mat)
if "form_desc" not in st.session_state:
    st.session_state.form_desc = ""
if "form_ref" not in st.session_state:
    st.session_state.form_ref = ""
if "form_uni" not in st.session_state:
    st.session_state.form_uni = "Und"

# --- 1. SECCIÓN DE BÚSQUEDA Y SELECCIÓN EN LA TABLA ---
st.subheader("📋 Catálogo de Artículos")

filtro_cat = st.text_input("🔍 Buscar en el Catálogo (escribe código, descripción o familia)", placeholder="Ej: andamios, PAP10001, tractor...", key="filtro_cat_input")

df_filtrado = df_mat.copy()
if filtro_cat.strip() != "":
    texto_busq = filtro_cat.lower().strip()
    def cumple_filtro_cat(row):
        for col in COLS_MAT:
            if texto_busq in str(row.get(col, "")).lower():
                return True
        return False
    if not df_filtrado.empty:
        df_filtrado = df_filtrado[df_filtrado.apply(cumple_filtro_cat, axis=1)]

codigo_seleccionado_tabla = None

if not df_filtrado.empty:
    cols_mostrar = [c for c in COLS_MAT if c in df_filtrado.columns]
    column_config = {
        "Familia": st.column_config.TextColumn("Familia", width="medium"),
        "Código": st.column_config.TextColumn("Código", width="small"),
        "Descripción": st.column_config.TextColumn("Descripción", width="large"),
        "Referencia": st.column_config.TextColumn("Referencia", width="small"),
        "Unidad": st.column_config.TextColumn("Und", width="small")
    }

    evento_seleccion = st.dataframe(
        df_filtrado[cols_mostrar], 
        use_container_width=True, 
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="tabla_catalogo",
        column_config=column_config
    )

    if evento_seleccion and "selection" in evento_seleccion:
        rows_sel = evento_seleccion.selection.get("rows", [])
        if rows_sel:
            idx_sel = rows_sel[0]
            fila_sel = df_filtrado.iloc[idx_sel]
            codigo_seleccionado_tabla = str(fila_sel.get("Código", "")).strip()
else:
    st.info("No se encontraron materiales que coincidan con la búsqueda.")

st.markdown("---")

# --- 2. BOTONES DE ACCIÓN (NUEVO, EDITAR, RECARGAR) ---
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("➕ Crear Nuevo Registro"):
        st.session_state.modo_operacion = "NUEVO"
        st.session_state.form_fam = "Servicios"
        st.session_state.form_codigo = generar_siguiente_codigo("Servicios", df_mat)
        st.session_state.form_desc = ""
        st.session_state.form_ref = ""
        st.session_state.form_uni = "Und"
        st.rerun()

with col_b2:
    if st.button("✏️ Cargar Registro Seleccionado para Editar"):
        if codigo_seleccionado_tabla:
            # Buscar el código exacto en la base de datos general
            match_reg = df_mat[df_mat["Código"].astype(str).str.strip().str.lower() == codigo_seleccionado_tabla.lower()]
            if not match_reg.empty:
                r = match_reg.iloc[0]
                st.session_state.modo_operacion = "EDITAR"
                st.session_state.form_fam = str(r.get("Familia", "Servicios"))
                st.session_state.form_codigo = str(r.get("Código", ""))
                st.session_state.form_desc = str(r.get("Descripción", ""))
                
                ref_val = str(r.get("Referencia", ""))
                st.session_state.form_ref = "" if ref_val.lower() in ["nan", "none", "nat", ""] else ref_val
                
                uni_val = str(r.get("Unidad", ""))
                st.session_state.form_uni = "Und" if uni_val.lower() in ["nan", "none", "nat", ""] else uni_val
                
                st.success(f"¡Código {st.session_state.form_codigo} cargado para edición!")
                st.rerun()
            else:
                st.error("No se encontró el registro seleccionado en la base de datos.")
        else:
            st.warning("⚠️ Primero haz clic en una fila de la tabla superior para seleccionarla.")

with col_b3:
    if st.button("🔄 Recargar Catálogo"):
        st.rerun()

# --- 3. FORMULARIO DE CREACIÓN / EDICIÓN ---
titulo_form = "✍️ Editando Código: " + st.session_state.form_codigo if st.session_state.modo_operacion == "EDITAR" else "✍️ Creando Nuevo Código"
st.subheader(titulo_form)

with st.form("form_catalogo_materiales"):
    c1, c2 = st.columns(2)
    with c1:
        # Si estamos editando, la familia no debe cambiar para mantener la coherencia del código
        disabled_fam = (st.session_state.modo_operacion == "EDITAR")
        try:
            idx_fam = nombres_familias.index(st.session_state.form_fam)
        except:
            idx_fam = 0
            
        sel_familia = st.selectbox("Familia", nombres_familias, index=idx_fam, disabled=disabled_fam)
        st.text_input("Código (Sistema)", value=st.session_state.form_codigo, disabled=True)

    with c2:
        desc_input = st.text_input("Descripción", value=st.session_state.form_desc)
        ref_input = st.text_input("Referencia", value=st.session_state.form_ref)
        uni_input = st.text_input("Unidad de Medida", value=st.session_state.form_uni)

    btn_guardar = st.form_submit_button("💾 Guardar Registro en Base de Datos", type="primary")

    if btn_guardar:
        if not desc_input.strip():
            st.error("La descripción es obligatoria.")
        else:
            if st.session_state.modo_operacion == "NUEVO":
                nuevo_cod = generar_siguiente_codigo(sel_familia, df_mat)
                nueva_fila = pd.DataFrame([{
                    "Familia": str(sel_familia),
                    "Código": str(nuevo_cod),
                    "Descripción": str(desc_input).strip(),
                    "Referencia": str(ref_input).strip(),
                    "Unidad": str(uni_input).strip()
                }])
                if not df_mat.empty:
                    df_mat = pd.concat([nueva_fila, df_mat], ignore_index=True)
                else:
                    df_mat = nueva_fila
                guardar_datos(df_mat, EXCEL_MATERIALES)
                st.success(f"¡Nuevo registro creado con éxito! Código: {nuevo_cod}")
                st.session_state.modo_operacion = "NUEVO"
                st.session_state.form_codigo = generar_siguiente_codigo(sel_familia, df_mat)
                st.session_state.form_desc = ""
                st.session_state.form_ref = ""
                st.session_state.form_uni = "Und"
                st.rerun()
            else:
                # MODO EDITAR: Buscar el código exacto, encontrarlo, modificarlo y guardar
                cod_objetivo = st.session_state.form_codigo.strip()
                mask = df_mat["Código"].astype(str).str.strip().str.lower() == cod_objetivo.lower()
                
                if not df_mat.empty and mask.any():
                    df_mat.loc[mask, "Familia"] = str(sel_familia).strip()
                    df_mat.loc[mask, "Descripción"] = str(desc_input).strip()
                    df_mat.loc[mask, "Referencia"] = str(ref_input).strip()
                    df_mat.loc[mask, "Unidad"] = str(uni_input).strip()
                    
                    guardar_datos(df_mat, EXCEL_MATERIALES)
                    st.success(f"¡Registro **{cod_objetivo}** encontrado, editado y guardado correctamente!")
                    st.session_state.modo_operacion = "NUEVO"
                    st.session_state.form_desc = ""
                    st.session_state.form_ref = ""
                    st.session_state.form_uni = "Und"
                    st.session_state.form_codigo = generar_siguiente_codigo("Servicios", df_mat)
                    st.rerun()
                else:
                    st.error(f"No se encontró el código '{cod_objetivo}' en la base de datos para actualizar.")
