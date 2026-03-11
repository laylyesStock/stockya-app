import streamlit as st
from supabase import create_client
import pandas as pd
import os

# 1. Configuración de página
st.set_page_config(page_title="StockYa", page_icon="PiraB.PNG", layout="centered")

# 2. LIMPIEZA TOTAL DE INTERFAZ (CSS)
st.markdown("""
    <style>
    .stDeployButton, #stDecoration { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
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

col1, col2 = st.columns([4, 1])
with col1:
    cod = st.text_input("Buscar...", label_visibility="collapsed", placeholder="Código o Referencia").strip().upper()
with col2:
    buscar = st.button("🔍")

# 4. Lógica de Búsqueda y Resultados
if cod:
    try:
        # --- PASO 1: Bitácora de control ---
        res_ctrl = supabase.table("tblcontrolexistencias").select("tienda, ultimaactualizacion").execute()
        dict_sinc = {t['tienda']: t['ultimaactualizacion'] for t in res_ctrl.data}

        # --- PASO 2: Traemos existencias ---
        res_stock = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.ilike.%{cod}%,c_Modelo.ilike.%{cod}%").execute()
        
        if res_stock.data:
            items_validados = []
            for item in res_stock.data:
                t_nombre = item['name_tienda']
                fecha_item_raw = item.get('Ultima_Actualizacion')
                fecha_valida_raw = dict_sinc.get(t_nombre)
                
                if fecha_item_raw and fecha_valida_raw:
                    try:
                        f_item = pd.to_datetime(fecha_item_raw).replace(tzinfo=None, microsecond=0)
                        f_ctrl = pd.to_datetime(fecha_valida_raw).replace(tzinfo=None, microsecond=0)
                        diferencia = abs((f_item - f_ctrl).total_seconds())
                        
                        # TOLERANCIA DE TIEMPO: 4 HORAS (14400 segundos)
                        if diferencia < 14400:
                            items_validados.append(item)
                    except:
                        continue

            items_con_stock = [item for item in items_validados if int(item['n_cantidad']) > 0]
            
            if items_con_stock:
                st.subheader("Disponibilidad:")
                dias_semana = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]

                for item in items_con_stock:
                    referencia = str(item.get('c_Modelo', 'N/A')).strip()
                    descripcion = str(item.get('c_descripcion', 'N/A')).strip()
                    marca = str(item.get('c_Marca', 'N/A')).strip().upper()
                    precio = float(item.get('n_Precio1', 0.0))
                    codigo = str(item.get('c_codarticulo', 'N/A')).strip()
                    tienda_nombre = item['name_tienda']
                    cant = int(item['n_cantidad'])
                    
                    raw_fecha = dict_sinc.get(tienda_nombre, None)
                    sinc_txt = "---"
                    if raw_fecha:
                        try:
                            fecha_dt = pd.to_datetime(raw_fecha).replace(tzinfo=None)
                            sinc_txt = f"{dias_semana[fecha_dt.weekday()]} {fecha_dt.strftime('%d/%m/%Y %I:%M %p')}"
                        except:
                            sinc_txt = raw_fecha

                    emoji_stock = "✅" if cant > 3 else "⚠️"
                    
                    # --- DISEÑO LIMPIO SIN NBSP ---
                    html_card = f"""
                    <div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin-bottom: 20px;">
                        <div style="background-color: #f8f9fa; padding: 12px;">
                            <div style="font-weight: bold; color: #666; font-size: 0.85em; margin-bottom: 8px;">📦 PRODUCTO</div>
                            <div style="margin-bottom: 4px;"><b>Referencia:</b> {referencia}</div>
                            <div style="margin-bottom: 4px;"><b>Descripción:</b> {descripcion}</div>
                            <div style="margin-bottom: 4px;"><b>Marca:</b> {marca}</div>
                            <div style="font-size: 1.2em; color: #000; font-weight: bold; margin-top: 6px;">Precio: ${precio:,.2f}</div>
                        </div>
                        <div style="border-top: 1px solid #eee;"></div>
                        <div style="background-color: #ffffff; padding: 12px;">
                            <div style="font-weight: bold; color: #666; font-size: 0.85em; margin-bottom: 8px;">🏭 EXISTENCIA</div>
                            <div style="margin-bottom: 4px;"><b>Código:</b> {codigo}</div>
                            <div style="margin-bottom: 4px;"><b>Tienda:</b> {tienda_nombre}</div>
                            <div style="margin-bottom: 4px; font-weight: bold; font-size: 1.1em; color: #333;">Stock: {emoji_stock} {cant}</div>
                            <div style="margin-top: 8px; font-size: 0.8em; color: #999;"><b>Actualización:</b> {sinc_txt}</div>
                        </div>
                    </div>
                    """
                    st.markdown(html_card, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Sin stock reciente.")
        else:
            if buscar: st.error("📍 Producto no encontrado.")
            
    except Exception as e:
        st.error(f"Error: {e}")






































