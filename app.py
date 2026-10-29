import streamlit as st

st.set_page_config(
    page_title="Sistema de Gestión Logística",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNCIÓN DE AUTENTICACIÓN ---
def check_password():
    """Retorna True si el usuario ha iniciado sesión correctamente."""
    if st.session_state.get("password_correct", False):
        return True

    # Pantalla de Login centrada
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 🏭 Inicio de Sesión")
        st.markdown("### Sistema de Gestión Logística - Asuserviciosss")
        st.markdown("---")
        
        with st.form("credentials_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
            
            if submit:
                # Comprueba contra los secrets configurados en Streamlit Cloud
                passwords = st.secrets.get("passwords", {})
                if username in passwords and passwords[username] == password:
                    st.session_state["password_correct"] = True
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("😕 Usuario o contraseña incorrectos.")
                    
    return False

# Si no ha iniciado sesión, se detiene aquí y NUNCA muestra el menú lateral ni los módulos
if not check_password():
    st.stop()


# --- APLICACIÓN PRINCIPAL (Solo se carga si las credenciales son correctas) ---

# Menú lateral con los módulos (Visible únicamente tras el login)
with st.sidebar:
    st.title("Módulos del Sistema")
    st.markdown(f"👤 **Usuario:** `{st.session_state.get('username', 'Admin')}`")
    st.markdown("---")
    
    st.page_link("app.py", label="Inicio / Principal", icon="🏠")
    st.page_link("pages/Centros_de_costos.py", label="Centros de Costos", icon="🏢")
    st.page_link("pages/Codigos_Materiales.py", label="Códigos de Materiales", icon="📦")
    st.page_link("pages/Importar_Ordenes.py", label="Importar Órdenes", icon="📥")
    st.page_link("pages/Ordenes_Compra.py", label="Órdenes de Compra", icon="🛒")
    st.page_link("pages/Proveedores.py", label="Proveedores", icon="🤝")
    st.page_link("pages/Requisiciones.py", label="Requisiciones", icon="📝")
    
    st.markdown("---")
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()

# Pantalla de Bienvenida al ingresar con éxito
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
