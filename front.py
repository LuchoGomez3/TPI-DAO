import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Reservas de Canchas",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL del backend FastAPI (ajustar según tu configuración)
API_BASE_URL = "http://localhost:8000"  # Cambiar según tu puerto

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0.3rem;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 0.3rem;
    }
    </style>
""", unsafe_allow_html=True)

# ===================== FUNCIONES DE API =====================

def api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None):
    """Función genérica para realizar peticiones a la API"""
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
        st.error(f"Error en la conexión con el servidor: {str(e)}")
        return None

# ===================== SECCIÓN: CLIENTES =====================

def seccion_clientes():
    st.header("👥 Gestión de Clientes")
    
    tab1, tab2, tab3 = st.tabs(["Ver Clientes", "Agregar Cliente", "Editar/Eliminar"])
    
    with tab1:
        st.subheader("Lista de Clientes")
        clientes = api_request("/clientes")
        if clientes:
            df = pd.DataFrame(clientes)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay clientes registrados o no se pudo conectar con el servidor")
    
    with tab2:
        st.subheader("Registrar Nuevo Cliente")
        with st.form("form_cliente"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre Completo*")
                email = st.text_input("Email*")
            with col2:
                telefono = st.text_input("Teléfono*")
                dni = st.text_input("DNI/CUIT*")
            
            direccion = st.text_input("Dirección")
            
            submitted = st.form_submit_button("Registrar Cliente", use_container_width=True)
            
            if submitted:
                if nombre and email and telefono and dni:
                    data = {
                        "nombre": nombre,
                        "email": email,
                        "telefono": telefono,
                        "dni": dni,
                        "direccion": direccion
                    }
                    resultado = api_request("/clientes", "POST", data)
                    if resultado:
                        st.success("✅ Cliente registrado exitosamente!")
                        st.rerun()
                else:
                    st.error("⚠️ Por favor complete todos los campos obligatorios")
    
    with tab3:
        st.subheader("Modificar o Eliminar Cliente")
        clientes = api_request("/clientes")
        if clientes:
            cliente_nombres = [f"{c['id']} - {c['nombre']}" for c in clientes]
            cliente_sel = st.selectbox("Seleccionar Cliente", cliente_nombres)
            
            if cliente_sel:
                cliente_id = int(cliente_sel.split(" - ")[0])
                cliente = next((c for c in clientes if c['id'] == cliente_id), None)
                
                if cliente:
                    with st.form("form_editar_cliente"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre = st.text_input("Nombre", value=cliente['nombre'])
                            email = st.text_input("Email", value=cliente['email'])
                        with col2:
                            telefono = st.text_input("Teléfono", value=cliente['telefono'])
                            dni = st.text_input("DNI", value=cliente['dni'])
                        
                        direccion = st.text_input("Dirección", value=cliente.get('direccion', ''))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            actualizar = st.form_submit_button("Actualizar", use_container_width=True)
                        with col_btn2:
                            eliminar = st.form_submit_button("Eliminar", type="secondary", use_container_width=True)
                        
                        if actualizar:
                            data = {
                                "nombre": nombre,
                                "email": email,
                                "telefono": telefono,
                                "dni": dni,
                                "direccion": direccion
                            }
                            resultado = api_request(f"/clientes/{cliente_id}", "PUT", data)
                            if resultado:
                                st.success("✅ Cliente actualizado!")
                                st.rerun()
                        
                        if eliminar:
                            resultado = api_request(f"/clientes/{cliente_id}", "DELETE")
                            if resultado:
                                st.success("✅ Cliente eliminado!")
                                st.rerun()

# ===================== SECCIÓN: CANCHAS =====================

def seccion_canchas():
    st.header("🏟️ Gestión de Canchas")
    
    tab1, tab2, tab3 = st.tabs(["Ver Canchas", "Agregar Cancha", "Editar/Eliminar"])
    
    with tab1:
        st.subheader("Lista de Canchas Disponibles")
        canchas = api_request("/canchas")
        if canchas:
            for cancha in canchas:
                with st.expander(f"🏟️ {cancha['nombre']} - {cancha['tipo_deporte']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Tipo:** {cancha['tipo_deporte']}")
                        st.write(f"**Capacidad:** {cancha['capacidad']} personas")
                    with col2:
                        st.write(f"**Techada:** {'Sí' if cancha.get('techada', False) else 'No'}")
                        st.write(f"**Iluminación:** {'Sí' if cancha.get('iluminacion', False) else 'No'}")
                    with col3:
                        st.write(f"**Precio/Hora:** ${cancha.get('precio_hora', 0)}")
                        st.write(f"**Estado:** {'Activa' if cancha.get('activa', True) else 'Inactiva'}")
                    if cancha.get('descripcion'):
                        st.write(f"**Descripción:** {cancha['descripcion']}")
        else:
            st.info("No hay canchas registradas")
    
    with tab2:
        st.subheader("Registrar Nueva Cancha")
        with st.form("form_cancha"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre de la Cancha*")
                tipo_deporte = st.selectbox("Tipo de Deporte*", 
                    ["Fútbol 5", "Fútbol 7", "Fútbol 11", "Tenis", "Paddle", "Basquet", "Volley"])
                capacidad = st.number_input("Capacidad (personas)*", min_value=1, value=10)
            
            with col2:
                precio_hora = st.number_input("Precio por Hora*", min_value=0.0, value=5000.0, step=500.0)
                techada = st.checkbox("Cancha Techada")
                iluminacion = st.checkbox("Tiene Iluminación")
            
            descripcion = st.text_area("Descripción")
            
            submitted = st.form_submit_button("Registrar Cancha", use_container_width=True)
            
            if submitted:
                if nombre and tipo_deporte:
                    data = {
                        "nombre": nombre,
                        "tipo_deporte": tipo_deporte,
                        "capacidad": capacidad,
                        "precio_hora": precio_hora,
                        "techada": techada,
                        "iluminacion": iluminacion,
                        "descripcion": descripcion,
                        "activa": True
                    }
                    resultado = api_request("/canchas", "POST", data)
                    if resultado:
                        st.success("✅ Cancha registrada exitosamente!")
                        st.rerun()
                else:
                    st.error("⚠️ Complete los campos obligatorios")
    
    with tab3:
        st.subheader("Modificar o Eliminar Cancha")
        canchas = api_request("/canchas")
        if canchas:
            cancha_nombres = [f"{c['id']} - {c['nombre']}" for c in canchas]
            cancha_sel = st.selectbox("Seleccionar Cancha", cancha_nombres)
            
            if cancha_sel:
                cancha_id = int(cancha_sel.split(" - ")[0])
                cancha = next((c for c in canchas if c['id'] == cancha_id), None)
                
                if cancha:
                    with st.form("form_editar_cancha"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre = st.text_input("Nombre", value=cancha['nombre'])
                            tipo_deporte = st.selectbox("Tipo de Deporte", 
                                ["Fútbol 5", "Fútbol 7", "Fútbol 11", "Tenis", "Paddle", "Basquet", "Volley"],
                                index=["Fútbol 5", "Fútbol 7", "Fútbol 11", "Tenis", "Paddle", "Basquet", "Volley"].index(cancha['tipo_deporte']) if cancha['tipo_deporte'] in ["Fútbol 5", "Fútbol 7", "Fútbol 11", "Tenis", "Paddle", "Basquet", "Volley"] else 0)
                            capacidad = st.number_input("Capacidad", min_value=1, value=cancha['capacidad'])
                        
                        with col2:
                            precio_hora = st.number_input("Precio/Hora", min_value=0.0, value=float(cancha.get('precio_hora', 0)))
                            techada = st.checkbox("Techada", value=cancha.get('techada', False))
                            iluminacion = st.checkbox("Iluminación", value=cancha.get('iluminacion', False))
                        
                        descripcion = st.text_area("Descripción", value=cancha.get('descripcion', ''))
                        activa = st.checkbox("Cancha Activa", value=cancha.get('activa', True))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            actualizar = st.form_submit_button("Actualizar", use_container_width=True)
                        with col_btn2:
                            eliminar = st.form_submit_button("Eliminar", type="secondary", use_container_width=True)
                        
                        if actualizar:
                            data = {
                                "nombre": nombre,
                                "tipo_deporte": tipo_deporte,
                                "capacidad": capacidad,
                                "precio_hora": precio_hora,
                                "techada": techada,
                                "iluminacion": iluminacion,
                                "descripcion": descripcion,
                                "activa": activa
                            }
                            resultado = api_request(f"/canchas/{cancha_id}", "PUT", data)
                            if resultado:
                                st.success("✅ Cancha actualizada!")
                                st.rerun()
                        
                        if eliminar:
                            resultado = api_request(f"/canchas/{cancha_id}", "DELETE")
                            if resultado:
                                st.success("✅ Cancha eliminada!")
                                st.rerun()

# ===================== SECCIÓN: RESERVAS =====================

def seccion_reservas():
    st.header("📅 Gestión de Reservas")
    
    tab1, tab2, tab3 = st.tabs(["Ver Reservas", "Nueva Reserva", "Gestionar Reservas"])
    
    with tab1:
        st.subheader("Reservas Registradas")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha_desde = st.date_input("Desde", value=datetime.now().date())
        with col2:
            fecha_hasta = st.date_input("Hasta", value=datetime.now().date() + timedelta(days=7))
        with col3:
            estado_filtro = st.selectbox("Estado", ["Todas", "Confirmada", "Cancelada", "Pendiente"])
        
        reservas = api_request(f"/reservas?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}")
        if reservas:
            if estado_filtro != "Todas":
                reservas = [r for r in reservas if r.get('estado', '') == estado_filtro]
            
            df = pd.DataFrame(reservas)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay reservas en el período seleccionado")
    
    with tab2:
        st.subheader("Crear Nueva Reserva")
        
        clientes = api_request("/clientes")
        canchas = api_request("/canchas")
        
        if not clientes:
            st.warning("⚠️ No hay clientes registrados. Por favor, registre un cliente primero.")
        elif not canchas:
            st.warning("⚠️ No hay canchas disponibles. Por favor, registre una cancha primero.")
        else:
            with st.form("form_reserva"):
                col1, col2 = st.columns(2)
                
                with col1:
                    cliente_opciones = [f"{c['id']} - {c['nombre']}" for c in clientes]
                    cliente_sel = st.selectbox("Cliente*", cliente_opciones)
                    
                    cancha_opciones = [f"{c['id']} - {c['nombre']}" for c in canchas if c.get('activa', True)]
                    cancha_sel = st.selectbox("Cancha*", cancha_opciones)
                
                with col2:
                    fecha = st.date_input("Fecha*", min_value=datetime.now().date())
                    hora_inicio = st.time_input("Hora Inicio*", value=datetime.strptime("09:00", "%H:%M").time())
                
                duracion = st.number_input("Duración (horas)*", min_value=0.5, max_value=8.0, value=1.0, step=0.5)
                
                col3, col4 = st.columns(2)
                with col3:
                    iluminacion = st.checkbox("Requiere Iluminación")
                with col4:
                    torneo = st.checkbox("Es parte de un Torneo")
                
                observaciones = st.text_area("Observaciones")
                
                submitted = st.form_submit_button("Crear Reserva", use_container_width=True)
                
                if submitted:
                    cliente_id = int(cliente_sel.split(" - ")[0])
                    cancha_id = int(cancha_sel.split(" - ")[0])
                    
                    # Calcular hora fin
                    hora_fin_dt = (datetime.combine(fecha, hora_inicio) + timedelta(hours=duracion)).time()
                    
                    data = {
                        "cliente_id": cliente_id,
                        "cancha_id": cancha_id,
                        "fecha": str(fecha),
                        "hora_inicio": str(hora_inicio),
                        "hora_fin": str(hora_fin_dt),
                        "duracion": duracion,
                        "iluminacion": iluminacion,
                        "torneo": torneo,
                        "observaciones": observaciones,
                        "estado": "Confirmada"
                    }
                    
                    # Validar disponibilidad
                    disponible = api_request(f"/reservas/disponibilidad?cancha_id={cancha_id}&fecha={fecha}&hora_inicio={hora_inicio}&hora_fin={hora_fin_dt}")
                    
                    if disponible and disponible.get('disponible', False):
                        resultado = api_request("/reservas", "POST", data)
                        if resultado:
                            st.success("✅ Reserva creada exitosamente!")
                            st.rerun()
                    else:
                        st.error("❌ La cancha no está disponible en el horario seleccionado")
    
    with tab3:
        st.subheader("Modificar o Cancelar Reservas")
        reservas = api_request("/reservas")
        if reservas:
            # Filtrar reservas futuras
            reservas_futuras = [r for r in reservas if datetime.strptime(r['fecha'], "%Y-%m-%d").date() >= datetime.now().date()]
            
            if reservas_futuras:
                reserva_opciones = [f"ID {r['id']} - {r['fecha']} {r['hora_inicio']} - Cancha {r['cancha_id']}" for r in reservas_futuras]
                reserva_sel = st.selectbox("Seleccionar Reserva", reserva_opciones)
                
                if reserva_sel:
                    reserva_id = int(reserva_sel.split(" ")[1])
                    reserva = next((r for r in reservas_futuras if r['id'] == reserva_id), None)
                    
                    if reserva:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Cliente ID:** {reserva['cliente_id']}")
                            st.write(f"**Cancha ID:** {reserva['cancha_id']}")
                            st.write(f"**Fecha:** {reserva['fecha']}")
                        with col2:
                            st.write(f"**Horario:** {reserva['hora_inicio']} - {reserva['hora_fin']}")
                            st.write(f"**Estado:** {reserva.get('estado', 'N/A')}")
                            st.write(f"**Iluminación:** {'Sí' if reserva.get('iluminacion') else 'No'}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("Cancelar Reserva", type="secondary", use_container_width=True):
                                resultado = api_request(f"/reservas/{reserva_id}/cancelar", "PUT")
                                if resultado:
                                    st.success("✅ Reserva cancelada!")
                                    st.rerun()
                        with col_btn2:
                            if st.button("Eliminar Reserva", use_container_width=True):
                                resultado = api_request(f"/reservas/{reserva_id}", "DELETE")
                                if resultado:
                                    st.success("✅ Reserva eliminada!")
                                    st.rerun()
            else:
                st.info("No hay reservas futuras para gestionar")

# ===================== SECCIÓN: REPORTES =====================

def seccion_reportes():
    st.header("📊 Reportes y Estadísticas")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Reservas por Cliente", "Reservas por Cancha", "Canchas Más Usadas", "Estadísticas"])
    
    with tab1:
        st.subheader("Reservas por Cliente")
        clientes = api_request("/clientes")
        if clientes:
            cliente_opciones = ["Todos"] + [f"{c['id']} - {c['nombre']}" for c in clientes]
            cliente_sel = st.selectbox("Seleccionar Cliente", cliente_opciones, key="rep_cliente")
            
            col1, col2 = st.columns(2)
            with col1:
                fecha_desde = st.date_input("Desde", value=datetime.now().date() - timedelta(days=30), key="rep_cli_desde")
            with col2:
                fecha_hasta = st.date_input("Hasta", value=datetime.now().date(), key="rep_cli_hasta")
            
            if cliente_sel != "Todos":
                cliente_id = int(cliente_sel.split(" - ")[0])
                reservas = api_request(f"/reportes/cliente/{cliente_id}?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}")
            else:
                reservas = api_request(f"/reservas?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}")
            
            if reservas:
                df = pd.DataFrame(reservas)
                st.dataframe(df, use_container_width=True)
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Reservas", len(reservas))
                with col2:
                    total_horas = sum([r.get('duracion', 0) for r in reservas])
                    st.metric("Total Horas", f"{total_horas:.1f}")
                with col3:
                    if 'precio_total' in df.columns:
                        st.metric("Ingresos Totales", f"${df['precio_total'].sum():,.0f}")
            else:
                st.info("No hay reservas para mostrar")
    
    with tab2:
        st.subheader("Reservas por Cancha")
        canchas = api_request("/canchas")
        if canchas:
            cancha_opciones = ["Todas"] + [f"{c['id']} - {c['nombre']}" for c in canchas]
            cancha_sel = st.selectbox("Seleccionar Cancha", cancha_opciones, key="rep_cancha")
            
            col1, col2 = st.columns(2)
            with col1:
                fecha_desde = st.date_input("Desde", value=datetime.now().date() - timedelta(days=30), key="rep_canc_desde")
            with col2:
                fecha_hasta = st.date_input("Hasta", value=datetime.now().date(), key="rep_canc_hasta")
            
            if cancha_sel != "Todas":
                cancha_id = int(cancha_sel.split(" - ")[0])
                reservas = api_request(f"/reportes/cancha/{cancha_id}?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}")
            else:
                reservas = api_request(f"/reservas?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}")
            
            if reservas:
                df = pd.DataFrame(reservas)
                st.dataframe(df, use_container_width=True)
                
                # Tasa de ocupación
                dias_periodo = (fecha_hasta - fecha_desde).days + 1
                horas_totales = sum([r.get('duracion', 0) for r in reservas])
                horas_disponibles = dias_periodo * 12  # Asumiendo 12 horas disponibles por día
                tasa_ocupacion = (horas_totales / horas_disponibles) * 100 if horas_disponibles > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Reservas", len(reservas))
                with col2:
                    st.metric("Horas Reservadas", f"{horas_totales:.1f}")
                with col3:
                    st.metric("Tasa de Ocupación", f"{tasa_ocupacion:.1f}%")
            else:
                st.info("No hay reservas para mostrar")
    
    with tab3:
        st.subheader("Canchas Más Utilizadas")
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_desde = st.date_input("Desde", value=datetime.now().date() - timedelta(days=30), key="rep_top_desde")
        with col2:
            fecha_hasta = st.date_input("Hasta", value=datetime.now().date(), key="rep_top_hasta")
        
        reservas = api_request(f"/reservas?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}")
        canchas = api_request("/canchas")
        
        if reservas and canchas:
            # Agrupar por cancha
            df = pd.DataFrame(reservas)
            uso_canchas = df.groupby('cancha_id').agg({
                'id': 'count',
                'duracion': 'sum'
            }).reset_index()
            uso_canchas.columns = ['cancha_id', 'cantidad_reservas', 'horas_totales']
            
            # Agregar nombres de canchas
            cancha_dict = {c['id']: c['nombre'] for c in canchas}
            uso_canchas['nombre_cancha'] = uso_canchas['cancha_id'].map(cancha_dict)
            
            # Ordenar por cantidad de reservas
            uso_canchas = uso_canchas.sort_values('cantidad_reservas', ascending=False)
            
            # Mostrar tabla
            st.dataframe(uso_canchas[['nombre_cancha', 'cantidad_reservas', 'horas_totales']], use_container_width=True)
            
            # Gráfico de barras
            fig = px.bar(uso_canchas, x='nombre_cancha', y='cantidad_reservas',
                        title='Cantidad de Reservas por Cancha',
                        labels={'nombre_cancha': 'Cancha', 'cantidad_reservas': 'Cantidad de Reservas'},
                        color='cantidad_reservas',
                        color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de torta
            fig_pie = px.pie(uso_canchas, values='horas_totales', names='nombre_cancha',
                            title='Distribución de Horas Reservadas por Cancha')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay datos suficientes para generar el reporte")
    
    with tab4:
        st.subheader("Utilización Mensual de Canchas")
        
        año = st.selectbox("Año", [2024, 2025, 2026], index=1)
        
        reservas = api_request(f"/reservas?año={año}")
        
        if reservas:
            df = pd.DataFrame(reservas)
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['mes'] = df['fecha'].dt.month
            df['mes_nombre'] = df['fecha'].dt.strftime('%B')
            
            # Agrupar por mes
            uso_mensual = df.groupby(['mes', 'mes_nombre']).agg({
                'id': 'count',
                'duracion': 'sum'
            }).reset_index()
            uso_mensual.columns = ['mes', 'mes_nombre', 'cantidad_reservas', 'horas_totales']
            
            # Gráfico de líneas
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=uso_mensual['mes_nombre'], y=uso_mensual['cantidad_reservas'],
                                    mode='lines+markers', name='Cantidad de Reservas',
                                    line=dict(color='#1E88E5', width=3)))
            fig.update_layout(title=f'Evolución de Reservas - Año {año}',
                            xaxis_title='Mes',
                            yaxis_title='Cantidad de Reservas',
                            hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de barras para horas
            fig_bar = px.bar(uso_mensual, x='mes_nombre', y='horas_totales',
                            title=f'Horas Totales Reservadas por Mes - Año {año}',
                            labels={'mes_nombre': 'Mes', 'horas_totales': 'Horas Totales'},
                            color='horas_totales',
                            color_continuous_scale='Viridis')
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Métricas generales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Reservas Año", df['id'].count())
            with col2:
                st.metric("Total Horas", f"{df['duracion'].sum():.1f}")
            with col3:
                promedio_mes = df['id'].count() / 12
                st.metric("Promedio Mensual", f"{promedio_mes:.0f}")
            with col4:
                if 'precio_total' in df.columns:
                    st.metric("Ingresos Anuales", f"${df['precio_total'].sum():,.0f}")
        else:
            st.info("No hay datos para el año seleccionado")

# ===================== SECCIÓN: TORNEOS =====================

def seccion_torneos():
    st.header("🏆 Gestión de Torneos y Campeonatos")
    
    tab1, tab2, tab3 = st.tabs(["Ver Torneos", "Crear Torneo", "Gestionar Torneos"])
    
    with tab1:
        st.subheader("Torneos Activos")
        torneos = api_request("/torneos")
        if torneos:
            for torneo in torneos:
                with st.expander(f"🏆 {torneo['nombre']} - {torneo.get('deporte', 'N/A')}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Fecha Inicio:** {torneo.get('fecha_inicio', 'N/A')}")
                        st.write(f"**Fecha Fin:** {torneo.get('fecha_fin', 'N/A')}")
                    with col2:
                        st.write(f"**Equipos:** {torneo.get('num_equipos', 0)}")
                        st.write(f"**Estado:** {torneo.get('estado', 'N/A')}")
                    with col3:
                        st.write(f"**Cancha:** {torneo.get('cancha_id', 'N/A')}")
                        st.write(f"**Premio:** ${torneo.get('premio', 0):,.0f}")
                    
                    if torneo.get('descripcion'):
                        st.write(f"**Descripción:** {torneo['descripcion']}")
        else:
            st.info("No hay torneos registrados")
    
    with tab2:
        st.subheader("Crear Nuevo Torneo")
        canchas = api_request("/canchas")
        
        if not canchas:
            st.warning("⚠️ No hay canchas disponibles. Registre una cancha primero.")
        else:
            with st.form("form_torneo"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nombre = st.text_input("Nombre del Torneo*")
                    deporte = st.selectbox("Deporte*", 
                        ["Fútbol 5", "Fútbol 7", "Fútbol 11", "Tenis", "Paddle", "Basquet", "Volley"])
                    fecha_inicio = st.date_input("Fecha Inicio*", min_value=datetime.now().date())
                
                with col2:
                    cancha_opciones = [f"{c['id']} - {c['nombre']}" for c in canchas if c.get('activa', True)]
                    cancha_sel = st.selectbox("Cancha Principal*", cancha_opciones)
                    num_equipos = st.number_input("Número de Equipos*", min_value=2, value=8)
                    fecha_fin = st.date_input("Fecha Fin*", min_value=datetime.now().date())
                
                col3, col4 = st.columns(2)
                with col3:
                    premio = st.number_input("Premio ($)", min_value=0.0, value=0.0, step=1000.0)
                with col4:
                    inscripcion = st.number_input("Costo Inscripción ($)", min_value=0.0, value=0.0, step=500.0)
                
                descripcion = st.text_area("Descripción del Torneo")
                
                submitted = st.form_submit_button("Crear Torneo", use_container_width=True)
                
                if submitted:
                    if nombre and deporte and cancha_sel:
                        cancha_id = int(cancha_sel.split(" - ")[0])
                        
                        data = {
                            "nombre": nombre,
                            "deporte": deporte,
                            "cancha_id": cancha_id,
                            "fecha_inicio": str(fecha_inicio),
                            "fecha_fin": str(fecha_fin),
                            "num_equipos": num_equipos,
                            "premio": premio,
                            "inscripcion": inscripcion,
                            "descripcion": descripcion,
                            "estado": "Inscripción Abierta"
                        }
                        
                        resultado = api_request("/torneos", "POST", data)
                        if resultado:
                            st.success("✅ Torneo creado exitosamente!")
                            st.rerun()
                    else:
                        st.error("⚠️ Complete los campos obligatorios")
    
    with tab3:
        st.subheader("Administrar Torneos")
        torneos = api_request("/torneos")
        if torneos:
            torneo_opciones = [f"{t['id']} - {t['nombre']}" for t in torneos]
            torneo_sel = st.selectbox("Seleccionar Torneo", torneo_opciones)
            
            if torneo_sel:
                torneo_id = int(torneo_sel.split(" - ")[0])
                torneo = next((t for t in torneos if t['id'] == torneo_id), None)
                
                if torneo:
                    # Información del torneo
                    st.write("### Información del Torneo")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Nombre:** {torneo['nombre']}")
                        st.write(f"**Deporte:** {torneo.get('deporte', 'N/A')}")
                    with col2:
                        st.write(f"**Fechas:** {torneo.get('fecha_inicio')} - {torneo.get('fecha_fin')}")
                        st.write(f"**Equipos:** {torneo.get('num_equipos', 0)}")
                    with col3:
                        st.write(f"**Estado:** {torneo.get('estado', 'N/A')}")
                        st.write(f"**Premio:** ${torneo.get('premio', 0):,.0f}")
                    
                    st.write("---")
                    
                    # Acciones
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        nuevo_estado = st.selectbox("Cambiar Estado", 
                            ["Inscripción Abierta", "En Curso", "Finalizado", "Cancelado"])
                        if st.button("Actualizar Estado", use_container_width=True):
                            data = {"estado": nuevo_estado}
                            resultado = api_request(f"/torneos/{torneo_id}", "PUT", data)
                            if resultado:
                                st.success("✅ Estado actualizado!")
                                st.rerun()
                    
                    with col_btn2:
                        if st.button("Ver Fixture/Calendario", use_container_width=True):
                            st.info("Funcionalidad de fixture en desarrollo")
                    
                    with col_btn3:
                        if st.button("Eliminar Torneo", type="secondary", use_container_width=True):
                            resultado = api_request(f"/torneos/{torneo_id}", "DELETE")
                            if resultado:
                                st.success("✅ Torneo eliminado!")
                                st.rerun()

# ===================== SECCIÓN: PAGOS =====================

def seccion_pagos():
    st.header("💳 Administración de Pagos")
    
    tab1, tab2, tab3 = st.tabs(["Ver Pagos", "Registrar Pago", "Reportes de Pagos"])
    
    with tab1:
        st.subheader("Historial de Pagos")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha_desde = st.date_input("Desde", value=datetime.now().date() - timedelta(days=30), key="pag_desde")
        with col2:
            fecha_hasta = st.date_input("Hasta", value=datetime.now().date(), key="pag_hasta")
        with col3:
            estado_pago = st.selectbox("Estado", ["Todos", "Pagado", "Pendiente", "Cancelado"])
        
        pagos = api_request(f"/pagos?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}")
        
        if pagos:
            if estado_pago != "Todos":
                pagos = [p for p in pagos if p.get('estado', '') == estado_pago]
            
            df = pd.DataFrame(pagos)
            st.dataframe(df, use_container_width=True)
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Pagos", len(pagos))
            with col2:
                total_pagado = sum([p.get('monto', 0) for p in pagos if p.get('estado') == 'Pagado'])
                st.metric("Total Pagado", f"${total_pagado:,.0f}")
            with col3:
                total_pendiente = sum([p.get('monto', 0) for p in pagos if p.get('estado') == 'Pendiente'])
                st.metric("Total Pendiente", f"${total_pendiente:,.0f}")
            with col4:
                if len(pagos) > 0:
                    tasa_pago = (len([p for p in pagos if p.get('estado') == 'Pagado']) / len(pagos)) * 100
                    st.metric("Tasa de Pago", f"{tasa_pago:.1f}%")
        else:
            st.info("No hay pagos registrados en el período seleccionado")
    
    with tab2:
        st.subheader("Registrar Nuevo Pago")
        
        reservas = api_request("/reservas")
        if not reservas:
            st.warning("⚠️ No hay reservas disponibles para registrar pagos")
        else:
            # Filtrar reservas sin pago o con pago pendiente
            reservas_sin_pago = [r for r in reservas if r.get('estado_pago', 'Pendiente') != 'Pagado']
            
            if not reservas_sin_pago:
                st.info("Todas las reservas tienen sus pagos registrados")
            else:
                with st.form("form_pago"):
                    reserva_opciones = [f"Reserva #{r['id']} - Cliente {r['cliente_id']} - {r['fecha']}" for r in reservas_sin_pago]
                    reserva_sel = st.selectbox("Seleccionar Reserva*", reserva_opciones)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        monto = st.number_input("Monto ($)*", min_value=0.0, step=100.0)
                        metodo_pago = st.selectbox("Método de Pago*", 
                            ["Efectivo", "Transferencia", "Tarjeta de Crédito", "Tarjeta de Débito", "MercadoPago"])
                    
                    with col2:
                        fecha_pago = st.date_input("Fecha de Pago*", value=datetime.now().date())
                        estado = st.selectbox("Estado*", ["Pagado", "Pendiente"])
                    
                    referencia = st.text_input("Referencia/Comprobante")
                    observaciones = st.text_area("Observaciones")
                    
                    submitted = st.form_submit_button("Registrar Pago", use_container_width=True)
                    
                    if submitted:
                        if monto > 0:
                            reserva_id = int(reserva_sel.split("#")[1].split(" ")[0])
                            
                            data = {
                                "reserva_id": reserva_id,
                                "monto": monto,
                                "metodo_pago": metodo_pago,
                                "fecha_pago": str(fecha_pago),
                                "estado": estado,
                                "referencia": referencia,
                                "observaciones": observaciones
                            }
                            
                            resultado = api_request("/pagos", "POST", data)
                            if resultado:
                                st.success("✅ Pago registrado exitosamente!")
                                st.rerun()
                        else:
                            st.error("⚠️ El monto debe ser mayor a 0")
    
    with tab3:
        st.subheader("Reportes de Pagos")
        
        año = st.selectbox("Seleccionar Año", [2024, 2025, 2026], index=1, key="pag_año")
        mes = st.selectbox("Seleccionar Mes (opcional)", 
            ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        
        pagos = api_request(f"/pagos?año={año}")
        
        if pagos:
            df = pd.DataFrame(pagos)
            df['fecha_pago'] = pd.to_datetime(df['fecha_pago'])
            
            # Filtrar por mes si no es "Todos"
            if mes != "Todos":
                mes_num = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"].index(mes) + 1
                df = df[df['fecha_pago'].dt.month == mes_num]
            
            # Gráfico de ingresos por método de pago
            if not df.empty:
                ingresos_metodo = df[df['estado'] == 'Pagado'].groupby('metodo_pago')['monto'].sum().reset_index()
                fig_metodo = px.pie(ingresos_metodo, values='monto', names='metodo_pago',
                                   title='Ingresos por Método de Pago')
                st.plotly_chart(fig_metodo, use_container_width=True)
                
                # Gráfico de evolución de ingresos
                df['mes'] = df['fecha_pago'].dt.to_period('M')
                ingresos_mes = df[df['estado'] == 'Pagado'].groupby('mes')['monto'].sum().reset_index()
                ingresos_mes['mes'] = ingresos_mes['mes'].astype(str)
                
                fig_evolucion = px.line(ingresos_mes, x='mes', y='monto',
                                       title='Evolución de Ingresos',
                                       labels={'mes': 'Mes', 'monto': 'Ingresos ($)'},
                                       markers=True)
                st.plotly_chart(fig_evolucion, use_container_width=True)
                
                # Métricas del período
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_ingresos = df[df['estado'] == 'Pagado']['monto'].sum()
                    st.metric("Ingresos del Período", f"${total_ingresos:,.0f}")
                with col2:
                    pendientes = df[df['estado'] == 'Pendiente']['monto'].sum()
                    st.metric("Pagos Pendientes", f"${pendientes:,.0f}")
                with col3:
                    total_transacciones = len(df[df['estado'] == 'Pagado'])
                    st.metric("Total Transacciones", total_transacciones)
            else:
                st.info("No hay datos para el período seleccionado")
        else:
            st.info("No hay pagos registrados para el año seleccionado")

# ===================== SECCIÓN: DASHBOARD =====================

def seccion_dashboard():
    st.markdown("<h1 class='main-header'>🏟️ Dashboard - Sistema de Reservas</h1>", unsafe_allow_html=True)
    
    # Métricas principales
    st.subheader("📊 Métricas del Día")
    
    hoy = datetime.now().date()
    reservas_hoy = api_request(f"/reservas?fecha={hoy}")
    clientes = api_request("/clientes")
    canchas = api_request("/canchas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        num_reservas = len(reservas_hoy) if reservas_hoy else 0
        st.metric("Reservas Hoy", num_reservas, delta=None)
    
    with col2:
        num_clientes = len(clientes) if clientes else 0
        st.metric("Clientes Totales", num_clientes)
    
    with col3:
        num_canchas = len([c for c in canchas if c.get('activa', True)]) if canchas else 0
        st.metric("Canchas Activas", num_canchas)
    
    with col4:
        if reservas_hoy:
            ingresos_hoy = sum([r.get('precio_total', 0) for r in reservas_hoy])
            st.metric("Ingresos Hoy", f"${ingresos_hoy:,.0f}")
        else:
            st.metric("Ingresos Hoy", "$0")
    
    st.write("---")
    
    # Próximas reservas
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📅 Próximas Reservas")
        if reservas_hoy:
            df_hoy = pd.DataFrame(reservas_hoy)
            df_hoy = df_hoy.sort_values('hora_inicio')
            st.dataframe(df_hoy[['id', 'cancha_id', 'hora_inicio', 'hora_fin', 'estado']].head(10), 
                        use_container_width=True, hide_index=True)
        else:
            st.info("No hay reservas para hoy")
    
    with col_right:
        st.subheader("🎯 Acciones Rápidas")
        if st.button("➕ Nueva Reserva", use_container_width=True):
            st.session_state['pagina'] = 'reservas'
            st.rerun()
        
        if st.button("👥 Nuevo Cliente", use_container_width=True):
            st.session_state['pagina'] = 'clientes'
            st.rerun()
        
        if st.button("🏟️ Nueva Cancha", use_container_width=True):
            st.session_state['pagina'] = 'canchas'
            st.rerun()
        
        if st.button("📊 Ver Reportes", use_container_width=True):
            st.session_state['pagina'] = 'reportes'
            st.rerun()
    
    st.write("---")
    
    # Gráfico de ocupación semanal
    st.subheader("📈 Ocupación Semanal")
    fecha_inicio_semana = hoy - timedelta(days=hoy.weekday())
    fecha_fin_semana = fecha_inicio_semana + timedelta(days=6)
    
    reservas_semana = api_request(f"/reservas?fecha_desde={fecha_inicio_semana}&fecha_hasta={fecha_fin_semana}")
    
    if reservas_semana:
        df_semana = pd.DataFrame(reservas_semana)
        df_semana['fecha'] = pd.to_datetime(df_semana['fecha'])
        df_semana['dia_semana'] = df_semana['fecha'].dt.day_name()
        
        ocupacion_dia = df_semana.groupby('dia_semana').agg({
            'id': 'count',
            'duracion': 'sum'
        }).reset_index()
        ocupacion_dia.columns = ['dia', 'reservas', 'horas']
        
        # Ordenar días de la semana
        dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_español = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        ocupacion_dia['dia'] = pd.Categorical(ocupacion_dia['dia'], categories=dias_orden, ordered=True)
        ocupacion_dia = ocupacion_dia.sort_values('dia')
        ocupacion_dia['dia'] = dias_español[:len(ocupacion_dia)]
        
        fig = px.bar(ocupacion_dia, x='dia', y='reservas',
                    title='Reservas por Día de la Semana',
                    labels={'dia': 'Día', 'reservas': 'Cantidad de Reservas'},
                    color='reservas',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de reservas para esta semana")

# ===================== MENÚ PRINCIPAL =====================

def main():
    # Inicializar estado de sesión
    if 'pagina' not in st.session_state:
        st.session_state['pagina'] = 'dashboard'
    
    # Sidebar con navegación
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1E88E5/FFFFFF?text=Canchas+AR", use_container_width=True)
        st.title("Menú Principal")
        
        paginas = {
            'Dashboard': 'dashboard',
            'Clientes': 'clientes',
            'Canchas': 'canchas',
            'Reservas': 'reservas',
            'Torneos': 'torneos',
            'Pagos': 'pagos',
            'Reportes': 'reportes'
        }
        
        for nombre, clave in paginas.items():
            if st.button(f"{'📊' if clave == 'dashboard' else '👥' if clave == 'clientes' else '🏟️' if clave == 'canchas' else '📅' if clave == 'reservas' else '🏆' if clave == 'torneos' else '💳' if clave == 'pagos' else '📈'} {nombre}", 
                        use_container_width=True,
                        type="primary" if st.session_state['pagina'] == clave else "secondary"):
                st.session_state['pagina'] = clave
                st.rerun()
        
        st.write("---")
        st.caption(f"🔌 Backend: {API_BASE_URL}")
        st.caption(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        st.caption("⚽ Sistema de Reservas v1.0")
    
    # Renderizar página seleccionada
    if st.session_state['pagina'] == 'dashboard':
        seccion_dashboard()
    elif st.session_state['pagina'] == 'clientes':
        seccion_clientes()
    elif st.session_state['pagina'] == 'canchas':
        seccion_canchas()
    elif st.session_state['pagina'] == 'reservas':
        seccion_reservas()
    elif st.session_state['pagina'] == 'torneos':
        seccion_torneos()
    elif st.session_state['pagina'] == 'pagos':
        seccion_pagos()
    elif st.session_state['pagina'] == 'reportes':
        seccion_reportes()

if __name__ == "__main__":
    main()