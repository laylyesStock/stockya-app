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

st.title("StockYa ⚡")

if os.path.exists("PiraB.PNG"): st.image("PiraB.PNG", width=180)
st.markdown("---")

col1, col2 = st.columns([4, 1])
with col1:
    cod = st.text_input("Buscar...", label_visibility="collapsed", placeholder="Código o Referencia").strip().upper()
with col2:
    buscar = st.button("🔍")

if cod:
    try:
        res_ctrl = supabase.table("tblcontrolexistencias").select("tienda, ultimaactualizacion").execute()
        dict_sinc = {t['tienda']: t['ultimaactualizacion'] for t in res_ctrl.data}

        res_stock = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.ilike.%{cod}%,c_Modelo.ilike.%{cod}%").execute()
        
        if res_stock.data:
            # --- AGRUPACIÓN POR PRODUCTO ---
            # Agrupamos por c_codarticulo para no repetir la cabecera
            df_resultados = pd.DataFrame(res_stock.data)
            
            for cod_art, grupo in df_resultados.groupby('c_codarticulo'):
                # Tomamos los datos del primer item del grupo para la cabecera de PRODUCTO
                primero = grupo.iloc[0]
                
                referencia = str(primero.get('c_Modelo', 'N/A')).strip()
                descripcion = str(primero.get('c_descripcion', 'N/A')).strip()
                marca = str(primero.get('c_Marca', 'N/A')).strip().upper()
                precio = float(primero.get('n_Precio1', 0.0))

                # --- DIBUJAMOS LA SECCIÓN PRODUCTO (UNA SOLA VEZ) ---
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 15px; border: 1px solid #ddd; border-radius: 10px 10px 0 0; margin-top: 20px;">
                    <div style="font-weight: bold; color: #666; font-size: 0.85em; margin-bottom: 8px;">📦 PRODUCTO</div>
                    <div style="margin-bottom: 4px;"><b>Referencia:</b> {referencia}</div>
                    <div style="margin-bottom: 4px;"><b>Descripción:</b> {descripcion}</div>
                    <div style="margin-bottom: 4px;"><b>Marca:</b> {marca}</div>
                    <div style="font-size: 1.2em; color: #000; font-weight: bold; margin-top: 6px;">Precio: ${precio:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

                # --- DIBUJAMOS LAS EXISTENCIAS (UNA DEBAJO DE OTRA) ---
                dias_semana = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
                
                for _, fila in grupo.iterrows():
                    tienda = fila['name_tienda']
                    cant = int(fila['n_cantidad'])
                    codigo_barras = str(fila.get('c_codarticulo', 'N/A')).strip()
                    
                    # Validar tiempo de sincronización (4 horas)
                    f_valida_raw = dict_sinc.get(tienda)
                    sinc_txt = "---"
                    es_valido = False
                    
                    if f_valida_raw:
                        f_ctrl = pd.to_datetime(f_valida_raw).replace(tzinfo=None)
                        ahora = pd.Timestamp.now().replace(microsecond=0)
                        if abs((ahora - f_ctrl).total_seconds()) < 14400: # 4 horas
                            es_valido = True
                            sinc_txt = f"{dias_semana[f_ctrl.weekday()]} {f_ctrl.strftime('%d/%m/%Y %I:%M %p')}"

                    if es_valido and cant > 0:
                        emoji_stock = "✅" if cant > 3 else "⚠️"
                        st.markdown(f"""
                        <div style="background-color: #ffffff; padding: 15px; border: 1px solid #ddd; border-top: none; margin-bottom: 2px;">
                            <div style="font-weight: bold; color: #666; font-size: 0.85em; margin-bottom: 8px;">🏭 EXISTENCIA</div>
                            <div style="margin-bottom: 4px;"><b>Código:</b> {codigo_barras}</div>
                            <div style="margin-bottom: 4px;"><b>Tienda:</b> {tienda}</div>
                            <div style="margin-bottom: 4px; font-weight: bold; font-size: 1.1em; color: #333;">Stock: {emoji_stock} {cant}</div>
                            <div style="margin-top: 8px; font-size: 0.8em; color: #999;"><b>Actualización:</b> {sinc_txt}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Espacio al final de cada bloque de producto
                st.write("")

        else:
            if buscar: st.error("📍 Producto no encontrado.")
            
    except Exception as e:
        st.error(f"Error: {e}")






































