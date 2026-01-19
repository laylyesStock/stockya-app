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

if st.button("BUSCAR"):
    if cod or ref:
        columna = "c_codarticulo" if cod else "c_Modelo"
        valor = cod if cod else ref
        
        try:
            res = supabase.table("tblExistencias").select("*").ilike(columna, f"%{valor}%").execute()
            
            if res.data:
                st.subheader("Resultados de Inventario")
                for item in res.data:
                    cant = int(item['n_cantidad'])
                    tienda = item['name_tienda']
                    desc = item['c_descripcion']
                    
                    # Lógica de colores (Semáforo de stock)
                    if cant <= 0:
                        st.error(f"❌ {tienda} | {desc} | AGOTADO")
                    elif cant <= 3:
                        st.warning(f"⚠️ {tienda} | {desc} | CRÍTICO: {cant}")
                    else:
                        st.success(f"✅ {tienda} | {desc} | DISPONIBLE: {cant}")
            else:
                st.warning("No se encontraron coincidencias.")
        except Exception as e:
            st.error("Error en la búsqueda. Revisa la conexión.")
    else:
        st.warning("Por favor, introduce un código o referencia.")




