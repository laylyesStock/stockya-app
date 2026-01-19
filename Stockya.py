import streamlit as st
from supabase import create_client
import os

# 1. Configuración de la página (Icono y Título)
st.set_page_config(
    page_title="StockYa",
    page_icon="PiraB.PNG",
    layout="centered"
)

# --- TRUCO PARA OCULTAR ICONOS DE GITHUB Y MENÚ ---
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QS13 {display: none !important;}
    button[title="View source on GitHub"] {display: none !important;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)
# ------------------------------------------------

# 2. Configuración de Supabase
URL = "https://darvsiqglsyfistdmweh.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcnZzaXFnbHN5ZmlzdGRtd2VoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgyNDA2MjUsImV4cCI6MjA4MzgxNjYyNX0.4jrpYr2Sg1UC8o2Y7iMO0gbw6U8v28-eQSQrH4fXYRA"
supabase = create_client(URL, KEY)

# 3. Interfaz y Logo
st.title("StockYa ⚡")

if os.path.exists("PiraB.PNG"):
    st.image("PiraB.PNG", width=180)
elif os.path.exists("PiraB.png"):
    st.image("PiraB.png", width=180)

st.write("---")

# 4. Buscador Forzado en una Sola Fila (PC y Celular)
st.markdown("""
    <style>
    /* Este código fuerza a que las columnas no se apilen en el celular */
    [data-testid="column"] {
        flex-direction: row !important;
        align-items: center !important;
        display: flex !important;
    }
    div[data-testid="column"]:nth-of-type(1) {
        flex: 4 !important; /* El cuadro de texto ocupa más espacio */
    }
    div[data-testid="column"]:nth-of-type(2) {
        flex: 1 !important; /* La lupa ocupa menos espacio */
        margin-left: -20px; /* La acerca más al cuadro */
    }
    </style>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    cod = st.text_input("Código o Referencia", label_visibility="collapsed", placeholder="Buscar...").strip().upper()
with col2:
    buscar = st.button("🔍")

# Línea divisoria para que no se pegue a los resultados
st.write("")
# 5. Lógica de Búsqueda Corregida
if buscar:
    if cod:
        try:
            res = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.ilike.%{cod}%,c_Modelo.ilike.%{cod}%").execute()
            
            if res.data:
                st.subheader("Resultados:")
                for i, item in enumerate(res.data):
                    cant = int(item['n_cantidad'])
                    tienda = item['name_tienda']
                    desc = item['c_descripcion']
                    
                    # Colores
                    if cant <= 0:
                        emoji, color_txt = "❌", "#ff4b4b"
                    elif cant <= 3:
                        emoji, color_txt = "⚠️", "#ffa500"
                    else:
                        emoji, color_txt = "✅", "#09ab3b"
                    
                    fondo = "#f0f2f6" if i % 2 == 0 else "#ffffff"
                    
                    # El diseño HTML en una sola variable para evitar errores
                    html_fila = f"""
                    <div style="background-color: {fondo}; padding: 10px; border-radius: 5px; border: 1px solid #eee; display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="flex: 2;">
                            <div style="font-weight: bold; color: #333;">{tienda}</div>
                            <div style="font-size: 0.8em; color: #666;">{desc}</div>
                        </div>
                        <div style="flex: 1; padding-left: 30px; color: {color_txt}; font-weight: bold; white-space: nowrap;">
                            {emoji} {cant}
                        </div>
                    </div>
                    """
                    st.markdown(html_fila, unsafe_allow_html=True)
            else:
                st.warning("📍 Sin ubicación (No se encontraron resultados)")
                
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Escribe algo para buscar.")
        # --- LIMPIEZA TOTAL DE ICONOS Y PIE DE PÁGINA ---
    hide_style = """
        <style>
        /* Esconde el menú de 3 puntos y la barra superior */
        header {visibility: hidden !important;}
    
      /* Esconde el pie de página de Streamlit */
        footer {visibility: hidden !important;}
    
        /* Esconde el icono de GitHub (la herradura/gato) y otros botones de servicio */
        #MainMenu {visibility: hidden !important;}
        .viewerBadge_container__1QS13 {display: none !important;}
        .stAppDeployButton {display: none !important;}
        div[data-testid="stStatusWidget"] {display: none !important;}
    
        /* Elimina el espacio extra que dejan los elementos ocultos */
        .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)












