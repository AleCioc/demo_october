import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.sidebar.image("SWITCH - Logo.png", use_column_width=True)

st.header("Dimensionamento flotta")

sim_stats_df = pd.read_csv(
    "results/Roma/multiple_runs/enjoy_fleet_test/sim_stats.csv",
    index_col=0
)

st.subheader("Risultati completi")
with st.expander("Clicca per vedere i risultati completi"):
    st.dataframe(sim_stats_df)

sim_stats_df.n_vehicles_sim = sim_stats_df.n_vehicles_sim.astype(float)

st.subheader("Domanda insoddisfatta [%]")
unsatisfied_by_n_vehicles = sim_stats_df.set_index("n_vehicles_sim").sort_index().percentage_unsatisfied.astype(float)
st.bar_chart(unsatisfied_by_n_vehicles)

# st.subheader("Emissioni di CO2 [kg]")
# co2_by_n_vehicles = sim_stats_df.set_index("n_vehicles_sim").sort_index().tot_co2_emissions_kg.astype(float)
# st.bar_chart(co2_by_n_vehicles)

st.subheader("Profitto dell'operatore [€]")
profit_by_n_vehicles = sim_stats_df.set_index("n_vehicles_sim").sort_index().profit.astype(float)
st.bar_chart(profit_by_n_vehicles)

# unsatisfied_by_n_vehicles
# fig, ax = plt.subplots(figsize=(15, 8))
# unsatisfied_by_n_vehicles.plot.bar()
# st.pyplot(fig)
