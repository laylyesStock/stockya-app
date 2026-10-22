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
            def es_dato_nuevo(fila):
                try:
                    t = str(fila['name_tienda']).strip()
                    s_id = int(fila.get('sesion_id', 0)) if pd.notna(fila.get('sesion_id')) else 0
                    return s_id >= dict_max_sesion.get(t, 0)
                except:
                    return True  # En caso de duda dejamos pasar el registro para no congelar la app

            df_filtrado = df_raw[df_raw.apply(es_dato_nuevo, axis=1)]
            df_final = df_filtrado[df_filtrado['n_cantidad'] > 0]

            if df_final.empty:
                st.warning("📍 Producto sin existencia.")
            else:
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

                    # --- ADVERTENCIA DE COINCIDENCIA PARCIAL ---
                    ref_limpia = referencia.upper()
                    es_exacto = cod.isdigit() or (cod == ref_limpia)

                    if not es_exacto:
                        st.warning(f"⚠️ **Coincidencia parcial:** Se muestra **{referencia}** porque contiene tu búsqueda **'{cod}'**.")

                    # --- CONSULTA DE ROTACIÓN: SOLO SI LA BÚSQUEDA ES EXACTA ---
                    dict_ventas_tienda = {}
                    html_rotacion_global = ""

                    if es_exacto:
                        try:
                            res_ventas = supabase.table("tblventas30d").select("name_tienda, cant_vendida_30d").eq("c_codarticulo", str(cod_art).strip()).execute()
                            if res_ventas.data:
                                total_cadena = 0
                                for v in res_ventas.data:
                                    t_nom = str(v.get('name_tienda', '')).strip()
                                    
                                    # Exclusión de Distribuidora (solo tiendas minoristas)
                                    if "DISTRIBUIDORA" in t_nom.upper():
                                        continue

                                    c_v = int(v.get('cant_vendida_30d', 0))
                                    dict_ventas_tienda[t_nom] = c_v
                                    total_cadena += c_v
                                
                                ritmo_cadena = round(total_cadena / 15.0, 1)
                                html_rotacion_global = f'<div class="badge-rotacion">📊 Ventas tiendas (15d): <b>{total_cadena} und</b> | Ritmo: <b>{ritmo_cadena} und/día</b></div>'
                        except Exception:
                            pass

                    # Cabecera de Producto
                    st.markdown(
                        f'<div class="card-producto">'
                        f'<div class="subtexto">📦 PRODUCTO</div>'
                        f'<div style="padding-bottom: 4px;"><b>Referencia:</b> {referencia}</div>'
                        f'<div style="padding-bottom: 4px;"><b>Descripción:</b> {descripcion}</div>'
                        f'<div style="padding-bottom: 4px;"><b>Marca:</b> {marca}</div>'
                        f'<div style="font-size: 1.2em; font-weight: bold; margin-top: 6px;">Precio: ${precio:,.2f}</div>'
                        f'{html_rotacion_global}'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    dias_semana = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
                    
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
                        
                        # Bloque de rotación por tienda (solo si fue exacto y no es Distribuidora)
                        # Bloque de rotación por tienda (solo si fue exacto y no es Distribuidora)
                        html_rotacion_tienda = ""
                        if es_exacto and "DISTRIBUIDORA" not in tienda_limpia.upper():
                            v_tienda = dict_ventas_tienda.get(tienda_limpia, 0)
                            ritmo_t = round(v_tienda / 15.0, 1)

                            # Cálculo de cobertura sin etiquetas de velocidad
                            if v_tienda > 0:
                                dias_cob = int(cant / (v_tienda / 15.0))
                                txt_cobertura = f"⏱️ Cobertura: <b>~{dias_cob} días</b>"
                            else:
                                txt_cobertura = "⏱️ Cobertura: <b>Estancado</b>"

                            html_rotacion_tienda = (
                                f'<div style="padding-bottom: 2px; font-size: 0.9em; opacity: 0.9;">'
                                f'📈 <b>Ventas 30d:</b> {v_tienda} und ({ritmo_t}/día)'
                                f'</div>'
                                f'<div style="padding-bottom: 6px; font-size: 0.9em; opacity: 0.9;">'
                                f'{txt_cobertura}'
                                f'</div>'
                            )
                        # Bloque de Existencia continuo (sin sangría que active bloques de código preformateado)
                        html_exis = (
                            f'<div class="card-existencia">'
                            f'<div class="subtexto">🏭 EXISTENCIA</div>'
                            f'<div style="padding-bottom: 6px;"><b>Código:</b> <span>{codigo_barras}</span></div>'
                            f'<div style="padding-bottom: 6px;"><b>Tienda:</b> <span class="tienda-highlight">{tienda_limpia}</span></div>'
                            f'<div style="padding-bottom: 6px; font-weight: bold;">Stock: {emoji_stock} {cant}</div>'
                            f'{html_rotacion_tienda}'
                            f'<div class="footer-sinc"><b>Actualización:</b> <span>{sinc_txt}</span></div>'
                            f'</div>'
                        )
                        st.markdown(html_exis, unsafe_allow_html=True)

                    st.write("") 

        else:
            if buscar: st.error("📍 Producto no encontrado.")
            
    except Exception as e:
        st.error(f"⚠️ Sincronizando datos con los servidores locales... Por favor, intente la búsqueda de nuevo en unos instantes.")









































