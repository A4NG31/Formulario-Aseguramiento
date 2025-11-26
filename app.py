import streamlit as st
import pandas as pd
from datetime import datetime
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from io import BytesIO
import openpyxl

# Configuración de la página
st.set_page_config(page_title="Entrega de Turno", layout="centered")

# Título principal
st.title("📋 Plantilla de Informe de Entrega de Cambio de Turno")

# Inicializar session state
if 'paso' not in st.session_state:
    st.session_state.paso = "1"
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
if 'actividad_actual_index' not in st.session_state:
    st.session_state.actividad_actual_index = 0
if 'datos_guardados' not in st.session_state:
    st.session_state.datos_guardados = []
if 'concesiones_seleccionadas' not in st.session_state:
    st.session_state.concesiones_seleccionadas = []
if 'correos_por_concesion' not in st.session_state:
    st.session_state.correos_por_concesion = {}
if 'tiene_novedades_conc' not in st.session_state:
    st.session_state.tiene_novedades_conc = "No"

# Función para guardar datos
def guardar_datos(datos):
    try:
        st.session_state.datos_guardados.append(datos)
        return True
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

# Función para ir a la siguiente actividad
def ir_siguiente_actividad():
    st.session_state.actividad_actual_index += 1
    
    # Limpiar datos de la actividad anterior
    st.session_state.categorias_seleccionadas = []
    st.session_state.tickets_por_categoria = {}
    st.session_state.escalados = ""
    st.session_state.novedades = ""
    st.session_state.tiene_pendientes = "No"
    st.session_state.concesiones_seleccionadas = []
    st.session_state.correos_por_concesion = {}
    st.session_state.tiene_novedades_conc = "No"
    
    if st.session_state.actividad_actual_index < len(st.session_state.actividades):
        siguiente_actividad = st.session_state.actividades[st.session_state.actividad_actual_index]
        if siguiente_actividad == "Tickets GLPI":
            st.session_state.paso = "3"
        elif siguiente_actividad == "Correo de Concesiones":
            st.session_state.paso = "4"
        elif siguiente_actividad == "Análisis del día":
            st.session_state.paso = "5"
    else:
        st.session_state.paso = "99"
    
    st.rerun()

