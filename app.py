import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="TLAG Dashboard", layout="wide")

st.title("🚀 TLAG PERFORMANCE DASHBOARD")
st.success("✅ Dashboard başarıyla deploy edildi!")

# Simple test data
data = {
    'İstasyon': ['KASTAMONU', 'SAMSUN', 'ANKARA', 'İSTANBUL', 'İZMİR'], 
    'Skor': [0.75, 0.82, 0.68, 0.91, 0.77],
    'Bölge': ['KUZEY', 'KUZEY', 'MERKEZ', 'MARMARA', 'EGE'],
    'Segment': ['My Precious', 'My Precious', 'Wasted Talent', 'My Precious', 'Saboteur']
}
df = pd.DataFrame(data)

st.markdown("## 📊 Test Verileri")
st.dataframe(df, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(df, x='İstasyon', y='Skor', title="İstasyon Performansı")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(df, names='Segment', title="Segment Dağılımı")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("## 📈 Bu Sadece Test Versiyonu")
st.info("Excel upload özelliği bir sonraki adımda eklenecek!")