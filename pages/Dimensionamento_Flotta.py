import streamlit as st
import pandas as pd

from utils import add_logo

st.set_page_config(layout="wide")

add_logo()

st.header("Dimensionamento flotta")

chosen_simulation = st.selectbox("Seleziona scenario:", options=[
    "fleet_dim_fuel", "fleet_dim_ev"
])

sim_stats_df = pd.read_csv(
    "results/Roma/multiple_runs/{}/sim_stats.csv".format(chosen_simulation),
    index_col=0
).rename(columns={"washing": "washing_cost"})

st.subheader("Risultati completi")
with st.expander("Clicca per vedere i risultati completi"):
    st.dataframe(sim_stats_df)

sim_stats_df.n_vehicles_sim = sim_stats_df.n_vehicles_sim.astype(float)

import altair as alt
import pandas as pd

st.subheader("Domanda insoddisfatta [%]")

unsatisfied_by_n_vehicles = sim_stats_df[[
    "n_vehicles_sim", "percentage_unsatisfied"
]]
altair_fig = alt.Chart(unsatisfied_by_n_vehicles).mark_bar(width=15).encode(
    x=alt.X('n_vehicles_sim', scale=alt.Scale(domain=[0, 1020])),
    y='percentage_unsatisfied',
    tooltip=["n_vehicles_sim", "percentage_unsatisfied"]
).interactive()
st.altair_chart(altair_fig, use_container_width=True)

st.subheader("Emissioni di CO2 [kg]")

co2_by_n_vehicles = sim_stats_df[[
    "n_vehicles_sim", "tot_welltotank_co2_emissions", "tot_tanktowheel_co2_emissions"
]].rename(columns={
    "tot_welltotank_co2_emissions": "WellToTank",
    "tot_tanktowheel_co2_emissions": "TankToWheel"
})
co2_by_n_vehicles["sim_stats_idx"] = co2_by_n_vehicles.index.values

co2_by_n_vehicles = pd.melt(
    co2_by_n_vehicles,
    id_vars="n_vehicles_sim",
    value_vars=["WellToTank", "TankToWheel"]
).rename(columns={"value": "co2_emissions", "variable": "well_to_weel_period"})

altair_fig = alt.Chart(co2_by_n_vehicles).mark_bar(
    width=12, opacity=0.9
).encode(
    x=alt.X('n_vehicles_sim', scale=alt.Scale(domain=[0, 1020])),
    y=alt.Y('co2_emissions:Q', stack=True),
    color=alt.Color(field='well_to_weel_period', scale=alt.Scale(scheme="greys")),
    tooltip=["n_vehicles_sim", "co2_emissions", "well_to_weel_period"]
).interactive()
st.altair_chart(altair_fig, use_container_width=True)

#co2_by_n_vehicles = sim_stats_df.set_index("n_vehicles_sim").sort_index().tot_co2_emissions_kg.astype(float)
#st.bar_chart(co2_by_n_vehicles)

st.subheader("Profitto dell'operatore [€]")

profit_by_n_vehicles = sim_stats_df[[
    "n_vehicles_sim", "profit"
]]
altair_fig = alt.Chart(profit_by_n_vehicles).mark_bar(width=15).encode(
    x=alt.X('n_vehicles_sim', scale=alt.Scale(domain=[0, 1020])),
    y='profit',
    tooltip=["n_vehicles_sim", "profit"],
    color=alt.condition(
        alt.datum.profit > 0,
        alt.value("blue"),  # The positive color
        alt.value("red")  # The negative color
    )
).interactive()
st.altair_chart(altair_fig, use_container_width=True)

st.subheader("Composizione dei costi [€]")

with st.expander("Clicca per vedere la tabella dei costi completi"):
    st.dataframe(sim_stats_df[[col for col in sim_stats_df if "cost" in col]])

costs_by_n_vehicles = sim_stats_df[
    ["cars_cost", "charging_infrastructure_cost", "n_vehicles_sim"]
]

st.markdown("#### Investimenti iniziali [€]")

costs_by_n_vehicles = pd.melt(
    costs_by_n_vehicles,
    id_vars="n_vehicles_sim",
    value_vars=["cars_cost", "charging_infrastructure_cost", "n_vehicles_sim"]
).rename(columns={"value": "cost", "variable": "cost_type"})

altair_fig = alt.Chart(costs_by_n_vehicles).mark_bar(
    width=12, opacity=0.9
).encode(
    x=alt.X('n_vehicles_sim', scale=alt.Scale(domain=[0, 1020])),
    y=alt.Y('cost:Q', stack=True),
    color=alt.Color(field='cost_type'),
    tooltip=["n_vehicles_sim", "cost", "cost_type"]
).interactive()

st.altair_chart(altair_fig, use_container_width=True)

st.markdown("#### Costi operativi [€]")

costs_by_n_vehicles = sim_stats_df[
    ["relocation_cost", "energy_cost", "washing_cost", "n_vehicles_sim"]
]

costs_by_n_vehicles = pd.melt(
    costs_by_n_vehicles,
    id_vars="n_vehicles_sim",
    value_vars=["relocation_cost", "energy_cost", "washing_cost", "n_vehicles_sim"]
).rename(columns={"value": "cost", "variable": "cost_type"})

altair_fig = alt.Chart(costs_by_n_vehicles).mark_bar(
    width=12, opacity=0.9
).encode(
    x=alt.X('n_vehicles_sim', scale=alt.Scale(domain=[0, 1020])),
    y=alt.Y('cost:Q', stack=True),
    color=alt.Color(field='cost_type'),
    tooltip=["n_vehicles_sim", "cost", "cost_type"]
).interactive()
st.altair_chart(altair_fig, use_container_width=True)
