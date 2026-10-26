import streamlit as st
from supabase import create_client
import pandas as pd
import os
import re

# 1. Configuración de página
st.set_page_config(page_title="StockYa", page_icon="PiraB.PNG", layout="centered")

# --- LISTA OFICIAL DE TALLAS TEXTILES ---
ORDEN_TALLAS_LETRAS = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

# --- CARGA DEL CATÁLOGO DE COLORES EN MEMORIA (UNA SOLA VEZ) ---
@st.cache_data
def cargar_catalogo_colores(ruta_txt="colores.txt"):
    diccionario_colores = {}
    if not os.path.exists(ruta_txt):
        return {}, []

    with open(ruta_txt, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or "|" not in linea:
                continue
            partes = linea.split("|", 1)
            cod_col = partes[0].strip().upper()
            nombre = partes[1].strip().upper()
            if cod_col:
                diccionario_colores[cod_col] = nombre

    colores_ordenados = sorted(diccionario_colores.keys(), key=len, reverse=True)
    return diccionario_colores, colores_ordenados

DICT_COLORES, LISTA_COLORES_ORDENADOS = cargar_catalogo_colores("colores.txt")

def descomponer_modelo(modelo_raw, colores_ordenados):
    if not modelo_raw:
        return None, None, None

    modelo = str(modelo_raw).strip().upper()

    # 1. Exclusión estricta de Surtidos
    if "STSUR" in modelo or "STSU" in modelo:
        return None, None, None

    # 2. Extraer talla al extremo derecho (primero letras, luego números de 2 dígitos)
    talla_detectada = None
    texto_sin_talla = modelo

    tallas_letras_por_longitud = sorted(ORDEN_TALLAS_LETRAS, key=len, reverse=True)
    for t_letra in tallas_letras_por_longitud:
        if modelo.endswith(t_letra):
            talla_detectada = t_letra
            texto_sin_talla = modelo[:-len(t_letra)]
            break

    if not talla_detectada:
        match_num = re.search(r"(\d{2})$", modelo)
        if match_num:
            talla_detectada = match_num.group(1)
            texto_sin_talla = modelo[:-2]

    if not talla_detectada:
        return None, None, None

    # 3. Extraer color por coincidencia con catálogo oficial
    color_detectado = None
    raiz_modelo = None

    for col in colores_ordenados:
        if texto_sin_talla.endswith(col):
            color_detectado = col
            raiz_modelo = texto_sin_talla[:-len(col)]
            break

    if not color_detectado or not raiz_modelo:
        return None, None, None

    return raiz_modelo, color_detectado, talla_detectada

def criterio_orden_talla(talla):
    talla_str = str(talla).strip().upper()
    if talla_str in ORDEN_TALLAS_LETRAS:
        return (0, ORDEN_TALLAS_LETRAS.index(talla_str))
    try:
        return (1, int(talla_str))
    except ValueError:
        return (2, talla_str)

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
    /* Estilos de la Corrida Horizontal de Tallas */
    .contenedor-corrida {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0 6px 0;
    }
    .caja-talla {
        background-color: var(--background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 6px 12px;
        text-align: center;
        min-width: 58px;
    }
    .caja-talla-activa {
        border: 2px solid #1E88E5 !important;
        background-color: rgba(30, 136, 229, 0.12) !important;
    }
    .talla-label {
        font-size: 0.82em;
        font-weight: bold;
    }
    .talla-cant {
        font-size: 0.95em;
        font-weight: bold;
        color: #1E88E5;
    }
    .talla-agotada {
        opacity: 0.45;
    }
    .talla-agotada .talla-cant {
        color: inherit !important;
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
            res_stock = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.eq.{cod},c_Modelo.eq.{cod}").execute()
        else:
            res_stock = supabase.table("tblExistencias").select("*").or_(f"c_codarticulo.eq.{cod},c_Modelo.ilike.%{cod}%").execute()

        if res_stock.data:
            df_raw = pd.DataFrame(res_stock.data)

            def es_dato_nuevo(fila):
                try:
                    t = str(fila['name_tienda']).strip()
                    s_id = int(fila.get('sesion_id', 0)) if pd.notna(fila.get('sesion_id')) else 0
                    return s_id >= dict_max_sesion.get(t, 0)
                except:
                    return True

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

                    ref_limpia = referencia.upper()
                    es_exacto = cod.isdigit() or (cod.strip() == ref_limpia.strip())

                    if not es_exacto:
                        st.warning(f"⚠️ **Coincidencia parcial:** Se muestra **{referencia}** porque contiene tu búsqueda **'{cod}'**.")

                    # --- ROTACIÓN ---
                    dict_ventas_tienda = {}
                    total_cadena = 0
                    ritmo_cadena = 0.0
                    html_rotacion_global = ""

                    if es_exacto:
                        try:
                            res_ventas = supabase.table("tblventas30d").select("name_tienda, cant_vendida_15d").eq("c_codarticulo", str(cod_art).strip()).execute()
                            if res_ventas.data:
                                for v in res_ventas.data:
                                    t_nom = str(v.get('name_tienda', '')).strip()

                                    if "DISTRIBUIDORA" in t_nom.upper():
                                        continue

                                    c_v = int(v.get('cant_vendida_15d', 0))
                                    dict_ventas_tienda[t_nom] = c_v
                                    total_cadena += c_v

                                ritmo_cadena = round(total_cadena / 15.0, 1)
                        except Exception:
                            pass

                        html_rotacion_global = f'<div class="badge-rotacion">📊 Ventas tiendas (15d): <b>{total_cadena} und</b> | Ritmo: <b>{ritmo_cadena} und/día</b></div>'

                    # --- CORRIDA DE TALLAS ---
                    html_corrida_tallas = ""
                    txt_color_header = ""

                    raiz_mod, cod_color, talla_actual = descomponer_modelo(referencia, LISTA_COLORES_ORDENADOS)
                    st.info(f"🔍 DEBUG: Ref='{referencia}' | Raiz='{raiz_mod}' | Color='{cod_color}' | Talla='{talla_actual}' | Colores cargados={len(LISTA_COLORES_ORDENADOS)}")

                    if raiz_mod and cod_color and es_exacto:
                        nombre_color_desc = DICT_COLORES.get(cod_color, cod_color)
                        txt_color_header = f' | <b>Color:</b> {nombre_color_desc} ({cod_color})'
                        prefijo_busqueda = f"{raiz_mod}{cod_color}"

                        try:
                            res_hermanas = supabase.table("tblExistencias").select("c_Modelo, n_cantidad, name_tienda, sesion_id").ilike("c_Modelo", f"{prefijo_busqueda}%").execute()
                            
                            dict_cantidades_talla = {}

                            if res_hermanas.data:
                                df_herm = pd.DataFrame(res_hermanas.data)
                                df_herm = df_herm[df_herm.apply(es_dato_nuevo, axis=1)]
                                df_herm = df_herm[df_herm['n_cantidad'] > 0]

                                for _, f_herm in df_herm.iterrows():
                                    mod_herm = f_herm.get('c_Modelo')
                                    r_h, c_h, t_h = descomponer_modelo(mod_herm, LISTA_COLORES_ORDENADOS)
                                    if r_h == raiz_mod and c_h == cod_color and t_h:
                                        cant_h = int(f_herm.get('n_cantidad', 0))
                                        dict_cantidades_talla[t_h] = dict_cantidades_talla.get(t_h, 0) + cant_h

                            # Oñemoinge talla ko'ag̃agua oĩ meme hag̃ua
                            if talla_actual not in dict_cantidades_talla:
                                dict_cantidades_talla[talla_actual] = int(grupo['n_cantidad'].sum())

                            if len(dict_cantidades_talla) > 0:
                                tallas_ordenadas = sorted(dict_cantidades_talla.keys(), key=criterio_orden_talla)

                                bloques_tallas = []
                                for t_item in tallas_ordenadas:
                                    es_activa = (t_item == talla_actual)
                                    clase_activa = " caja-talla-activa" if es_activa else ""
                                    estrella = " ★" if es_activa else ""
                                    cant_total_talla = dict_cantidades_talla.get(t_item, 0)
                                    clase_agotada = " talla-agotada" if cant_total_talla == 0 else ""

                                    bloques_tallas.append(
                                        f'<div class="caja-talla{clase_activa}{clase_agotada}">'
                                        f'<div class="talla-label">T.{t_item}{estrella}</div>'
                                        f'<div class="talla-cant">({cant_total_talla})</div>'
                                        f'</div>'
                                    )

                                html_corrida_tallas = (
                                    f'<div style="margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--border-color);">'
                                    f'<div class="subtexto">📐 CORRIDA DE TALLAS — {nombre_color_desc} ({cod_color})</div>'
                                    f'<div class="contenedor-corrida">{"".join(bloques_tallas)}</div>'
                                    f'</div>'
                                )
                        except Exception:
                            pass

                    # Cabecera de Producto
                    st.markdown(
                        f'<div class="card-producto">'
                        f'<div class="subtexto">📦 PRODUCTO</div>'
                        f'<div style="padding-bottom: 4px;"><b>Referencia:</b> {referencia}</div>'
                        f'<div style="padding-bottom: 4px;"><b>Descripción:</b> {descripcion}</div>'
                        f'<div style="padding-bottom: 4px;"><b>Marca:</b> {marca}{txt_color_header}</div>'
                        f'<div style="font-size: 1.2em; font-weight: bold; margin-top: 6px;">Precio: ${precio:,.2f}</div>'
                        f'{html_rotacion_global}'
                        f'{html_corrida_tallas}'
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

                        html_rotacion_tienda = ""
                        if es_exacto and "DISTRIBUIDORA" not in tienda_limpia.upper():
                            v_tienda = dict_ventas_tienda.get(tienda_limpia, 0)
                            ritmo_t = round(v_tienda / 15.0, 1)

                            if v_tienda > 0:
                                dias_cob = int(cant / (v_tienda / 15.0))
                                txt_cobertura = f"⏱️ Cobertura: <b>~{dias_cob} días</b>"
                            else:
                                txt_cobertura = "⏱️ Cobertura: <b>Estancado</b>"

                            html_rotacion_tienda = (
                                f'<div style="padding-bottom: 2px; font-size: 0.9em; opacity: 0.9;">'
                                f'📈 <b>Ventas 15d:</b> {v_tienda} und ({ritmo_t}/día)'
                                f'</div>'
                                f'<div style="padding-bottom: 6px; font-size: 0.9em; opacity: 0.9;">'
                                f'{txt_cobertura}'
                                f'</div>'
                            )

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
            if buscar:
                st.error("📍 Producto no encontrado.")

    except Exception as e:
        st.error(f"⚠️ Sincronizando datos con los servidores locales... Por favor, intente la búsqueda de nuevo en unos instantes.")
