import streamlit as st
from supabase import create_client

# 1. Configuración
URL = "https://darvsiqglsyfistdmweh.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcnZzaXFnbHN5ZmlzdGRtd2VoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgyNDA2MjUsImV4cCI6MjA4MzgxNjYyNX0.4jrpYr2Sg1UC8o2Y7iMO0gbw6U8v28-eQSQrH4fXYRA"

supabase = create_client(URL, KEY)

# 2. Interfaz básica
st.title("StockYa ⚡")
st.image("PiraB.png", width=200) # Asegúrate que sea .png o .PNG según lo cambiaste
st.write("---")

col1, col2 = st.columns(2)
with col1:
    cod = st.text_input("Código").strip().upper()
with col2:
    ref = st.text_input("Referencia").strip().upper()

if st.button("BUSCAR"):
    if cod or ref:
        columna = "c_codarticulo" if cod else "c_Modelo"
        valor = cod if cod else ref
        
        res = supabase.table("tblExistencias").select("*").ilike(columna, f"%{valor}%").execute()
        
        if res.data:
            for item in res.data:
                st.info(f"📍 {item['name_tienda']} | {item['c_descripcion']} | Cant: {int(item['n_cantidad'])}")
        else:
            st.warning("No hay resultados")

