import streamlit as st
from supabase import create_client
import os

# 1. Configuración de página y LOGO
st.set_page_config(
    page_title="StockYa",
    page_icon="PiraB.PNG",
    layout="centered"
)

# 2. LIMPIEZA TOTAL
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    .viewerBadge_container__1QS13 {display:none !important;}
    div[data-testid="stStatusWidget"] {display:none !important;}
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Configuración de Supabase
URL = "https://darvsiqglsyfistdmweh.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcnZzaXFnbHN5ZmlzdGRtd2VoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgyNDA2MjUsImV4cCI6MjA4MzgxNjYyNX0.4jrpYr2Sg1UC8o2Y7iMO0gbw6U8v28-eQSQrH4fXYRA"
supabase = create_client(URL, KEY)

# 4. Interfaz y Estado de Tiendas
st.title("StockYa ⚡")

try:
    # Traemos la información de la tabla de control
    res_ctrl = supabase.table("control_tiendas").select("*").execute()
    if res_ctrl.data:
        st.write("### Estado de las Tiendas")
        cols = st.columns(len(res_ctrl.data))
        
        for i, tienda in enumerate(res_ctrl.data):
            with cols[i]:
                # Mostramos la tienda y su última sincronización
                st.metric(
                    label=tienda['tienda'], 
                    value="Online 📡", 
                    delta=f"Act: {tienda['ultima_actualizacion']}"
                )
except Exception as e:
    st.info("Sincronizando reloj de tiendas...")

# Mostrar Logo
if os.path.exists("PiraB.PNG"):
    st.image("PiraB.PNG", width=150)
elif os.path.exists("PiraB.png"):
    st.image("PiraB.png", width=150)

st.write("---")

# 5. Buscador Forzado
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

# 6. Lógica de Búsqueda Mejorada
if buscar and cod:
    try:
        # Buscamos en la tabla tblExistencias
        res = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.ilike.%{cod}%,c_Modelo.ilike.%{cod}%").execute()
        
        if res.data:
            # --- FILTRO MÁGICO: Solo mostramos si cantidad > 0 ---
            items_con_stock = [item for item in res.data if int(item['n_cantidad']) > 0]
            
            if items_con_stock:
                st.subheader("Resultados:")
                for i, item in enumerate(items_con_stock):
                    cant = int(item['n_cantidad'])
                    tienda = item['name_tienda']
                    desc = item['c_descripcion']
                    
                    # Semáforo de stock
                    if cant <= 3: emoji, color_txt = "⚠️", "#ffa500"
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
                st.warning("📍 Sin stock disponible en ninguna tienda.")
        else:
            st.warning("📍 Producto no encontrado.")
    except Exception as e:
        st.error(f"Error en la consulta: {e}")
elif buscar and not cod:
    st.warning("Escribe algo para buscar.")

















