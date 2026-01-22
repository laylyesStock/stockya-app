import streamlit as st
from supabase import create_client
import os

# 1. Configuración de página y LOGO
st.set_page_config(
    page_title="StockYa",
    page_icon="PiraB.PNG",
    layout="centered"
)

# 2. LIMPIEZA TOTAL (Al principio para que no falle)
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    .viewerBadge_container__1QS13 {display:none !important;}
    div[data-testid="stStatusWidget"] {display:none !important;}
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Configuración de Supabase
URL = "https://darvsiqglsyfistdmweh.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcnZzaXFnbHN5ZmlzdGRtd2VoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgyNDA2MjUsImV4cCI6MjA4MzgxNjYyNX0.4jrpYr2Sg1UC8o2Y7iMO0gbw6U8v28-eQSQrH4fXYRA"
supabase = create_client(URL, KEY)

# 4. Interfaz y Logo
st.title("StockYa ⚡")
try:
    # Traemos la información de la tabla de control
    res = supabase.table("control_tiendas").select("*").execute()
    if res.data:
        st.subheader("Estado de las Tiendas")
        cols = st.columns(len(res.data)) # Crea una columna por cada tienda
        
        for i, tienda in enumerate(res.data):
            with cols[i]:
                st.metric(label=tienda['tienda'], 
                          value="Online", 
                          delta=f"Hace {tienda['ultima_actualizacion']}")
except Exception as e:
    st.write("Conectando con el sistema de control...")



if os.path.exists("PiraB.PNG"):
    st.image("PiraB.PNG", width=180)
elif os.path.exists("PiraB.png"):
    st.image("PiraB.png", width=180)

st.write("---")

# 5. Buscador Forzado en una Sola Fila
st.markdown("""
    <style>
    [data-testid="column"] {
        flex-direction: row !important;
        align-items: center !important;
        display: flex !important;
    }
    div[data-testid="column"]:nth-of-type(1) { flex: 4 !important; }
    div[data-testid="column"]:nth-of-type(2) { flex: 1 !important; margin-left: -20px; }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    cod = st.text_input("Buscar...", label_visibility="collapsed", placeholder="Código o Referencia").strip().upper()
with col2:
    buscar = st.button("🔍")

st.write("")

# 6. Lógica de Búsqueda
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
                    
                    if cant <= 0: emoji, color_txt = "❌", "#ff4b4b"
                    elif cant <= 3: emoji, color_txt = "⚠️", "#ffa500"
                    else: emoji, color_txt = "✅", "#09ab3b"
                    
                    fondo = "#f0f2f6" if i % 2 == 0 else "#ffffff"
                    
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

















