# pip install streamlit

import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache
def get_data():
    url = "http://data.insideairbnb.com/the-netherlands/north-holland/amsterdam/2022-09-07/visualisations/listings.csv"
    return pd.read_csv(url)
df = get_data()

st.title("Streamlit tutorial: Usando Streamlit")
st.markdown("Este tutorial muestra como usar Streamlit para mostrar datos de Airbnb.")
st.header("Airbnb")
st.markdown("Datos de Amsterdam 2022")

st.dataframe(df.head())