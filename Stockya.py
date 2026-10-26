import streamlit as st
from supabase import create_client
import pandas as pd
import os

# 1. Configuración de página
st.set_page_config(page_title="StockYa", page_icon="PiraB.PNG", layout="centered")

# 2. LIMPIEZA TOTAL DE INTERFAZ Y ADAPTACIÓN A MODO OSCURO / CLARO
st.markdown("""
    <style>
    .stDeployButton, #stDecoration { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    header { background-color: transparent !important; height: 1rem !important; }
    .block-container { padding-top: 1rem !important; }

    /* Tarjetas adaptables automáticamente según el tema del teléfono */
    .card-producto {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 15px;
        border: 1px solid var(--border-color);
        border-radius: 10px 10px 0 0;
        margin-top: 20px;
        font-family: sans-serif;
    }
    .card-existencia {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 15px;
        border: 1px solid var(--border-color);
        border-top: none;
        margin-bottom: 2px;
        font-family: sans-serif;
    }
    .subtexto {
        font-weight: bold;
        opacity: 0.7;
        font-size: 0.85em;
        margin-bottom: 8px;
    }
    .tienda-highlight {
        color: #1E88E5 !important;
        font-weight: bold;
        font-size: 1.1em;
    }
    .footer-sinc {
        margin-top: 10px;
        font-size: 0.85em;
        opacity: 0.6;
        border-top: 1px dashed var(--border-color);
        padding-top: 5px;
    }
    .badge-rotacion {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.88em;
        font-weight: bold;
        margin-top: 8px;
        background-color: rgba(30, 136, 229, 0.15);
        border: 1px solid rgba(30, 136, 229, 0.35);
    }
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
    cod = st.text_input(
        "Buscar...",
        label_visibility="collapsed",
        placeholder="Código o Referencia",
        help="ℹ️ Solo se muestra mercancía con existencia física activa (> 0). Si un modelo no aparece, está agotado."
    ).strip().upper()
with col2:
    buscar = st.button("🔍")

if cod:
    try:
        # A. Bitácora de sincronización
        res_ctrl = supabase.table("tblcontrolexistencias").select("tienda, ultimaactualizacion").execute()
        dict_sinc = {}
        if res_ctrl.data:
            dict_sinc = {str(t['tienda']).strip(): t['ultimaactualizacion'] for t in res_ctrl.data}

        # B. Obtener IDs de sesión más recientes por tienda de forma segura
        res_sesiones = supabase.table("tblExistencias").select("name_tienda, sesion_id").execute()
        dict_max_sesion = {}
        if res_sesiones.data:
            df_sesiones = pd.DataFrame(res_sesiones.data)
            if not df_sesiones.empty and 'sesion_id' in df_sesiones.columns:
                df_sesiones['sesion_id'] = pd.to_numeric(df_sesiones['sesion_id'], errors='coerce').fillna(0).astype(int)
                dict_max_sesion = df_sesiones.groupby('name_tienda')['sesion_id'].max().to_dict()

        # C. Buscamos el producto con lógica inteligente para evitar cruces
        if cod.isdigit():
            # Si introducen números limpios (Código de barra), coincidencia exacta estricta
            res_stock = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.eq.{cod},c_Modelo.eq.{cod}").execute()
        else:
            # Si incluye letras, es referencia/modelo, usamos coincidencia parcial flexible
            res_stock = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.eq.{cod},c_Modelo.ilike.%{cod}%").execute()

        if res_stock.data:
            df_raw = pd.DataFrame(res_stock.data)

            # --- PARCHE DE LIMPIEZA DE FANTASMAS PROTEGIDO ---









































