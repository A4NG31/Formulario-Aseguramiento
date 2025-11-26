import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(page_title="Entrega de Turno", layout="centered")

# Título principal
st.title("📋 Plantilla de Informe de Entrega de Cambio de Turno")

# Inicializar session state
if 'paso' not in st.session_state:
    st.session_state.paso = 1
if 'nombre' not in st.session_state:
    st.session_state.nombre = ""
if 'actividades' not in st.session_state:
    st.session_state.actividades = []
if 'categorias_seleccionadas' not in st.session_state:
    st.session_state.categorias_seleccionadas = []
if 'tickets_por_categoria' not in st.session_state:
    st.session_state.tickets_por_categoria = {}
if 'escalados' not in st.session_state:
    st.session_state.escalados = ""
if 'novedades' not in st.session_state:
    st.session_state.novedades = ""
if 'tiene_pendientes' not in st.session_state:
    st.session_state.tiene_pendientes = "No"

# Función para guardar en Excel
def guardar_datos(datos):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"entrega_turno_{timestamp}.xlsx"
        
        df_nuevo = pd.DataFrame([datos])
        df_nuevo.to_excel(nombre_archivo, index=False)
        
        st.success("✅ Datos guardados exitosamente")
        st.download_button(
            label="📥 Descargar respaldo",
            data=open(nombre_archivo, 'rb'),
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        return True
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

# PASO 1: Selección de nombre
if st.session_state.paso == 1:
    with st.form("form_nombre"):
        nombre = st.selectbox(
            "Seleccione su nombre *",
            ["", "David Grillo", "Jose Arias", "Cesar Salamanca", "Ruben Palacios"]
        )
        
        submit_nombre = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if submit_nombre:
            if not nombre:
                st.error("⚠️ Por favor selecciona tu nombre")
            else:
                st.session_state.nombre = nombre
                st.session_state.paso = 2
                st.rerun()

# PASO 2: Selección de actividades
elif st.session_state.paso == 2:
    st.info(f"👤 Usuario: **{st.session_state.nombre}**")
    
    with st.form("form_actividades"):
        actividades = st.multiselect(
            "¿Qué trabajaste en tu turno? *",
            ["Tickets GLPI", "Correo de Concesiones", "Análisis del día"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            siguiente = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if atras:
            st.session_state.paso = 1
            st.rerun()
        
        if siguiente:
            if not actividades:
                st.error("⚠️ Selecciona al menos una actividad")
            else:
                st.session_state.actividades = actividades
                # Determinar a qué paso ir según la primera actividad
                if "Tickets GLPI" in actividades:
                    st.session_state.paso = 3
                elif "Correo de Concesiones" in actividades:
                    st.session_state.paso = 4
                elif "Análisis del día" in actividades:
                    st.session_state.paso = 5
                st.rerun()

# PASO 3: TICKETS GLPI - Selección de categorías
elif st.session_state.paso == 3:
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 🎫 Tickets GLPI")
    
    categorias_opciones = [
        "Novedades en transacciones SOUL-Aseguramiento",
        "Error de transacción",
        "Actualización de Datos",
        "Novedades de facturación",
        "Revisión transacción",
        "Cambio de transacción",
        "Falla Aprovisionamiento",
        "Activación Servicios",
        "Falla del servicio",
        "Usuario Inactivo",
        "Doble Cobro",
        "Actualización estado de cuenta",
        "Desconoce transacción",
        "Novedades NC y ND",
        "Devolución de saldo",
        "Falla App",
        "Envío de facturas",
        "Agendamiento",
        "Novedades facturación",
        "Novedades en la factura",
        "Aclaración correcto",
        "Uso del Servicio Gopass",
        "Novedad en Transacciones",
        "Inconsistencia en Mensualidad",
        "Revisión Inhibición"
    ]
    
    with st.form("form_categorias"):
        categorias = st.multiselect(
            "¿Cuáles categorías trabajaste?",
            categorias_opciones,
            default=st.session_state.categorias_seleccionadas
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            siguiente = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if atras:
            st.session_state.paso = 2
            st.rerun()
        
        if siguiente:
            if not categorias:
                st.error("⚠️ Selecciona al menos una categoría")
            else:
                st.session_state.categorias_seleccionadas = categorias
                st.session_state.paso = 3.1
                st.rerun()

# PASO 3.1: TICKETS GLPI - Número de tickets por categoría
elif st.session_state.paso == 3.1:
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 🎫 Tickets GLPI")
    
    with st.form("form_num_tickets"):
        st.markdown("**Número de tickets resueltos por categoría:**")
        tickets_dict = {}
        for cat in st.session_state.categorias_seleccionadas:
            valor_default = st.session_state.tickets_por_categoria.get(cat, 0)
            tickets_dict[cat] = st.number_input(
                cat,
                min_value=0,
                value=valor_default,
                step=1,
                key=f"ticket_{cat}"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            siguiente = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if atras:
            st.session_state.paso = 3
            st.rerun()
        
        if siguiente:
            st.session_state.tickets_por_categoria = tickets_dict
            st.session_state.paso = 3.2
            st.rerun()

# PASO 3.2: TICKETS GLPI - Escalados y novedades
elif st.session_state.paso == 3.2:
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 🎫 Tickets GLPI")
    
    with st.form("form_escalados"):
        escalados = st.text_input(
            "¿Cuántos tickets escalaste a otras áreas? (ej: Desarrollo - 5)",
            value=st.session_state.escalados
        )
        
        novedades = st.text_area(
            "¿Tuviste novedades en tickets?",
            value=st.session_state.novedades,
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            siguiente = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if atras:
            st.session_state.paso = 3.1
            st.rerun()
        
        if siguiente:
            st.session_state.escalados = escalados
            st.session_state.novedades = novedades
            st.session_state.paso = 3.3
            st.rerun()

# PASO 3.3: TICKETS GLPI - Pendientes
elif st.session_state.paso == 3.3:
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 🎫 Tickets GLPI")
    
    with st.form("form_pendientes"):
        pendientes = st.radio(
            "¿Dejaste algo pendiente?",
            ["No", "Sí"],
            index=0 if st.session_state.tiene_pendientes == "No" else 1
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            siguiente = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if atras:
            st.session_state.paso = 3.2
            st.rerun()
        
        if siguiente:
            st.session_state.tiene_pendientes = pendientes
            if pendientes == "Sí":
                st.session_state.paso = 3.4
            else:
                st.session_state.paso = 3.5
            st.rerun()

# PASO 3.4: TICKETS GLPI - Descripción de pendientes
elif st.session_state.paso == 3.4:
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 🎫 Tickets GLPI")
    
    with st.form("form_desc_pendientes"):
        desc_pendientes = st.text_area(
            "¿Qué dejaste pendiente para el siguiente turno?",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            enviar = st.form_submit_button("📤 Enviar", use_container_width=True)
        
        if atras:
            st.session_state.paso = 3.3
            st.rerun()
        
        if enviar:
            if not desc_pendientes.strip():
                st.error("⚠️ Por favor describe lo que dejaste pendiente")
            else:
                datos = {
                    "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Nombre": st.session_state.nombre,
                    "Actividad": "Tickets GLPI",
                    "Categorías": ", ".join(st.session_state.categorias_seleccionadas),
                    "Tickets Escalados": st.session_state.escalados,
                    "Novedades": st.session_state.novedades,
                    "Pendientes": desc_pendientes
                }
                
                for cat, num in st.session_state.tickets_por_categoria.items():
                    datos[f"Tickets - {cat}"] = num
                
                if guardar_datos(datos):
                    st.balloons()
                    if st.button("✅ Hacer otro envío"):
                        st.session_state.paso = 1
                        st.session_state.nombre = ""
                        st.session_state.actividades = []
                        st.session_state.categorias_seleccionadas = []
                        st.session_state.tickets_por_categoria = {}
                        st.session_state.escalados = ""
                        st.session_state.novedades = ""
                        st.session_state.tiene_pendientes = "No"
                        st.rerun()

# PASO 3.5: TICKETS GLPI - Envío final (sin pendientes)
elif st.session_state.paso == 3.5:
    datos = {
        "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Nombre": st.session_state.nombre,
        "Actividad": "Tickets GLPI",
        "Categorías": ", ".join(st.session_state.categorias_seleccionadas),
        "Tickets Escalados": st.session_state.escalados,
        "Novedades": st.session_state.novedades,
        "Pendientes": "No"
    }
    
    for cat, num in st.session_state.tickets_por_categoria.items():
        datos[f"Tickets - {cat}"] = num
    
    if guardar_datos(datos):
        st.balloons()
        if st.button("✅ Hacer otro envío"):
            st.session_state.paso = 1
            st.session_state.nombre = ""
            st.session_state.actividades = []
            st.session_state.categorias_seleccionadas = []
            st.session_state.tickets_por_categoria = {}
            st.session_state.escalados = ""
            st.session_state.novedades = ""
            st.session_state.tiene_pendientes = "No"
            st.rerun()

# PASO 4: Formulario CORREO DE CONCESIONES
elif st.session_state.paso == 4:
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Correo de Concesiones")
    
    concesiones_opciones = [
        "Accenorte",
        "Alt. Viales",
        "Alma",
        "Aut. El Cafe"
    ]
    
    with st.form("form_concesiones"):
        concesiones = st.multiselect(
            "¿Qué concesiones trabajaste?",
            concesiones_opciones
        )
        
        correos_por_concesion = {}
        if concesiones:
            st.markdown("**Número de correos respondidos por concesión:**")
            for conc in concesiones:
                correos_por_concesion[conc] = st.number_input(
                    conc,
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"correo_{conc}"
                )
        
        st.markdown("---")
        tuvo_novedades = st.radio(
            "¿Tuviste novedades?",
            ["No", "Sí"]
        )
        
        desc_novedades = ""
        if tuvo_novedades == "Sí":
            desc_novedades = st.text_area(
                "Describe la novedad:",
                height=100
            )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            enviar = st.form_submit_button("📤 Enviar", use_container_width=True)
        
        if atras:
            st.session_state.paso = 2
            st.rerun()
        
        if enviar:
            datos = {
                "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nombre": st.session_state.nombre,
                "Actividad": "Correo de Concesiones",
                "Concesiones": ", ".join(concesiones) if concesiones else "N/A",
                "Novedades": desc_novedades if tuvo_novedades == "Sí" else "No"
            }
            
            # Agregar correos por concesión
            for conc, num in correos_por_concesion.items():
                datos[f"Correos - {conc}"] = num
            
            if guardar_datos(datos):
                st.balloons()
                if st.button("✅ Hacer otro envío"):
                    st.session_state.paso = 1
                    st.session_state.nombre = ""
                    st.session_state.actividades = []
                    st.rerun()

# PASO 5: Formulario ANÁLISIS DEL DÍA
elif st.session_state.paso == 5:
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📊 Análisis del Día")
    
    with st.form("form_analisis"):
        analisis = st.text_area(
            "Describe el análisis del día:",
            height=200
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            enviar = st.form_submit_button("📤 Enviar", use_container_width=True)
        
        if atras:
            st.session_state.paso = 2
            st.rerun()
        
        if enviar:
            if not analisis.strip():
                st.error("⚠️ Por favor describe el análisis del día")
            else:
                datos = {
                    "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Nombre": st.session_state.nombre,
                    "Actividad": "Análisis del Día",
                    "Análisis": analisis
                }
                
                if guardar_datos(datos):
                    st.balloons()
                    if st.button("✅ Hacer otro envío"):
                        st.session_state.paso = 1
                        st.session_state.nombre = ""
                        st.session_state.actividades = []
                        st.rerun()

# Footer
st.markdown("---")
st.caption("Formulario de Entrega de Turno - Aseguramiento | Gopass")
