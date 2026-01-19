import streamlit as st
from supabase import create_client
import os

# 1. Configuración de Supabase
URL = "https://darvsiqglsyfistdmweh.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcnZzaXFnbHN5ZmlzdGRtd2VoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgyNDA2MjUsImV4cCI6MjA4MzgxNjYyNX0.4jrpYr2Sg1UC8o2Y7iMO0gbw6U8v28-eQSQrH4fXYRA"
supabase = create_client(URL, KEY)

# 2. Cabecera y Logo (Solución definitiva)
st.title("StockYa ⚡")

# Esto busca el archivo se llame como se llame en Git
if os.path.exists("PiraB.PNG"):
    st.image("PiraB.PNG", width=200)
elif os.path.exists("PiraB.png"):
    st.image("PiraB.png", width=200)
else:
    st.subheader("Pirámide C.A.") # Texto por si el logo falla

st.write("---")

# 3. Buscador
col1, col2 = st.columns(2)
with col1:
    cod = st.text_input("Código").strip().upper()
with col2:
    ref = st.text_input("Referencia").strip().upper()

# 4. Botón con Lupa y Lógica de Búsqueda
if st.button("🔍"):
    if cod or ref:
        columna = "c_codarticulo" if cod else "c_Modelo"
        valor = cod if cod else ref    
        try:
            res = supabase.table("tblExistencias").select("*").ilike(columna, f"%{valor}%").execute()
            
            if res.data:
                st.subheader("Resultados:")
                # Usamos enumerate para saber el número de fila y alternar color
                for i, item in enumerate(res.data):
                    cant = int(item['n_cantidad'])
                    tienda = item['name_tienda']
                    desc = item['c_descripcion']
                    
                    # Definimos el color del texto según stock
                    if cant <= 0:
                        emoji, texto_stock, color_texto = "❌", "AGOTADO", "#ff4b4b" # Rojo
                    elif cant <= 3:
                        emoji, texto_stock, color_texto = "⚠️", f"STOCK CRÍTICO: {cant}", "#ffa500" # Naranja/Amarillo
                    else:
                        emoji, texto_stock, color_texto = "✅", f"DISPONIBLE: {cant}", "#09ab3b" # Verde
                    
                    # Truco de color de fondo alternado (estilo Excel)
                    fondo = "#f0f2f6" if i % 2 == 0 else "#ffffff"
                    
                    # Dibujamos la fila con HTML
                    st.markdown(f"""
                        <div style="background-color: {fondo}; padding: 10px; border-radius: 5px; margin-bottom: 5px; border: 1px solid #e6e9ef;">
                            <span style="color: #31333F; font-weight: bold;">{tienda}</span> | 
                            <span style="color: #555;">{desc}</span> | 
                            <span style="color: {color_texto}; font-weight: bold;">{emoji} {texto_stock}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No se encontraron coincidencias.")
        except Exception as e:
            st.error("Error en la búsqueda.")
    else:
        st.warning("Introduce un Código o Referencia.")





