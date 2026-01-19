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
# 5. Lógica de Búsqueda Estilo Excel Lineal
if buscar:
    if cod:
        try:
            res = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.ilike.%{cod}%,c_Modelo.ilike.%{cod}%").execute()
            
            if res.data:
                st.write("### Inventario:")
                for i, item in enumerate(res.data):
                    cant = int(item['n_cantidad'])
                    tienda = item['name_tienda']
                    desc = item['c_descripcion']
                    
                    # Semáforo de colores
                    if cant <= 0:
                        emoji, color_txt = "❌", "#ff4b4b" # Rojo
                    elif cant <= 3:
                        emoji, color_txt = "⚠️", "#ffa500" # Naranja
                    else:
                        emoji, color_txt = "✅", "#09ab3b" # Verde
                    
                    # Fondo alternado estilo cebra
                    fondo = "#f0f2f6" if i % 2 == 0 else "#ffffff"
                    
                    # FILA LINEAL ESTILO EXCEL (Sin el campo ubicación)
                    st.markdown(f"""
                        <div style="background-color: {fondo}; padding: 8px 10px; border: 1px solid #eee; font-family: sans-serif; font-size: 0.9em; display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-right: 10px;">
                                <strong>{tienda}</strong> | {desc}
                            </div>
                            <div style="color: {color_txt}; font-weight: bold; white-space: nowrap;">
                                {emoji} {cant}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                # AQUÍ USAMOS TU FRASE: Solo sale si no hay coincidencias
                st.warning("📍 Sin ubicación (No se encontraron resultados para esta búsqueda)")
                
        except Exception as e:
            st.error("Error de conexión con la base de datos.")
    else:
        st.warning("Por favor, escribe un código o referencia.")









