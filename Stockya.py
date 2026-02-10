
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
    /* Ocultamos lo innecesario pero dejamos que el navegador gestione la App */
    .stDeployButton, #stDecoration { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    
    /* En lugar de ocultar, hacemos el header transparente y pequeño */
    header { background-color: rgba(0,0,0,0) !important; height: 1rem !important; }
    
    .block-container { padding-top: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Configuración de Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- INTERFAZ VISUAL ---
st.title("StockYa ⚡")

if os.path.exists("PiraB.PNG"):
    st.image("PiraB.PNG", width=180)
elif os.path.exists("PiraB.png"):
    st.image("PiraB.png", width=180)

st.markdown("---")
st.write("")

col1, col2 = st.columns([4, 1])
with col1:
    cod = st.text_input("Buscar...", label_visibility="collapsed", placeholder="Código o Referencia").strip().upper()
with col2:
    buscar = st.button("🔍")

# 4. Lógica de Búsqueda y Resultados
if cod: 
    try:
        # --- PASO 1: Traemos la bitácora de control ---
        res_ctrl = supabase.table("tblcontrolexistencias").select("tienda, ultimaactualizacion").execute()
        dict_sinc = {t['tienda']: t['ultimaactualizacion'] for t in res_ctrl.data}

        # --- PASO 2: Traemos existencias ---
        res_stock = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.ilike.%{cod}%,c_Modelo.ilike.%{cod}%").execute()
        
        if res_stock.data:
            # --- FILTRO BFF EVOLUCIONADO (Integridad Total) ---
            items_validados = []
            for item in res_stock.data:
                t_nombre = item['name_tienda']
                fecha_item_raw = item.get('Ultima_Actualizacion')
                fecha_valida_raw = dict_sinc.get(t_nombre)
                
                if fecha_item_raw and fecha_valida_raw:
                    try:
                        # Convertimos a datetime de pandas (maneja todos los formatos ISO)
                        f_item = pd.to_datetime(fecha_item_raw).replace(tzinfo=None)
                        f_ctrl = pd.to_datetime(fecha_valida_raw).replace(tzinfo=None)
                        
                        # Si la diferencia es menor a 60 segundos, el dato es íntegro
                        if abs((f_item - f_ctrl).total_seconds()) < 60:
                            items_validados.append(item)
                    except:
                        continue

            # Ahora trabajamos solo con los validados que tengan stock
            items_con_stock = [item for item in items_validados if int(item['n_cantidad']) > 0]
            
            if items_con_stock:
                st.subheader("Disponibilidad:")
                dias_semana = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]

                for i, item in enumerate(items_con_stock):
                    tienda_nombre = item['name_tienda']
                    cant = int(item['n_cantidad'])
                    
                    # --- Lógica de Identificación Dual ---
                    cod_art = str(item.get('c_codarticulo', '')).strip()
                    modelo = str(item.get('c_Modelo', '')).strip()
                    if modelo and modelo.upper() != "NONE" and modelo != cod_art:
                        identidad = f"{cod_art} / {modelo}"
                    else:
                        identidad = cod_art
                    
                    desc = f"{item['c_descripcion']} ({identidad})"
                    
                    # --- Lógica de Fecha (Visualización) ---
                    raw_fecha = dict_sinc.get(tienda_nombre, None)
                    sinc_txt = "---"

                    if raw_fecha:
                        try:
                            fecha_dt = pd.to_datetime(raw_fecha).replace(tzinfo=None)
                            nombre_dia = dias_semana[fecha_dt.weekday()]
                            sinc_txt = f"{nombre_dia} {fecha_dt.strftime('%d/%m/%Y %I:%M %p')}"
                        except:
                            sinc_txt = raw_fecha

                    color_txt = "#09ab3b" if cant > 3 else "#ffa500"
                    emoji_stock = "✅" if cant > 3 else "⚠️"
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
                                {emoji_stock} {cant}
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






































