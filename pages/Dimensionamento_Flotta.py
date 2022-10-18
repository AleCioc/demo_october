import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Dimensionamento flotta")

chosen_simulation_readable = st.selectbox("Seleziona scenario:", options=[
    "Dimensionamento con veicoli a benzina", "Dimensionamento con veicoli elettrici"
])

chosen_simulation = "UNSPECIFIED"

if chosen_simulation_readable == "Dimensionamento con veicoli a benzina":
    chosen_simulation = "fleet_dim_fuel"
elif chosen_simulation_readable == "Dimensionamento con veicoli elettrici":
    chosen_simulation = "fleet_dim_ev"

sim_stats_df = pd.read_csv(
    "results/Roma/multiple_runs/{}/sim_stats.csv".format(chosen_simulation),
    index_col=0
).rename(columns={"washing_cost": "vehicle_maintainance_cost"})
sim_stats_df["avg_vehicle_utilisation"] = sim_stats_df.tot_mobility_duration / sim_stats_df.n_vehicles_sim / (15*24*60*60)

st.header("Risultati generali delle simulazioni")

st.subheader("Risultati completi")

with st.expander("Clicca per vedere la tabella dei risultati completi"):
    st.dataframe(sim_stats_df)


best_config_stats = sim_stats_df.loc[sim_stats_df.profit.idxmax()]
original_fleet_stats = sim_stats_df.loc[sim_stats_df.n_vehicles_sim == 600]

st.subheader("Risultati miglior scenario")

st.markdown(
    """
    
La migliore configurazione trovata è composta da {} veicoli, mentre la flotta originale ha 600 veicoli.

    """.format(best_config_stats.n_vehicles_sim)
)

from configs.vehicle_conf import vehicle_conf
from configs.cost_config import *

with st.expander("Clicca per vedere i dettagli della miglior configurazione"):
    st.dataframe(pd.DataFrame(best_config_stats).T)

with st.expander("Clicca per vedere la configurazione del singolo veicolo"):
    st_cols = st.columns((1, 1))
    if chosen_simulation == "fleet_dim_fuel":
        st_cols[0].write(vehicle_conf["gasoline"])
        st_cols[1].write(vehicle_cost["gasoline"]["Seat Leon 1.5 TSI 2020"])

with st.expander("Clicca per vedere la configurazione degli altri costi"):
    st_cols = st.columns((1, 1))
    if chosen_simulation == "fleet_dim_fuel":
        st_cols[0].write(fuel_costs["gasoline"])
        st_cols[1].write(administrative_cost_conf)

# if chosen_simulation == "fleet_dim_fuel":
#     with st.expander("Clicca per vedere la configurazione veicoli"):
#         st.write(vehicle_conf["gasoline"])


#with st.expander("Clicca per vedere i KPI più importanti"):

st_cols = st.columns((1, 1, 1))
st_cols[0].metric(
    "Aumento utilizzo veicoli",
    "+ {:.2f} %".format((
        ((best_config_stats.avg_vehicle_utilisation) \
         - (original_fleet_stats.avg_vehicle_utilisation)) \
        / (original_fleet_stats.avg_vehicle_utilisation)
    ).values[0] * 100), help="Frazione del tempo totale in cui un veicolo è utilizzato dagli utenti"
)

st_cols[1].metric(
    "Aumento domanda soddisfatta per veicolo",
    "+ {:.2f} %".format((
        (best_config_stats.percentage_satisfied / best_config_stats.n_vehicles_sim)\
        - (original_fleet_stats.percentage_satisfied / 600)
    ).values[0] * 100), help="Domanda degli utenti che un singolo veicolo riesce a soddisfare"
)
if original_fleet_stats.profit.values[0] < 0:
    profit_sign = -1
else:
    profit_sign = 1

st_cols[2].metric(
    "Aumento profitto",
    "+ {:.2f} %".format((
        ((best_config_stats.profit) \
         - (original_fleet_stats.profit)) \
        / (original_fleet_stats.profit * profit_sign)
    ).values[0] * 100),
    help="Profitto operativo mensile"
)
st_cols = st.columns((1, 1, 1))
st_cols[0].metric(
    "Riduzione CO2 emessa",
    "- {:.2f} %".format((
            (original_fleet_stats.tot_co2_emissions_kg - best_config_stats.tot_co2_emissions_kg)\
            / original_fleet_stats.tot_co2_emissions_kg
    ).values[0] * 100),
    help="Emissioni di CO2eq [kg] calcolate con la metodologia Well-to-Wheel"
)

st_cols[1].metric(
    "Riduzione costi veicoli",
    "- {:.2f} %".format((
            (original_fleet_stats.cars_cost + original_fleet_stats.vehicle_maintainance_cost\
             - best_config_stats.cars_cost - best_config_stats.vehicle_maintainance_cost)\
            / (original_fleet_stats.cars_cost + original_fleet_stats.vehicle_maintainance_cost)
    ).values[0] * 100),
    help="Comprende rata mensile di leasing e costi di manutenzione calcolati sull'intera flotta"
)
st_cols[2].metric(
    "Riduzione veicoli in circolazione",
    "- {:.2f} %".format(((600 - best_config_stats.n_vehicles_sim) / 600) * 100),
    help="Puoi ottenere un servizio efficiente con meno veicoli!"
)

sim_stats_df.n_vehicles_sim = sim_stats_df.n_vehicles_sim.astype(float)

st.header("Guarda tutti i grafici")

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

st.subheader("Frazione di tempo in cui un veicolo è utilizzato dagli utenti [%]")

unsatisfied_by_n_vehicles = sim_stats_df[[
    "n_vehicles_sim", "avg_vehicle_utilisation"
]]
altair_fig = alt.Chart(unsatisfied_by_n_vehicles).mark_bar(width=15).encode(
    x=alt.X('n_vehicles_sim', scale=alt.Scale(domain=[0, 1020])),
    y='avg_vehicle_utilisation',
    tooltip=["n_vehicles_sim", "avg_vehicle_utilisation"]
).interactive()
st.altair_chart(altair_fig, use_container_width=True)

st.subheader("Profitto per veicolo [€]")

profit_by_n_vehicles = sim_stats_df[[
    "n_vehicles_sim", "avg_vehicle_utilisation", "profit"
]]
profit_by_n_vehicles.loc[:, "profit_per_vehicle"] = profit_by_n_vehicles.profit / profit_by_n_vehicles.n_vehicles_sim
altair_fig = alt.Chart(profit_by_n_vehicles).mark_bar(width=15).encode(
    x=alt.X('n_vehicles_sim', scale=alt.Scale(domain=[0, 1020])),
    y='profit_per_vehicle',
    tooltip=["n_vehicles_sim", "profit_per_vehicle"]
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

st.markdown("#### Costi infrastruttura [€]")

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
    ["relocation_cost", "energy_cost", "vehicle_maintainance_cost", "n_vehicles_sim"]
]

costs_by_n_vehicles = pd.melt(
    costs_by_n_vehicles,
    id_vars="n_vehicles_sim",
    value_vars=["relocation_cost", "energy_cost", "vehicle_maintainance_cost", "n_vehicles_sim"]
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
