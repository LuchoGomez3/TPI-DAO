import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Reservas de Canchas",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL del backend FastAPI
API_BASE_URL = "http://localhost:8000"

# Estilos CSS
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #1E88E5; text-align: center; margin-bottom: 2rem; }
    .metric-card { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1E88E5; }
    </style>
""", unsafe_allow_html=True)


# ===================== FUNCIONES API =====================

def api_request(endpoint: str, method: str = "GET", data: dict = None):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)

        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return None


# ===================== SECCIÓN: CLIENTES =====================

def seccion_clientes():
    st.header("👥 Gestión de Clientes")

    tab1, tab2 = st.tabs(["Ver Clientes", "Nuevo Cliente"])

    with tab1:
        clientes = api_request("/clientes/")
        if clientes:
            df = pd.DataFrame(clientes)
            st.dataframe(
                df[["id", "nombre", "apellido", "email", "telefono"]],
                use_container_width=True
            )
        else:
            st.info("No hay clientes registrados.")

    with tab2:
        st.subheader("Registrar Cliente")
        with st.form("form_cliente"):
            col1, col2 = st.columns(2)
            nombre = col1.text_input("Nombre")
            apellido = col2.text_input("Apellido")
            email = col1.text_input("Email")
            telefono = col2.text_input("Teléfono")

            if st.form_submit_button("Guardar"):
                data = {"nombre": nombre, "apellido": apellido, "email": email, "telefono": telefono}
                if api_request("/clientes/", "POST", data):
                    st.success("Cliente creado!")
                    st.rerun()


# ===================== SECCIÓN: CANCHAS =====================

def seccion_canchas():
    st.header("🏟️ Gestión de Canchas")

    tab1, tab2 = st.tabs(["Ver Canchas", "Nueva Cancha"])

    with tab1:
        canchas = api_request("/canchas/")
        if canchas:
            for c in canchas:
                tipo = c.get("tipo_cancha", {}).get("nombre", "Sin Tipo")
                desc = c.get("tipo_cancha", {}).get("descripcion", "")

                with st.expander(f"🏟️ {c['nombre']} ({tipo})"):
                    st.write(f"**Descripción:** {desc}")
                    if st.button(f"Eliminar {c['nombre']}", key=f"del_{c['id']}"):
                        api_request(f"/canchas/{c['id']}", "DELETE")
                        st.rerun()
        else:
            st.info("No hay canchas registradas.")

    with tab2:
        st.subheader("Registrar Cancha")
        # Tipos hardcodeados básicos (deben coincidir con la DB)
        tipos = {1: "F5", 2: "F7", 3: "TENIS", 4: "PADEL"}

        with st.form("form_cancha"):
            nombre = st.text_input("Nombre de la Cancha")
            tipo_sel = st.selectbox("Tipo", options=list(tipos.keys()), format_func=lambda x: tipos[x])

            if st.form_submit_button("Guardar"):
                data = {"nombre": nombre, "tipo_cancha_id": tipo_sel}
                if api_request("/canchas/", "POST", data):
                    st.success("Cancha creada!")
                    st.rerun()


# ===================== SECCIÓN: RESERVAS =====================

def seccion_reservas():
    st.header("📅 Gestión de Reservas")

    tab1, tab2 = st.tabs(["Listado", "Nueva Reserva"])

    with tab1:
        reservas = api_request("/reservas/")
        if reservas:
            data_view = []
            for r in reservas:
                cliente_nombre = f"{r.get('cliente', {}).get('nombre', 'Unknown')} {r.get('cliente', {}).get('apellido', '')}"
                cancha_nombre = r.get('cancha', {}).get('nombre', 'Unknown')
                estado = r.get('estado_reserva', {}).get('nombre', 'Unknown')

                data_view.append({
                    "ID": r["id"],
                    "Fecha": r["fecha"].split("T")[0],
                    "Hora": f"{r['hora_inicio']} - {r['hora_fin']}",
                    "Cliente": cliente_nombre,
                    "Cancha": cancha_nombre,
                    "Estado": estado
                })
            st.dataframe(pd.DataFrame(data_view), use_container_width=True)
        else:
            st.info("No hay reservas.")

    with tab2:
        clientes = api_request("/clientes/")
        canchas = api_request("/canchas/")

        if clientes and canchas:
            with st.form("new_reserva"):
                col1, col2 = st.columns(2)
                cli_id = col1.selectbox("Cliente", options=[c['id'] for c in clientes],
                                        format_func=lambda x: next(
                                            (f"{c['nombre']} {c['apellido']}" for c in clientes if c['id'] == x), ""))
                cancha_id = col2.selectbox("Cancha", options=[c['id'] for c in canchas],
                                           format_func=lambda x: next((c['nombre'] for c in canchas if c['id'] == x),
                                                                      ""))

                now = datetime.now()
                hora_default = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                fin_default = hora_default + timedelta(hours=1)

                fecha = st.date_input("Fecha", min_value=now.date())
                col3, col4 = st.columns(2)
                hora_in = col3.time_input("Inicio", value=hora_default.time(), step=3600)
                hora_fin = col4.time_input("Fin", value=fin_default.time(), step=3600)

                if st.form_submit_button("Reservar"):
                    data = {
                        "cliente_id": cli_id,
                        "cancha_id": cancha_id,
                        "fecha": fecha.isoformat(),
                        "hora_inicio": str(hora_in),
                        "hora_fin": str(hora_fin)
                    }
                    try:
                        response = requests.post(f"{API_BASE_URL}/reservas/", json=data)
                        if response.status_code == 200:
                            st.success("✅ Reserva creada exitosamente!")
                            st.rerun()
                        else:
                            error_detail = response.json().get("detail", "Error desconocido")
                            st.error(f"⚠️ No se pudo reservar: {error_detail}")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
        else:
            st.warning("Faltan clientes o canchas para poder reservar.")


# ===================== DASHBOARD (CON BOTÓN PDF) =====================

def seccion_dashboard():
    st.title("📊 Dashboard General")

    # Obtener datos
    reservas = api_request("/reservas/")
    clientes = api_request("/clientes/")
    pagos = api_request("/pagos/")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Reservas", len(reservas) if reservas else 0)
    with col2:
        st.metric("Clientes Registrados", len(clientes) if clientes else 0)
    with col3:
        total_ingresos = sum(p['monto'] for p in pagos) if pagos else 0
        st.metric("Ingresos Totales", f"${total_ingresos:,.0f}")

    st.markdown("---")

    # === SECCIÓN: REPORTE PDF ===
    st.subheader("📄 Reportes y Estadísticas")
    st.write("Generar informe completo con gráficos de ocupación y listados detallados.")

    col_pdf, col_spacer = st.columns([1, 3])

    with col_pdf:
        # Lógica para descargar PDF
        if st.button("🔄 Generar Nuevo Reporte PDF", type="primary"):
            with st.spinner("Generando gráficos y compilando PDF..."):
                try:
                    # Petición al endpoint de reportes
                    response = requests.get(f"{API_BASE_URL}/reportes/pdf")

                    if response.status_code == 200:
                        st.success("¡Reporte listo!")
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=response.content,
                            file_name="Reporte_Canchas_TPI.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Error al generar el reporte en el servidor.")
                except Exception as e:
                    st.error(f"No se pudo conectar con el sistema de reportes: {e}")


# ===================== MENÚ PRINCIPAL =====================

def main():
    if 'pagina' not in st.session_state:
        st.session_state['pagina'] = 'dashboard'

    with st.sidebar:
        st.title("Canchas TPI")
        if st.button("📊 Dashboard", use_container_width=True): st.session_state['pagina'] = 'dashboard'
        if st.button("👥 Clientes", use_container_width=True): st.session_state['pagina'] = 'clientes'
        if st.button("🏟️ Canchas", use_container_width=True): st.session_state['pagina'] = 'canchas'
        if st.button("📅 Reservas", use_container_width=True): st.session_state['pagina'] = 'reservas'

    if st.session_state['pagina'] == 'dashboard':
        seccion_dashboard()
    elif st.session_state['pagina'] == 'clientes':
        seccion_clientes()
    elif st.session_state['pagina'] == 'canchas':
        seccion_canchas()
    elif st.session_state['pagina'] == 'reservas':
        seccion_reservas()


if __name__ == "__main__":
    main()