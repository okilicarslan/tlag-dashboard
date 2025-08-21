import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="TLAG Dashboard", layout="wide")
st.title("🚀 TLAG PERFORMANCE DASHBOARD")
st.write("Dashboard başarıyla deploy edildi!")

# Simple test data
data = {
    'İstasyon': ['Test1', 'Test2', 'Test3'], 
    'Skor': [0.75, 0.82, 0.68]
}
df = pd.DataFrame(data)

st.dataframe(df)

fig = px.bar(df, x='İstasyon', y='Skor')
st.plotly_chart(fig)