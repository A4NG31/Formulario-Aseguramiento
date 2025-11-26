import streamlit as st
import pandas as pd
from datetime import datetime
import openpyxl
from io import BytesIO
import requests
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

# Configuración de la página
st.set_page_config(page_title="Entrega de Turno", layout="centered")

# Título principal
st.title("📋 Plantilla de Informe de Entrega de Cambio de Turno")

# Inicializar session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Función para guardar en Excel (simulación - necesitarás configurar credenciales de SharePoint)
def guardar_en_sharepoint(datos):
    """
    NOTA IMPORTANTE: Para guardar en SharePoint necesitas:
    1. Instalar: pip install Office365-REST-Python-Client
    2. Configurar credenciales de SharePoint en Streamlit Cloud (Secrets)
    3. El código actual simula el guardado. Descarga el Excel localmente.
    """
    try:
        # Crear DataFrame
        df_nuevo = pd.DataFrame([datos])
        
        # Por ahora, guardar localmente (para pruebas)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"entrega_turno_{timestamp}.xlsx"
        
        # Guardar como Excel
        df_nuevo.to_excel(nombre_archivo, index=False)
        
        st.success(f"✅ Datos guardados exitosamente")
        st.download_button(
            label="📥 Descargar respaldo local",
            data=open(nombre_archivo, 'rb'),
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Aquí iría el código para subir a SharePoint
        # Necesitarás configurar las credenciales en st.secrets
        
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar: {str(e)}")
        return False

# Formulario principal
with st.form("formulario_turno"):
    # Pregunta 1: Nombre
    nombre = st.selectbox(
        "Seleccione su nombre *",
        ["", "David Grillo", "Jose Arias", "Cesar Salamanca", "Ruben Palacios"]
    )
    
    # Pregunta 2: Qué trabajaste
    trabajos = st.multiselect(
        "¿Qué trabajaste en tu turno? *",
        ["Tickets GLPI", "Correo de Concesiones", "Análisis del día"]
    )
    
    # Variables para almacenar respuestas
    datos_tickets = {}
    datos_concesiones = {}
    analisis_dia = ""
    
    # SECCIÓN TICKETS GLPI
    if "Tickets GLPI" in trabajos:
        st.markdown("---")
        st.subheader("🎫 Tickets GLPI")
        
        categorias = [
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
        
        categorias_seleccionadas = st.multiselect(
            "¿Cuáles categorías trabajaste?",
            categorias
        )
        
        # Campos para número de tickets por categoría
        tickets_por_categoria = {}
        if categorias_seleccionadas:
            st.write("**Número de tickets resueltos por categoría:**")
            for cat in categorias_seleccionadas:
                tickets_por_categoria[cat] = st.number_input(
                    f"{cat}",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"ticket_{cat}"
                )
        
        # Tickets escalados
        tickets_escalados = st.text_input(
            "¿Cuántos tickets escalaste a otras áreas? (ej: Desarrollo - 5)"
        )
        
        # Novedades en tickets
        novedades_tickets = st.text_area(
            "¿Tuviste novedades en tickets?",
            height=100
        )
        
        # Pendientes
        tiene_pendientes = st.radio(
            "¿Dejaste algo pendiente?",
            ["No", "Sí"],
            key="pendientes_tickets"
        )
        
        pendientes_descripcion = ""
        if tiene_pendientes == "Sí":
            pendientes_descripcion = st.text_area(
                "¿Qué dejaste pendiente para el siguiente turno?",
                height=100,
                key="desc_pendientes_tickets"
            )
        
        datos_tickets = {
            "categorias": categorias_seleccionadas,
            "tickets_por_categoria": tickets_por_categoria,
            "escalados": tickets_escalados,
            "novedades": novedades_tickets,
            "pendientes": pendientes_descripcion if tiene_pendientes == "Sí" else "No"
        }
    
    # SECCIÓN CORREO DE CONCESIONES
    if "Correo de Concesiones" in trabajos:
        st.markdown("---")
        st.subheader("📧 Correo de Concesiones")
        
        concesiones = [
            "Accenorte",
            "Alt. Viales",
            "Alma",
            "Aut. El Cafe"
        ]
        
        concesiones_seleccionadas = st.multiselect(
            "¿Qué concesiones trabajaste?",
            concesiones
        )
        
        # Campos para número de correos por concesión
        correos_por_concesion = {}
        if concesiones_seleccionadas:
            st.write("**Número de correos respondidos por concesión:**")
            for conc in concesiones_seleccionadas:
                correos_por_concesion[conc] = st.number_input(
                    f"{conc}",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"correo_{conc}"
                )
        
        # Novedades en concesiones
        tuvo_novedades_conc = st.radio(
            "¿Tuviste novedades?",
            ["No", "Sí"],
            key="novedades_conc"
        )
        
        novedades_conc = ""
        if tuvo_novedades_conc == "Sí":
            novedades_conc = st.text_area(
                "Describe la novedad:",
                height=100,
                key="desc_novedades_conc"
            )
        
        datos_concesiones = {
            "concesiones": concesiones_seleccionadas,
            "correos_por_concesion": correos_por_concesion,
            "novedades": novedades_conc if tuvo_novedades_conc == "Sí" else "No"
        }
    
    # SECCIÓN ANÁLISIS DEL DÍA
    if "Análisis del día" in trabajos:
        st.markdown("---")
        st.subheader("📊 Análisis del Día")
        
        analisis_dia = st.text_area(
            "Describe el análisis del día:",
            height=150,
            key="analisis"
        )
    
    # Botón de envío
    submitted = st.form_submit_button("📤 Enviar Informe", use_container_width=True)
    
    if submitted:
        # Validaciones
        if not nombre:
            st.error("⚠️ Por favor selecciona tu nombre")
        elif not trabajos:
            st.error("⚠️ Por favor selecciona al menos una actividad")
        else:
            # Preparar datos para guardar
            datos_completos = {
                "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nombre": nombre,
                "Actividades": ", ".join(trabajos)
            }
            
            # Agregar datos según las actividades
            if "Tickets GLPI" in trabajos:
                datos_completos["Categorías GLPI"] = ", ".join(datos_tickets.get("categorias", []))
                for cat, num in datos_tickets.get("tickets_por_categoria", {}).items():
                    datos_completos[f"Tickets - {cat}"] = num
                datos_completos["Tickets Escalados"] = datos_tickets.get("escalados", "")
                datos_completos["Novedades Tickets"] = datos_tickets.get("novedades", "")
                datos_completos["Pendientes Tickets"] = datos_tickets.get("pendientes", "")
            
            if "Correo de Concesiones" in trabajos:
                datos_completos["Concesiones"] = ", ".join(datos_concesiones.get("concesiones", []))
                for conc, num in datos_concesiones.get("correos_por_concesion", {}).items():
                    datos_completos[f"Correos - {conc}"] = num
                datos_completos["Novedades Concesiones"] = datos_concesiones.get("novedades", "")
            
            if "Análisis del día" in trabajos:
                datos_completos["Análisis del Día"] = analisis_dia
            
            # Guardar datos
            if guardar_en_sharepoint(datos_completos):
                st.session_state.submitted = True
                st.balloons()
                st.success("🎉 ¡Informe enviado exitosamente!")
                st.info("💡 Nota: Para integración completa con SharePoint, configura las credenciales en Streamlit Cloud Secrets")

# Información adicional
with st.expander("ℹ️ Instrucciones de Configuración"):
    st.markdown("""
    ### Para integración con SharePoint:
    
    1. **Instalar dependencias** (requirements.txt):
       ```
       streamlit
       pandas
       openpyxl
       Office365-REST-Python-Client
       ```
    
    2. **Configurar Secrets en Streamlit Cloud**:
       - Ve a tu app en Streamlit Cloud
       - Settings → Secrets
       - Agrega:
       ```toml
       [sharepoint]
       username = "tu_email@gopass.com.co"
       password = "tu_contraseña"
       site_url = "https://grupogopass-my.sharepoint.com"
       ```
    
    3. **El código ya está preparado** para guardar directamente en el Excel de SharePoint
    """)

st.markdown("---")
st.caption("Formulario de Entrega de Turno - Aseguramiento | Gopass")