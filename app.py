import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import requests
import json
import base64
import pytz  # Necesitarás instalar esta librería

# Configuración de la página (debe ir al principio)
st.set_page_config(page_title="Cambio de Turno", page_icon="📋", layout="wide")

# Logo de GoPass con contenedor estilizado
st.markdown("""
<div class="logo-container">
    <img src="https://i.imgur.com/z9xt46F.jpeg"
         style="width: 60%; border-radius: 10px; display: block; margin: 0 auto;" 
         alt="Logo Gopass">
</div>
""", unsafe_allow_html=True)

# Título principal
st.title("📋 Informe de Entrega de Cambio de Turno")

# CSS personalizado para normalizar estilos
st.markdown("""
<style>
    /* Normalizar todos los campos de entrada */
    .stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox select {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2);
    }
    
    /* Botones consistentes */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Formularios consistentes */
    .stForm {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 25px;
        background-color: #fafafa;
        margin-bottom: 20px;
    }
    
    /* Radio buttons y multiselect consistentes */
    .stRadio > div {
        flex-direction: row;
        gap: 20px;
    }
    
    .stRadio label {
        margin-right: 20px;
    }
    
    .stMultiSelect > div > div {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
    }
    
    /* Info boxes consistentes */
    .stAlert {
        border-radius: 8px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Función para obtener la hora actual de Colombia
def obtener_hora_colombia():
    try:
        # Zona horaria de Colombia (Bogotá)
        zona_colombia = pytz.timezone('America/Bogota')
        hora_actual = datetime.now(zona_colombia)
        return hora_actual.strftime("%Y-%m-%d %H:%M:%S")
    except:
        # Fallback en caso de error
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
if 'desc_pendientes' not in st.session_state:
    st.session_state.desc_pendientes = ""
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
if 'desc_novedades_conc' not in st.session_state:
    st.session_state.desc_novedades_conc = ""
if 'analisis_dia' not in st.session_state:
    st.session_state.analisis_dia = ""
if 'parqueaderos_seleccionadas' not in st.session_state:
    st.session_state.parqueaderos_seleccionadas = []
if 'correos_por_parqueadero' not in st.session_state:
    st.session_state.correos_por_parqueadero = {}
if 'tiene_novedades_p_conc' not in st.session_state:
    st.session_state.tiene_novedades_p_conc = "No"
if 'desc_novedades_p_conc' not in st.session_state:
    st.session_state.desc_novedades_p_conc = ""
if 'analisis_alertas' not in st.session_state:
    st.session_state.analisis_dia = ""

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
    
    if st.session_state.actividad_actual_index < len(st.session_state.actividades):
        siguiente_actividad = st.session_state.actividades[st.session_state.actividad_actual_index]
        if siguiente_actividad == "Tickets GLPI":
            st.session_state.paso = "3"
        elif siguiente_actividad == "Correo de Concesiones":
            st.session_state.paso = "4"
        elif siguiente_actividad == "Análisis del día":
            st.session_state.paso = "5"
        elif siguiente_actividad == "Conciliaciones parqueaderos":
            st.session_state.paso = "6"
        elif siguiente_actividad == "Gestion de alertas":
            st.session_state.paso = "7"
    else:
        st.session_state.paso = "99"
    
    st.rerun()

# Función para exportar a GitHub
def exportar_todo():
    try:
        # Obtener configuración de GitHub desde secrets
        github_token = st.secrets["github"]["token"]
        repo_owner = st.secrets["github"]["repo_owner"]
        repo_name = st.secrets["github"]["repo_name"]
        file_path = st.secrets["github"]["file_path"]
        
        # URL de la API de GitHub
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Intentar obtener el archivo existente
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            # Archivo existe, descargar y agregar datos
            file_data = response.json()
            file_sha = file_data["sha"]
            
            # Decodificar contenido existente
            existing_content = base64.b64decode(file_data["content"])
            existing_df = pd.read_excel(BytesIO(existing_content))
            
            # Crear DataFrame con nuevos datos
            df_nuevos = pd.DataFrame(st.session_state.datos_guardados)
            
            # FILTRAR DUPLICADOS EXACTOS: Comparar TODOS los campos incluyendo "Fecha y Hora"
            registros_unicos = []
            registros_duplicados = 0
            
            for idx, nuevo_registro in df_nuevos.iterrows():
                # Verificar si el registro ya existe en existing_df (comparación completa)
                es_duplicado = False
                
                if not existing_df.empty:
                    for _, registro_existente in existing_df.iterrows():
                        # Comparar TODOS los campos (incluyendo Fecha y Hora)
                        campos_iguales = True
                        
                        for col in df_nuevos.columns:
                            valor_nuevo = nuevo_registro.get(col, "")
                            valor_existente = registro_existente.get(col, "")
                            
                            # Comparar como strings para evitar problemas con tipos de datos
                            if str(valor_nuevo) != str(valor_existente):
                                campos_iguales = False
                                break
                        
                        if campos_iguales:
                            es_duplicado = True
                            break
                
                if not es_duplicado:
                    registros_unicos.append(nuevo_registro)
                else:
                    registros_duplicados += 1
            
            # Si todos los registros son duplicados, informar y no actualizar
            if len(registros_unicos) == 0:
                st.warning(f"⚠️ No se guardaron datos: {registros_duplicados} registro(s) duplicado(s) detectado(s)")
                st.info("💡 Este registro ya fue enviado anteriormente (mismo usuario, fecha, hora y datos)")
                return False
            
            # Crear DataFrame solo con registros únicos
            df_nuevos_unicos = pd.DataFrame(registros_unicos)
            
            # Concatenar con los datos existentes
            df_completo = pd.concat([existing_df, df_nuevos_unicos], ignore_index=True)
            
            # Mostrar información de duplicados si los hay
            if registros_duplicados > 0:
                st.warning(f"⚠️ Se omitieron {registros_duplicados} registro(s) duplicado(s)")
                st.success(f"✅ Se guardaron {len(registros_unicos)} registro(s) nuevo(s)")
            
        elif response.status_code == 404:
            # Archivo no existe, crear nuevo
            file_sha = None
            df_nuevos = pd.DataFrame(st.session_state.datos_guardados)
            df_completo = df_nuevos
            
        else:
            raise Exception(f"Error al acceder a GitHub: {response.status_code} - {response.text}")
        
        # Guardar DataFrame en buffer
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_completo.to_excel(writer, index=False, sheet_name='Entregas')
        output.seek(0)
        
        # Codificar en base64 para GitHub
        content_base64 = base64.b64encode(output.read()).decode('utf-8')
        
        # Preparar payload para GitHub
        commit_message = f"Actualización de entregas - {obtener_hora_colombia()}"
        
        payload = {
            "message": commit_message,
            "content": content_base64,
        }
        
        if file_sha:
            payload["sha"] = file_sha
        
        # Subir archivo a GitHub
        upload_response = requests.put(api_url, headers=headers, json=payload)
        
        if upload_response.status_code in [200, 201]:
            st.success("✅ Datos guardados exitosamente en GitHub")
            
            # Mostrar link al archivo
            file_url = f"https://github.com/{repo_owner}/{repo_name}/blob/main/{file_path}"
            st.markdown(f"🔗 [Ver archivo en GitHub]({file_url})")
            
            # Ofrecer descarga local también
            timestamp = obtener_hora_colombia().replace(":", "").replace(" ", "_").replace("-", "")
            nombre_archivo = f"entrega_turno_{timestamp}.xlsx"
            
            output.seek(0)
            st.download_button(
                label="📥 Descargar copia local",
                data=output.getvalue(),
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # Mostrar resumen
            st.markdown("### 📊 Resumen de datos guardados:")
            st.dataframe(df_nuevos_unicos if 'df_nuevos_unicos' in locals() else df_nuevos, use_container_width=True)
            
            return True
        else:
            raise Exception(f"Error al subir archivo: {upload_response.status_code} - {upload_response.text}")
        
    except KeyError as e:
        st.error(f"❌ Error de configuración: Falta {str(e)} en secrets")
        st.info("⚙️ Configura los secrets de GitHub en Streamlit Cloud")
        return False
        
    except Exception as e:
        st.error(f"❌ Error al guardar en GitHub: {str(e)}")
        
        # Fallback: guardar localmente
        try:
            timestamp = obtener_hora_colombia().replace(":", "").replace(" ", "_").replace("-", "")
            nombre_archivo = f"entrega_turno_{timestamp}.xlsx"
            
            df_nuevos = pd.DataFrame(st.session_state.datos_guardados)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_nuevos.to_excel(writer, index=False, sheet_name='Entregas')
            output.seek(0)
            
            st.warning("⚠️ Guardando localmente por error de conexión con GitHub")
            st.download_button(
                label="📥 Descargar respaldo local",
                data=output.getvalue(),
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            return True
        except Exception as e2:
            st.error(f"❌ Error al guardar localmente: {str(e2)}")
            return False

# PASO 1: Selección de nombre
if st.session_state.paso == "1":
    with st.form("form_nombre"):
        st.markdown("### 👤 Analista de Aseguramiento")
        nombre = st.selectbox(
            "Seleccione su nombre *",
            ["", "David Grillo", "Jose Arias", "Cesar Salamanca", "Ruben Palacios"],
            key="select_nombre"
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
        st.markdown("### 📋 Selección de Actividades")
        actividades = st.multiselect(
            "¿Qué trabajaste en tu turno? *",
            ["Tickets GLPI", "Correo de Concesiones", "Análisis del día", "Conciliaciones parqueaderos", "Gestion de alertas"],
            default=st.session_state.actividades,
            key="multiselect_actividades"
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
                elif primera_actividad == "Conciliaciones parqueaderos":
                    st.session_state.paso = "6"
                elif primera_actividad == "Gestion de alertas":
                    st.session_state.paso = "7"

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
        st.markdown("### 🎯 Categorías de Tickets")
        categorias = st.multiselect(
            "¿Cuáles categorías trabajaste? *",
            categorias_opciones,
            default=st.session_state.categorias_seleccionadas,
            key="multiselect_categorias"
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
        st.markdown("### 📊 Número de Tickets Resueltos")
        st.markdown("**Ingresa la cantidad de tickets resueltos por categoría:**")
        
        tickets_dict = {}
        for cat in st.session_state.categorias_seleccionadas:
            valor_default = st.session_state.tickets_por_categoria.get(cat, 0)
            tickets_dict[cat] = st.number_input(
                f"Tickets en {cat}",
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
        st.markdown("### 🔄 Tickets Escalados y Novedades")
        
        escalados = st.text_input(
            "¿Cuántos tickets escalaste a otras áreas? (ej: Desarrollo - 5)",
            value=st.session_state.escalados,
            key="input_escalados"
        )
        
        novedades = st.text_area(
            "¿Tuviste novedades en tickets?",
            value=st.session_state.novedades,
            height=100,
            key="area_novedades"
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
        st.markdown("### 📋 Pendientes para el Siguiente Turno")
        
        pendientes = st.radio(
            "¿Dejaste algo pendiente? *",
            ["No", "Sí"],
            index=0 if st.session_state.tiene_pendientes == "No" else 1,
            key="radio_pendientes"
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
                # Guardar datos sin pendientes
                datos = {
                    "Fecha y Hora": obtener_hora_colombia(),
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

# PASO 3.4: Descripción de pendientes
elif st.session_state.paso == "3.4":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 🎫 Tickets GLPI")
    
    with st.form("form_desc_pendientes"):
        st.markdown("### 📝 Descripción de Pendientes")
        
        desc_pendientes = st.text_area(
            "¿Qué dejaste pendiente para el siguiente turno? *",
            value=st.session_state.desc_pendientes,
            height=150,
            key="area_pendientes"
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
                    "Fecha y Hora": obtener_hora_colombia(),
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
                    st.session_state.desc_pendientes = ""  # Limpiar para siguiente uso
                    ir_siguiente_actividad()

# ========== CORREO DE CONCESIONES ==========
# PASO 4: Selección de concesiones
elif st.session_state.paso == "4":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Correo de Concesiones")
    
    concesiones_opciones = [
        "Accenorte",
        "Alt. Viales",
        "Alma",
        "Aut. El Cafe",
        "App Gica",
        "Aut. Del Caribe",
        "Aut. Rio Grande",
        "Aut. Rio Magda",
        "Alca. Envigado",
        "Aut. Nordeste",
        "Autovia BTS",
        "Aut. Neiva–Girar",
        "Panamericana",
        "Coviiandina",
        "Covioriente",
        "Covipacifico",
        "Devimar",
        "Devimed",
        "Devisab",
        "Findeter",
        "La Pintada",
        "Pacifico Tres",
        "Peajes Nacionales",
        "Peri. Del Oriente",
        "Concesión Pisa",
        "Ruta Al Mar",
        "Ruta Al Sur",
        "Ruta Costera C-B",
        "Ruta Del Cacao",
        "R. Magdalena S.M",
        "Ruta Del Valle",
        "Saba. De Occidente",
        "Ruta Portuaria",
        "Tunel Aburra Or.",
        "U.V Camino Del P.",
        "Via 40 Express",
        "Vial De Los Llanos",
        "Transv. Sigsa",
        "Montes De Maria",
        "Rio Pamplonita",
        "Union Del Sur",
        "Vias Del Nus",
        "Yuma",
        "ICCU",
        "Aut. Urabá",
        "Aut. Magda Medio"
    ]

    with st.form("form_concesiones_select"):
        st.markdown("### 🏢 Concesiones Trabajadas")
        concesiones = st.multiselect(
            "¿Qué concesiones trabajaste? *",
            concesiones_opciones,
            default=st.session_state.concesiones_seleccionadas,
            key="multiselect_concesiones"
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
        st.markdown("### 📧 Correos Respondidos por Concesión")
        st.markdown("**Ingresa la cantidad de correos respondidos por concesión:**")
        
        correos_dict = {}
        for conc in st.session_state.concesiones_seleccionadas:
            valor_default = st.session_state.correos_por_concesion.get(conc, 0)
            correos_dict[conc] = st.number_input(
                f"Correos en {conc}",
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
        st.markdown("### 📋 Novedades en Concesiones")
        
        tuvo_novedades = st.radio(
            "¿Tuviste novedades? *",
            ["No", "Sí"],
            index=0 if st.session_state.tiene_novedades_conc == "No" else 1,
            key="radio_novedades_conc"
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
                # Guardar datos sin novedades
                datos = {
                    "Fecha y Hora": obtener_hora_colombia(),
                    "Nombre": st.session_state.nombre,
                    "Actividad": "Correo de Concesiones",
                    "Concesiones": ", ".join(st.session_state.concesiones_seleccionadas),
                    "Novedades": "No"
                }
                
                for conc, num in st.session_state.correos_por_concesion.items():
                    datos[f"Correos - {conc}"] = num
                
                if guardar_datos(datos):
                    ir_siguiente_actividad()

# PASO 4.3: Descripción de novedades
elif st.session_state.paso == "4.3":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Correo de Concesiones")
    
    with st.form("form_desc_novedades_conc"):
        st.markdown("### 📝 Descripción de Novedades")
        
        desc_novedades = st.text_area(
            "¿Qué novedades tuviste? *",
            value=st.session_state.desc_novedades_conc,
            height=150,
            key="area_novedades_conc"
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
                    "Fecha y Hora": obtener_hora_colombia(),
                    "Nombre": st.session_state.nombre,
                    "Actividad": "Correo de Concesiones",
                    "Concesiones": ", ".join(st.session_state.concesiones_seleccionadas),
                    "Novedades": desc_novedades
                }
                
                for conc, num in st.session_state.correos_por_concesion.items():
                    datos[f"Correos - {conc}"] = num
                
                if guardar_datos(datos):
                    st.session_state.desc_novedades_conc = ""  # Limpiar para siguiente uso
                    ir_siguiente_actividad()

# ========== ANÁLISIS DEL DÍA ==========
# PASO 5: Análisis del día
elif st.session_state.paso == "5":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📊 Análisis del Día")
    
    with st.form("form_analisis"):
        st.markdown("### 📈 Análisis del Día")
        
        analisis = st.text_area(
            "Describe el análisis del día: *",
            value=st.session_state.analisis_dia,
            height=200,
            key="area_analisis"
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
                    "Fecha y Hora": obtener_hora_colombia(),
                    "Nombre": st.session_state.nombre,
                    "Actividad": "Análisis del Día",
                    "Análisis": analisis
                }
                
                if guardar_datos(datos):
                    st.session_state.analisis_dia = ""  # Limpiar para siguiente uso
                    ir_siguiente_actividad()


# ========== conciliaciones parqueaderos ==========
# PASO 4: Selección de parqueaderos
elif st.session_state.paso == "6":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Conciliaciones parqueaderos")
    
    parqueaderos_opciones = [
    "CENTRO COMERCIAL AVENIDA JIMENEZ",
    "PACIFIC MALL",
    "PARQUE LLERAS",
    "MALLPLAZA NQS",
    "COMERCIO PRUEBAS TX",
    "CENTRO COMERCIAL ALTOS DEL PRADO",
    "TEQUENDAMA TORRE BANCO FALABELLA",
    "CARRERA 5A CON 18",
    "CC LA ESTACION IBAGUE",
    "SALITRE PLAZA",
    "CC PUERTA DEL NORTE",
    "PALATINO",
    "JUMBO CALLE 170",
    "CENTRO",
    "SANDWICH QBANO",
    "TEQUENDAMA CE ROSETTA (D+A)",
    "CALLE 88",
    "COMERCIO DE PRUEBAS EN TX",
    "CC 20 DE JULIO",
    "METRO PRADO",
    "TEQUENDAMA CENTRO MEDICO DALI",
    "CENTRO MEDICO MONTSALUD",
    "EASY SOACHA",
    "EDIFICIO INTERNATIONAL TOWER",
    "CC MULTICENTRO IBAGUE",
    "COMCEL",
    "HACIENDA SANTA BÁRBARA",
    "TEQUENDAMA UNIANDES",
    "TEQUENDAMA ALTOS DEL BOSQUE",
    "LOS MOLINOS",
    "CC EL PUENTE",
    "FUNERARIA EL APOGEO",
    "SANTA BEATRIZ 3",
    "TEQUENDAMA PARTENON II",
    "EL RETIRO",
    "CASA DE LA CERVEZA",
    "ARCHIES PEPE SIERRA",
    "ANDINO PASS",
    "CALLE 96",
    "SA R",
    "CC PREMIUM PLAZA",
    "CC JARDINES LLANO GRANDE",
    "MARIACHIS",
    "METRO GIRON BULEVAR DE LAS CEIBAS",
    "MC DONALDS AV ESPERANZA",
    "CC HAYUELOS",
    "LA TERMINAL SANTA BARBARA",
    "FEDETRANSCARGA ACCESO",
    "PEDRO SAFI",
    "METRO SIMÓN BOLÍVAR",
    "CENTRO COMERCIAL BIMA",
    "COMERCIO DE PRUEBAS",
    "GRAN PLAZA BOSA",
    "TEQUENDAMA CLL 77",
    "PARKING CLINICA SAN RAFAEL I",
    "LOCAL",
    "MODELIA BARES",
    "EASY GAITAN CORTEZ",
    "TEQUENDAMA PARTENON I",
    "JUMBO CALLE 80",
    "CENTRO MEDICO COUNTRY 80",
    "METRO SAN CAYETANO",
    "MILENIO SUR",
    "TEQUENDAMA EDIFICIO EL BOSQUE",
    "TEATRO ECCI CENTRO",
    "UNISABANA PUENTE MADERA",
    "UNIVERSIDAD PILOTO",
    "RADAR PARK",
    "CC PLAZA CENTRAL",
    "JUMBO PALOQUEMADO",
    "CENTRO CHÍA",
    "AV ESPERANZA",
    "COUNTRY CALLE 85",
    "UNICENTRO MEDELLIN",
    "TEQUENDAMA INVENTION CENTER",
    "SAN ANDRESITO ASDINCGO",
    "OLIMPICA CL 100",
    "EDIFICIO TERPEL",
    "TUNAL 1",
    "TUNAL 1 (ERRONEO)",
    "UNIVERSIDAD ANTONIO NARIÑO",
    "AEROPUERTO INTERNACIONAL DE BARRANQUILLA",
    "CASTILLA",
    "UNICENTRO CALI",
    "CC SAN CANCIO",
    "PARQUE LA COLINA",
    "METRO BELLO",
    "CORRAL TRADICIONAL CEDRITOS",
    "CC SAN SILVESTRE",
    "LOTE 12 - LA TERMINAL",
    "TEQUENDAMA PLAZA ESPAÑA",
    "CORRAL TRADICIONAL CLL 116",
    "TEQUENDAMA KUAN (CHIA)",
    "EASY 4 SUR",
    "BELMIRA",
    "PARKING ARCHIES CEDRITOS",
    "CALLE 100-1 OLIMPICA",
    "UNICENTRO BOGOTA",
    "CC AVENIDA CHILE",
    "CALLE 93A",
    "UNICENTRO PALMIRA",
    "JUMBO CHIPICHAPE",
    "CC PUNTO CLAVE",
    "CC CHIPICHAPE",
    "GOPASSS",
    "PARTENON",
    "ALHAMBRA 1 CARULLA",
    "METRO ITAGUI",
    "CENTRO COMERCIAL PUENTE LARGO",
    "GRAN PLAZA EL ENSUEÑO",
    "FEDETRANSCARGA RESTAURANTE",
    "TEQUENDAMA CLL 90",
    "EDIFICIO TORRE PLATINO",
    "SANTA BEATRIZ 1",
    "CC ATLANTIS PLAZA",
    "CALLE 100 SALAS",
    "COMERCIO PARA PRUEBAS",
    "TEQUENDAMA SANTA BARBARA",
    "ZONA ROSA ELITE",
    "CC ISERRA 100",
    "ALHAMBRA 2 TRIANGULO",
    "CALLE 90 CHICO",
    "JUMBO HAYUELOS",
    "CENTRO EMP SAN ROQUE",
    "MCDONALD'S AV 1RA DE MAYO",
    "CENTRO COMERCIAL GRAN SAN VICTORINO",
    "GRAN PLAZA TERREROS",
    "CC CAÑAVERAL",
    "CC FUNDADORES",
    "GRAN PLAZA DEL SOL",
    "CC BUENAVISTA 1",
    "CINE COLOMBIA CHAPINERO",
    "GRAN PLAZA FLORENCIA",
    "CC PLAZA IMPERIAL",
    "INNOVO PLAZA",
    "CC PASEO VILLA DEL RIO",
    "CENTRO MÉDICO ALMIRANTE COLÓN",
    "PARKING CLÍNICA SAN RAFAEL II",
    "HOLGUINES TRADE CENTER",
    "HELM BANK",
    "TERMINAL SUR DE MEDELLIN P.H",
    "METRO AUTOPISTA SUR",
    "CALLE 97",
    "CC BULEVAR NIZA",
    "CASALIMPIA",
    "TERMINAL SUR",
    "JUMBO RIONEGRO",
    "SANTA BEATRIZ  2",
    "ANDINO",
    "CC VIZCAYA",
    "MODULO 1",
    "UNIVERSIDAD DE LA SALLE",
    "UNISABANA CAMPUS",
    "ELITE DE LA MODA",
    "TERMINAL NORTE",
    "JUMBO LAS VEGAS",
    "PLAZA DE LAS AMERICAS",
    "SUBA - LOT",
    "SANTAFE",
    "GRAN PLAZA IPIALES",
    "CC VIVA ENVIGADO",
    "LAGO 79",
    "CC NUESTRO BOGOTA",
    "FEDETRANSCARGA AUDITORIO",
    "ANALIZAR",
    "BOLSA DE BOGOTA",
    "JUZGADOS CARRERA 10A",
    "TEQUENDAMA UNIBOSQUE",
    "CORFERIAS PARQUEADERO VERDE",
    "URBAN",
    "GRAN ESTACION 2",
    "GRAN PLAZA SOACHA",
    "CORRAL TRADICIONAL CLL 93A",
    "SAN ANDRESITO PROVIDENCIA",
    "METRO MOSQUERA",
    "MODELIA EXITO",
    "CC BUENAVISTA 2",
    "CENTRO COMERCIAL LOURDES III",
    "AVENIDA 19 CON 114",
    "FONTANAR",
    "CENTRO COMERCIAL AUTO GRANDE",
    "CHICO 97",
    "UNICENTRO ARMENIA",
    "EASY CENTRO MAYOR",
    "UNICENTRO CUCUTA",
    "PRUEBA",
    "AEROPUERTO RIONEGRO",
    "CASTELLANA",
    "EDIFICIO COLINA OFFICE PARK",
    "SANTAFE MEDELLIN",
    "PARKING SOTANO",
    "PALMETTO PLAZA",
    "ACQUA POWER CENTER",
    "CRUZ ROJA COLOMBIANA",
    "SAN ANDRESITO RONCADOR S.A.S",
    "TITAN PLAZA",
    "METRO FLORIDABLANCA",
    "CEMENTERIO EL APOGEO",
    "CC CARIBE PLAZA"
]

    with st.form("form_parqueaderos_select"):
        st.markdown("### 🏢 Conciliaciones Trabajadas")
        parqueaderos = st.multiselect(
            "¿Qué conciliaciones trabajaste? *",
            parqueaderos_opciones,
            default=st.session_state.parqueaderos_seleccionadas,
            key="multiselect_parqueaderos"
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
            if not parqueaderos:
                st.error("⚠️ Selecciona al menos un parqueadero")
            else:
                st.session_state.parqueaderos_seleccionadas = parqueaderos
                st.session_state.paso = "6.1"
                st.rerun()

# PASO 4.1: Número de correos por parqueadero
elif st.session_state.paso == "6.1":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Conciliaciones parqueaderos")
    
    with st.form("form_num_correos"):
        st.markdown("### 📧 Correos Respondidos por Parqueadero")
        st.markdown("**Ingresa la cantidad de correos respondidos por parqueadero:**")
        
        correos_dict_p = {}
        for conc in st.session_state.parqueaderos_seleccionadas:
            valor_default = st.session_state.correos_por_parqueadero.get(conc, 0)
            correos_dict_p[conc] = st.number_input(
                f"Correos en {conc}",
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
            st.session_state.paso = "6"
            st.rerun()
        
        if siguiente:
            st.session_state.correos_por_parqueadero = correos_dict_p
            st.session_state.paso = "6.2"
            st.rerun()

# PASO 6.2: ¿Tuviste novedades?
elif st.session_state.paso == "6.2":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Conciliaciones parqueaderos")
    
    with st.form("form_novedades_conc"):
        st.markdown("### 📋 Novedades en Conciliaciones de parqueaderos")
        
        tuvo_novedades_p = st.radio(
            "¿Tuviste novedades? *",
            ["No", "Sí"],
            index=0 if st.session_state.tiene_novedades_p_conc == "No" else 1,
            key="radio_novedades_p_conc"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            siguiente = st.form_submit_button("Siguiente ➡️", use_container_width=True)
        
        if atras:
            st.session_state.paso = "6.1"
            st.rerun()
        
        if siguiente:
            st.session_state.tiene_novedades_p_conc = tuvo_novedades_p
            if tuvo_novedades_p == "Sí":
                st.session_state.paso = "6.3"
            else:
                # Guardar datos sin novedades
                datos = {
                    "Fecha y Hora": obtener_hora_colombia(),
                    "Nombre": st.session_state.nombre,
                    "Actividad": "Correo de Concesiones",
                    "Parqueaderos": ", ".join(st.session_state.parqueaderos_seleccionadas),
                    "Novedades": "No"
                }
                
                for conc, num in st.session_state.correos_por_parqueadero.items():
                    datos[f"Correos - {conc}"] = num
                
                if guardar_datos(datos):
                    ir_siguiente_actividad()

# PASO 6.3: Descripción de novedades
elif st.session_state.paso == "6.3":
    st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📧 Conciliaciones parqueaderos")
    
    with st.form("form_desc_novedades_p_conc"):
        st.markdown("### 📝 Descripción de Novedades")
        
        desc_novedades_p = st.text_area(
            "¿Qué novedades tuviste? *",
            value=st.session_state.desc_novedades_p_conc,
            height=150,
            key="area_novedades_p_conc"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            atras = st.form_submit_button("⬅️ Atrás", use_container_width=True)
        with col2:
            enviar = st.form_submit_button("📤 Enviar", use_container_width=True)
        
        if atras:
            st.session_state.paso = "6.2"
            st.rerun()
        
        if enviar:
            if not desc_novedades_p.strip():
                st.error("⚠️ Por favor describe las novedades")
            else:
                datos = {
                    "Fecha y Hora": obtener_hora_colombia(),
                    "Nombre": st.session_state.nombre,
                    "Actividad": "Correo de Concesiones",
                    "Parqueaderos": ", ".join(st.session_state.parqueaderos_seleccionadas),
                    "Novedades": desc_novedades_p
                }
                
                for conc, num in st.session_state.correos_por_parqueadero.items():
                    datos[f"Correos - {conc}"] = num
                
                if guardar_datos(datos):
                    st.session_state.desc_novedades_p_conc = ""  # Limpiar para siguiente uso
                    ir_siguiente_actividad()


 # ========== ANÁLISIS DEL DÍA ==========
 # PASO 7: Gestion de alertas
elif st.session_state.paso == "7":
        st.info(f"👤 Usuario: **{st.session_state.nombre}** | 📊 Gestion de alertas")
        
    with st.form("form_analisis_alertas"):
            st.markdown("### 📈 Gestión de alertas")
            
        gestion = st.text_area(
                    "Describe tu gestión de alertas: *",
                    value=st.session_state.analisis_alertas,
                    height=200,
                    key="alertas_analisis"
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
                            "Fecha y Hora": obtener_hora_colombia(),
                            "Nombre": st.session_state.nombre,
                            "Actividad": "Gestión de Alertas",
                            "Gestion": gestion
                        }
                        
                        if guardar_datos(datos):
                            st.session_state.analisis_alertas = ""  # Limpiar para siguiente uso
                            ir_siguiente_actividad()            
 

# ========== FINALIZACIÓN ==========
# PASO 99: Exportación final
elif st.session_state.paso == "99":
    st.success("✅ ¡Todas las actividades completadas!")
    st.info(f"👤 **{st.session_state.nombre}** completó: {', '.join(st.session_state.actividades)}")
    
    if exportar_todo():
        st.balloons()
        
        if st.button("🔄 Hacer otro envío", use_container_width=True):
            # Resetear todos los estados
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Footer
st.markdown("---")
st.caption("Formulario de Entrega de Turno - Aseguramiento | Gopass | Created by Angel Torres")
