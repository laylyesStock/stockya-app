import streamlit as st
from supabase import create_client
import pandas as pd
import os

# 1. Configuración de página
st.set_page_config(
    page_title="StockYa",
    page_icon="PiraB.PNG",
    layout="centered"
)

# 2. LIMPIEZA TOTAL DE INTERFAZ (CSS)
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    /* Estilo para que la lupa y el input queden en la misma línea */
    [data-testid="column"] {
        flex-direction: row !important;
        align-items: center !important;
        display: flex !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Configuración de Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- ORDEN VISUAL SOLICITADO ---

# A. Título Principal
st.title("StockYa ⚡")

# B. Logo Tiendas La Pirámide
if os.path.exists("PiraB.PNG"):
    st.image("PiraB.PNG", width=180)
elif os.path.exists("PiraB.png"):
    st.image("PiraB.png", width=180)

st.write("") # Espacio pequeño

# C. Buscador (Caja de texto + Lupa)
col1, col2 = st.columns([4, 1])
with col1:
    cod = st.text_input("Buscar...", label_visibility="collapsed", placeholder="Código o Referencia").strip().upper()
with col2:
    buscar = st.button("🔍")

# 4. Lógica de Búsqueda y Resultados
if cod: # Se activa al escribir o dar clic en lupa
    try:
        # Traemos existencias
        res_stock = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.ilike.%{cod}%,c_Modelo.ilike.%{cod}%").execute()
        
        # Traemos la bitácora para saber las horas de sincronización
        res_ctrl = supabase.table("tblcontrolexistencias").select("tienda, ultimaactualizacion").execute()
        dict_sinc = {t['tienda']: t['ultimaactualizacion'] for t in res_ctrl.data}

        if res_stock.data:
            # Solo tiendas con stock mayor a 0
            items_con_stock = [item for item in res_stock.data if int(item['n_cantidad']) > 0]
            
            if items_con_stock:
                st.subheader("Disponibilidad:")
                
                for i, item in enumerate(items_con_stock):
                    tienda_nombre = item['name_tienda']
                    cant = int(item['n_cantidad'])
                    desc = item['c_descripcion']
                    
                    # Formatear la hora de sincronización de esta tienda
                    raw_fecha = dict_sinc.get(tienda_nombre, "---")
                    try:
                        fecha_dt = pd.to_datetime(raw_fecha).replace(tzinfo=None)
                        sinc_txt = fecha_dt.strftime('%I:%M %p')
                    except:
                        sinc_txt = raw_fecha

                    # Colores por cantidad
                    color_txt = "#09ab3b" if cant > 3 else "#ffa500"
                    emoji = "✅" if cant > 3 else "⚠️"
                    
                    # Diseño de la fila (Minimalista)
                    fondo = "#f8f9fa" if i % 2 == 0 else "#ffffff"
                    
                    html_fila = f"""
                    <div style="background-color: {fondo}; padding: 12px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 2;">
                                <div style="font-weight: bold; color: #333; font-size: 1.1em;">{tienda_nombre}</div>
                                <div style="font-size: 0.85em; color: #666;">{desc}</div>
                                <div style="font-size: 0.8em; color: #888; margin-top: 4px;">📡 {sinc_txt}</div>
                            </div>
                            <div style="flex: 1; text-align: right; color: {color_txt}; font-weight: bold; font-size: 1.2em;">
                                {emoji} {cant}
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(html_fila, unsafe_allow_html=True)
            else:
                st.warning("📍 No hay stock disponible en ninguna tienda.")
        else:
            if buscar: st.error("📍 Producto no encontrado.")
            
    except Exception as e:
        st.error(f"Error en consulta: {e}")

























