import streamlit as st
import pandas as pd

from utils import add_logo


st.set_page_config(
    layout="wide"
)

add_logo()

st.header("Benvenut*!")

st.text("Naviga il menu a sinistra per guardare i risultati delle analisi.")

