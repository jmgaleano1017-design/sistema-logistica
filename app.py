import streamlit as st

st.set_page_config(
    page_title="Sistema de Gestión Logística",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Menú lateral personalizado y garantizado
with st.sidebar:
    st.image("https://img.icons8.com/color/96/logistic-apex.png", width=80)
    st.title("Módulos del Sistema")
    st.markdown("---")
    
    st.page_link("app.py", label="Inicio / Principal", icon="🏠")
    st.page_link("pages/Centros_de_costos.py", label="Centros de Costos", icon="🏢")
    st.page_link("pages/Codigos_Materiales.py", label="Códigos de Materiales", icon="📦")
    st.page_link("pages/Importar_Ordenes.py", label="Importar Órdenes", icon="📥")
    st.page_link("pages/Ordenes_Compra.py", label="Órdenes de Compra", icon="🛒")
    st.page_link("pages/Proveedores.py", label="Proveedores", icon="🤝")
    st.page_link("pages/Requisiciones.py", label="Requisiciones", icon="📝")
    
    st.markdown("---")
    st.caption("Asuserviciosss - Logística")

# Pantalla Principal (app.py)
st.title("🏭 Sistema de Gestión Logística Asuserviciosss")
st.markdown("---")
st.success("¡Bienvenido al núcleo del sistema logístico!")
st.info("👉 Utiliza el menú lateral izquierdo para navegar directamente entre todos los módulos del sistema.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Estado del Sistema", "Operativo", "100%")
with col2:
    st.metric("Módulos Activos", "6", "Conectados")
with col3:
    st.metric("Base de Datos", "Excel / Local", "Sincronizada")
