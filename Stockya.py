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

# 4. Buscador
col1, col2 = st.columns([3, 1]) # El botón queda al lado de los inputs
with col1:
    cod = st.text_input("Código o Referencia").strip().upper()
with col2:
    st.write("##") # Espacio para alinear el botón
    buscar = st.button("🔍")

# 5. Lógica de Búsqueda
if buscar:
    if cod:
        try:
            # Buscamos en ambas columnas para simplificarle la vida al usuario
            res = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.ilike.%{cod}%,c_Modelo.ilike.%{cod}%").execute()
            
            if res.data:
                st.subheader("Inventario:")
                for i, item in enumerate(res.data):
                    cant = int(item['n_cantidad'])
                    tienda = item['name_tienda']
                    desc = item['c_descripcion']
                    ubicacion = item.get('c_ubicacion', 'Sin Ubicación')
                    
                    if cant <= 0:
                        emoji_stk, texto_stock, color_txt = "❌", "AGOTADO", "#ff4b4b"
                    elif cant <= 3:
                        emoji_stk, texto_stock, color_txt = "⚠️", f"CRÍTICO: {cant}", "#ffa500"
                    else:
                        emoji_stk, texto_stock, color_txt = "✅", f"STOCK: {cant}", "#09ab3b"
                    
                    fondo = "#f0f2f6" if i % 2 == 0 else "#ffffff"
                    
                    st.markdown(f"""
                        <div style="background-color: {fondo}; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #ddd;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="font-size: 1.1em;">{tienda}</strong>
                                <span style="background: #31333F; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">📍 {ubicacion}</span>
                            </div>
                            <div style="margin-top: 5px; color: #444; font-size: 0.9em;">{desc}</div>
                            <div style="margin-top: 8px; color: {color_txt}; font-weight: bold; font-size: 1em;">{emoji_stk} {texto_stock}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No se encontró nada con ese dato.")
        except Exception as e:
            st.error("Error de conexión.")
    else:
        st.warning("Escribe algo para buscar.")








