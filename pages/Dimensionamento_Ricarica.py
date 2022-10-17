import streamlit as st
import pandas as pd
from utils import add_logo
import altair as alt

st.set_page_config(layout="wide")

add_logo()

st.header("Dimensionamento ricarica")

chosen_simulation = st.selectbox("Seleziona scenario:", options=[
    "charging_dim_ev"
])

sim_stats_df = pd.read_csv(
    "results/Roma/multiple_runs/{}/sim_stats.csv".format(chosen_simulation),
    index_col=0
).rename(columns={"washing_cost": "vehicle_maintainance_cost"})

st.subheader("Risultati completi")
with st.expander("Clicca per vedere i risultati completi"):
    st.dataframe(sim_stats_df)

sim_stats_df.tot_n_charging_poles = sim_stats_df.tot_n_charging_poles.astype(float)

selected_n_charging_zones = st.selectbox(
    "Seleziona numero di zone con stazioni di ricarica:", sorted(sim_stats_df.n_charging_zones.unique())
)

st.subheader("Domanda insoddisfatta [%]")

unsatisfied_by_n_poles = sim_stats_df.loc[
    sim_stats_df.n_charging_zones == selected_n_charging_zones, [
        "tot_n_charging_poles", "percentage_unsatisfied"
    ]
]
altair_fig = alt.Chart(unsatisfied_by_n_poles).mark_bar(width=15).encode(
    x=alt.X('tot_n_charging_poles', scale=alt.Scale(domain=[0, 50])),
    y='percentage_unsatisfied',
    tooltip=["tot_n_charging_poles", "percentage_unsatisfied"]
).interactive()
st.altair_chart(altair_fig, use_container_width=True)

st.subheader("Profitto dell'operatore [€]")

profit_by_charging_config = sim_stats_df.loc[
    sim_stats_df.n_charging_zones == selected_n_charging_zones, [
        "tot_n_charging_poles", "n_charging_zones", "profit"
    ]].copy()

profit_by_charging_config["profit_norm"] = profit_by_charging_config.profit / profit_by_charging_config.profit.max()
profit_by_charging_config["profit_abs"] = profit_by_charging_config.profit.abs()

altair_fig = alt.Chart(profit_by_charging_config).mark_bar(width=15).encode(
    x=alt.X('tot_n_charging_poles', scale=alt.Scale(domain=[0, 50])),
    y='profit',
    tooltip=["tot_n_charging_poles", "profit"],
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

costs_by_n_poles = sim_stats_df.loc[
    :, [
        "cars_cost", "charging_infrastructure_cost", "tot_n_charging_poles", "n_charging_zones"
    ]
]

st.markdown("#### Costi infrastruttura [€]")

costs_by_n_poles = pd.melt(
    costs_by_n_poles,
    id_vars=["n_charging_zones", "tot_n_charging_poles"],
    value_vars=["charging_infrastructure_cost", "tot_n_charging_poles", "n_charging_zones"]
).rename(columns={"value": "cost", "variable": "cost_type"})

altair_fig = alt.Chart(costs_by_n_poles).mark_bar(
    width=12, opacity=0.9
).encode(
    x=alt.X('tot_n_charging_poles', scale=alt.Scale(domain=[0, 50])),
    y=alt.Y('cost:Q', stack=True),
    color=alt.Color(field='cost_type'),
    tooltip=["tot_n_charging_poles", "cost", "cost_type"]
).interactive()

st.altair_chart(altair_fig, use_container_width=True)

st.markdown("#### Costi operativi [€]")

costs_by_n_poles = sim_stats_df.loc[
    sim_stats_df.n_charging_zones == selected_n_charging_zones, [
        "relocation_cost", "energy_cost", "vehicle_maintainance_cost", "tot_n_charging_poles"
    ]
]
costs_by_n_poles = pd.melt(
    costs_by_n_poles,
    id_vars="tot_n_charging_poles",
    value_vars=["relocation_cost", "energy_cost", "vehicle_maintainance_cost", "tot_n_charging_poles"]
).rename(columns={"value": "cost", "variable": "cost_type"})

altair_fig = alt.Chart(costs_by_n_poles).mark_bar(
    width=12, opacity=0.9
).encode(
    x=alt.X('tot_n_charging_poles', scale=alt.Scale(domain=[0, 50])),
    y=alt.Y('cost:Q', stack=True),
    color=alt.Color(field='cost_type'),
    tooltip=["tot_n_charging_poles", "cost", "cost_type"]
).interactive()
st.altair_chart(altair_fig, use_container_width=True)
