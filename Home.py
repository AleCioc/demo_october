import streamlit as st
import pandas as pd

from utils import add_logo


st.set_page_config(
    layout="wide"
)

add_logo()

st.header("Benvenut*!")

st.subheader("Naviga il menu a sinistra per guardare i risultati delle analisi.")

st.markdown(
    """

I risultati sono così organizzati:

- **Dimensionamento Flotta**
    - Scegli il numero di veicoli che soddisfa meglio la tua domanda di mobilità e i tuoi vincoli operativi
    - Confronta diverse metriche con numero di veicoli variabile
- **Dimensionamento Ricarica**
    - Scegli il numero di stazioni di rifornimento/ricarica necessario ad alimentare i tuoi veicoli
- **Parcheggi**
    - Analizza come si distribuiscono i parcheggi nella tua zona operativa
    - Identifica zone di parcheggio critiche
- **Stazioni di ricarica**
    - Identifica zone dove è più importante posizionare le tue stazioni di ricarica
    - Analizza l'impatto della disposizione della stazioni sulla domanda insoddisfatta degli utenti
    """

)
