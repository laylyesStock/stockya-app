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

if cod:
    try:
        # A. Bitácora de sincronización
        res_ctrl = supabase.table("tblcontrolexistencias").select("tienda, ultimaactualizacion").execute()
        dict_sinc = {str(t['tienda']).strip(): t['ultimaactualizacion'] for t in res_ctrl.data}

        # B. Obtener IDs de sesión más recientes por tienda
        res_sesiones = supabase.table("tblExistencias").select("name_tienda, sesion_id").execute()
        if res_sesiones.data:
            df_sesiones = pd.DataFrame(res_sesiones.data)
            dict_max_sesion = df_sesiones.groupby('name_tienda')['sesion_id'].max().to_dict()
        else:
            dict_max_sesion = {}

        # C. Buscamos el producto
        res_stock = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.ilike.%{cod}%,c_Modelo.ilike.%{cod}%").execute()
        
        if res_stock.data:
            df_raw = pd.DataFrame(res_stock.data)

            # --- PARCHE DE LIMPIEZA DE FANTASMAS ---
            # Solo permitimos filas que coincidan con la última sesión de su tienda
            def es_dato_nuevo(fila):
                t = str(fila['name_tienda']).strip()
                s_id = int(fila.get('sesion_id', 0))
                # Si es la última sesión conocida de esa tienda, es válido
                return s_id >= dict_max_sesion.get(t, 0)

            df_filtrado = df_raw[df_raw.apply(es_dato_nuevo, axis=1)]
            # Además, solo mostramos si la cantidad es mayor a 0
            df_final = df_filtrado[df_filtrado['n_cantidad'] > 0]

            if df_final.empty:
                st.warning("📍 Producto sin existencia.")
            else:
                # Agrupamos por código para mostrar la cabecera del producto
                for cod_art, grupo in df_final.groupby('c_codarticulo'):
                    primero = grupo.iloc[0]
                    
                    referencia = str(primero.get('c_Modelo', 'N/A')).strip()
                    descripcion = str(primero.get('c_descripcion', 'N/A')).strip()
                    marca = str(primero.get('c_Marca', 'N/A')).strip().upper()
                    
                    try:
                        val_precio = primero.get('n_Precio1')
                        precio = float(val_precio) if val_precio and not pd.isna(val_precio) else 0.0
                    except:
                        precio = 0.0

                    # Cabecera de Producto
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 15px; border: 1px solid #ddd; border-radius: 10px 10px 0 0; margin-top: 20px; font-family: sans-serif; color: #333 !important;">
                        <div style="font-weight: bold; color: #666 !important; font-size: 0.85em; margin-bottom: 8px;">📦 PRODUCTO</div>
                        <div style="margin-bottom: 4px; color: #333 !important;"><b>Referencia:</b> {referencia}</div>
                        <div style="margin-bottom: 4px; color: #333 !important;"><b>Descripción:</b> {descripcion}</div>
                        <div style="margin-bottom: 4px; color: #333 !important;"><b>Marca:</b> {marca}</div>
                        <div style="font-size: 1.2em; color: #000 !important; font-weight: bold; margin-top: 6px;">Precio: ${precio:,.2f}</div>
                    </div>""", unsafe_allow_html=True)

                    dias_semana = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
                    
                    # Bloque de Existencias (Solo las válidas)
                    for _, fila in grupo.iterrows():
                        tienda_limpia = str(fila['name_tienda']).strip()
                        cant = int(fila['n_cantidad'])
                        codigo_barras = str(fila.get('c_codarticulo', 'N/A')).strip()
                        
                        f_valida_raw = dict_sinc.get(tienda_limpia)
                        sinc_txt = "---"
                        
                        if f_valida_raw:
                            try:
                                f_dt = pd.to_datetime(f_valida_raw).replace(tzinfo=None)
                                sinc_txt = f"{dias_semana[f_dt.weekday()]} {f_dt.strftime('%d/%m/%Y %I:%M %p')}"
                            except:
                                sinc_txt = f_valida_raw

                        emoji_stock = "✅" if cant > 3 else "⚠️"
                        html_exis = f"""
                        <div style="background-color: #ffffff; padding: 15px; border: 1px solid #ddd; border-top: none; margin-bottom: 2px; font-family: sans-serif; color: #333 !important;">
                            <div style="font-weight: bold; color: #666 !important; font-size: 0.85em; margin-bottom: 8px;">🏭 EXISTENCIA</div>
    
                            <div style="margin-bottom: 6px; color: #333 !important;">
                                <b>Código:</b> <span style="color: #333 !important;">{codigo_barras}</span>
                            </div>
        
                            <div style="margin-bottom: 6px; color: #333 !important;">
                                <b>Tienda:</b> <span style="color: #007bff !important; font-weight: bold; font-size: 1.1em;">{tienda_limpia}</span>
                            </div>
        
                            <div style="margin-bottom: 6px; font-weight: bold; color: #333 !important;">
                                Stock: {emoji_stock} {cant}
                            </div>
        
                            <div style="margin-top: 10px; font-size: 0.85em; color: #888 !important; border-top: 1px dashed #eee; padding-top: 5px;">
                                <b>Actualización:</b> {sinc_txt}
                            </div>
                        </div>"""
                        st.markdown(html_exis, unsafe_allow_html=True)
                    
                    st.write("") 

        else:
            if buscar: st.error("📍 Producto no encontrado.")
            
    except Exception as e:
        st.error(f"Error: {e}")














