# Función para exportar
def exportar_todo():
    try:
        # Obtener credenciales de Streamlit secrets
        username = st.secrets["sharepoint"]["username"]
        password = st.secrets["sharepoint"]["password"]
        site_url = st.secrets["sharepoint"]["site_url"]
        
        # Ruta del archivo en SharePoint
        file_url = "/personal/diego_sierra_gopass_com_co/Documents/Book.xlsx"
        
        # Conectar a SharePoint
        ctx = ClientContext(site_url).with_credentials(
            UserCredential(username, password)
        )
        
        # Descargar el archivo existente
        download_path = BytesIO()
        file = ctx.web.get_file_by_server_relative_url(file_url)
        file.download(download_path)
        ctx.execute_query()
        
        # Leer el Excel existente
        download_path.seek(0)
        df_existente = pd.read_excel(download_path)
        
        # Crear DataFrame con los nuevos datos
        df_nuevos = pd.DataFrame(st.session_state.datos_guardados)
        
        # Combinar datos existentes con nuevos
        df_completo = pd.concat([df_existente, df_nuevos], ignore_index=True)
        
        # Guardar en un buffer
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_completo.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)
        
        # Subir el archivo actualizado a SharePoint
        file.upload(output.getvalue())
        ctx.execute_query()
        
        st.success("✅ Datos guardados exitosamente en SharePoint")
        
        # También ofrecer descarga local
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"entrega_turno_{timestamp}.xlsx"
        
        output.seek(0)
        st.download_button(
            label="📥 Descargar respaldo local",
            data=output.getvalue(),
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error al guardar en SharePoint: {str(e)}")
        
        # Fallback: guardar localmente
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"entrega_turno_{timestamp}.xlsx"
            
            df_nuevos = pd.DataFrame(st.session_state.datos_guardados)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_nuevos.to_excel(writer, index=False, sheet_name='Sheet1')
            output.seek(0)
            
            st.warning("⚠️ Guardando localmente por error de conexión")
            st.download_button(
                label="📥 Descargar respaldo local",
                data=output.getvalue(),
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            return True
        except Exception as e2:
            st.error(f"❌ Error al guardar localmente: {str(e2)}")
            return False

# PASO 1: Selección de nombre
if st.session_state.paso == "1":
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
                st.session_state.paso = "2"
                st.rerun()

# PASO 2: Selección de actividades
elif st.session_state.paso == "2":
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
            st.session_state.paso = "1"
            st.rerun()
        
        if siguiente:
            if not actividades:
                st.error("⚠️ Selecciona al menos una actividad")
            else:
                st.session_state.actividades = actividades
                st.session_state.actividad_actual_index = 0
                primera_actividad = actividades[0]
                if primera_actividad == "Tickets GLPI":
                    st.session_state.paso = "3"
                elif primera_actividad == "Correo de Concesiones":
                    st.session_state.paso = "4"
                elif primera_actividad == "Análisis del día":
                    st.session_state.paso = "5"
                st.rerun()

# ========== TICKETS GLPI ==========
# PASO 3: Selección de categorías
elif st.session_state.paso == "3":
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
            st.session_state.paso = "2"
            st.rerun()
        
        if siguiente:
            if not categorias:
                st.error("⚠️ Selecciona al menos una categoría")
            else:
                st.session_state.categorias_seleccionadas = categorias
                st.session_state.paso = "3.1"
                st.rerun()

# PASO 3.1: Número de tickets por categoría
elif st.session_state.paso == "3.1":
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
            st.session_state.paso = "3"
            st.rerun()
        
        if siguiente:
            st.session_state.tickets_por_categoria = tickets_dict
            st.session_state.paso = "3.2"
            st.rerun()

# PASO 3.2: Escalados y novedades
elif st.session_state.paso == "3.2":
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
            st.session_state.paso = "3.1"
            st.rerun()
        
        if siguiente:
            st.session_state.escalados = escalados
            st.session_state.novedades = novedades
            st.session_state.paso = "3.3"
            st.rerun()

# PASO 3.3: Pendientes
elif st.session_state.paso == "3.3":
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
            st.session_state.paso = "3.2"
            st.rerun()
        
        if siguiente:
            st.session_state.tiene_pendientes = pendientes
            if pendientes == "Sí":
                st.session_state.paso = "3.4"
            else:
                st.session_state.paso = "3.5"
            st.rerun()

# PASO 3.4: Descripción de pendientes
elif st.session_state.paso == "3.4":
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
            st.session_state.paso = "3.3"
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
                    ir_siguiente_actividad()

# PASO 3.5: Envío final (sin pendientes)
elif st.session_state.paso == "3.5":
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
        ir_siguiente_actividad()

# ========== CORREO DE CONCESIONES ==========
# PASO 4: Selección de concesiones
elif st.session_state.paso == "4":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Correo de Concesiones")
    
    concesiones_opciones = [
        "Accenorte",
        "Alt. Viales",
        "Alma",
        "Aut. El Cafe"
    ]
    
    with st.form("form_concesiones_select"):
        concesiones = st.multiselect(
            "¿Qué concesiones trabajaste?",
            concesiones_opciones,
            default=st.session_state.concesiones_seleccionadas
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            siguiente = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if atras:
            st.session_state.paso = "2"
            st.rerun()
        
        if siguiente:
            if not concesiones:
                st.error("⚠️ Selecciona al menos una concesión")
            else:
                st.session_state.concesiones_seleccionadas = concesiones
                st.session_state.paso = "4.1"
                st.rerun()

# PASO 4.1: Número de correos por concesión
elif st.session_state.paso == "4.1":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Correo de Concesiones")
    
    with st.form("form_num_correos"):
        st.markdown("**Número de correos respondidos por concesión:**")
        correos_dict = {}
        for conc in st.session_state.concesiones_seleccionadas:
            valor_default = st.session_state.correos_por_concesion.get(conc, 0)
            correos_dict[conc] = st.number_input(
                conc,
                min_value=0,
                value=valor_default,
                step=1,
                key=f"correo_{conc}"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            siguiente = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if atras:
            st.session_state.paso = "4"
            st.rerun()
        
        if siguiente:
            st.session_state.correos_por_concesion = correos_dict
            st.session_state.paso = "4.2"
            st.rerun()

# PASO 4.2: ¿Tuviste novedades?
elif st.session_state.paso == "4.2":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Correo de Concesiones")
    
    with st.form("form_novedades_conc"):
        tuvo_novedades = st.radio(
            "¿Tuviste novedades?",
            ["No", "Sí"],
            index=0 if st.session_state.tiene_novedades_conc == "No" else 1
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            siguiente = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if atras:
            st.session_state.paso = "4.1"
            st.rerun()
        
        if siguiente:
            st.session_state.tiene_novedades_conc = tuvo_novedades
            if tuvo_novedades == "Sí":
                st.session_state.paso = "4.3"
            else:
                st.session_state.paso = "4.4"
            st.rerun()

# PASO 4.3: Descripción de novedades
elif st.session_state.paso == "4.3":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Correo de Concesiones")
    
    with st.form("form_desc_novedades_conc"):
        desc_novedades = st.text_area(
            "¿Qué novedades tuviste?",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            enviar = st.form_submit_button("📤 Enviar", use_container_width=True)
        
        if atras:
            st.session_state.paso = "4.2"
            st.rerun()
        
        if enviar:
            if not desc_novedades.strip():
                st.error("⚠️ Por favor describe las novedades")
            else:
                datos = {
                    "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Nombre": st.session_state.nombre,
                    "Actividad": "Correo de Concesiones",
                    "Concesiones": ", ".join(st.session_state.concesiones_seleccionadas),
                    "Novedades": desc_novedades
                }
                
                for conc, num in st.session_state.correos_por_concesion.items():
                    datos[f"Correos - {conc}"] = num
                
                if guardar_datos(datos):
                    ir_siguiente_actividad()

# PASO 4.4: Envío final (sin novedades)
elif st.session_state.paso == "4.4":
    datos = {
        "Fecha y Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Nombre": st.session_state.nombre,
        "Actividad": "Correo de Concesiones",
        "Concesiones": ", ".join(st.session_state.concesiones_seleccionadas),
        "Novedades": "No"
    }
    
    for conc, num in st.session_state.correos_por_concesion.items():
        datos[f"Correos - {conc}"] = num
    
    if guardar_datos(datos):
        ir_siguiente_actividad()

# ========== ANÁLISIS DEL DÍA ==========
# PASO 5: Análisis del día
elif st.session_state.paso == "5":
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
            st.session_state.paso = "2"
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
                    ir_siguiente_actividad()

# ========== FINALIZACIÓN ==========
# PASO 99: Exportación final
elif st.session_state.paso == "99":
    st.success("✅ ¡Todas las actividades completadas!")
    st.info(f"👤 **{st.session_state.nombre}** completó: {', '.join(st.session_state.actividades)}")
    
    if exportar_todo():
        st.balloons()
        
        if st.button("🔄 Hacer otro envío", use_container_width=True):
            st.session_state.paso = "1"
            st.session_state.nombre = ""
            st.session_state.actividades = []
            st.session_state.actividad_actual_index = 0
            st.session_state.datos_guardados = []
            st.session_state.categorias_seleccionadas = []
            st.session_state.tickets_por_categoria = {}
            st.session_state.escalados = ""
            st.session_state.novedades = ""
            st.session_state.tiene_pendientes = "No"
            st.session_state.concesiones_seleccionadas = []
            st.session_state.correos_por_concesion = {}
            st.session_state.tiene_novedades_conc = "No"
            st.rerun()

# Footer
st.markdown("---")
st.caption("Formulario de Entrega de Turno - Aseguramiento | Gopass")
