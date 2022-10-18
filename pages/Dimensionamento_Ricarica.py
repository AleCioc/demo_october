import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")

st.title("Dimensionamento ricarica")

chosen_simulation_readable = st.selectbox("Seleziona scenario:", options=[
    "Dimensionamento ricarica per veicoli elettrici"
])

chosen_simulation = "UNSPECIFIED"

if chosen_simulation_readable == "Dimensionamento ricarica per veicoli elettrici":
    chosen_simulation = "charging_dim_ev"

sim_stats_df = pd.read_csv(
    "results/Roma/multiple_runs/{}/sim_stats.csv".format(chosen_simulation),
    index_col=0
).rename(columns={"washing_cost": "vehicle_maintainance_cost"})

st.header("Risultati generali delle simulazioni")

st.subheader("Risultati completi")

with st.expander("Clicca per vedere i risultati completi"):
    st.dataframe(sim_stats_df)

best_config_stats_profit = sim_stats_df.loc[sim_stats_df.profit.idxmax()]
best_config_stats_unsatisfied = sim_stats_df.loc[sim_stats_df.percentage_unsatisfied.idxmin()]
best_config_stats_relot = sim_stats_df[sim_stats_df.percentage_satisfied > 70]
best_config_stats_relot = best_config_stats_relot.loc[best_config_stats_relot.cum_relo_t.idxmin()]

original_fleet_stats = sim_stats_df.loc[sim_stats_df.n_vehicles_sim == 600]

st.subheader("Risultati miglior scenario")

st.markdown(
    """

La migliore configurazione in base al profitto è composta da {} zone (max) con stazioni di ricarica e {} colonnine totali.

    """.format(
        best_config_stats_profit.n_charging_zones,
        best_config_stats_profit.tot_n_charging_poles
    )
)

st.markdown(
    """

La migliore configurazione in base alla domanda soddisfatta è composta da {} zone (max) con stazioni di ricarica e {} colonnine totali.

    """.format(
        best_config_stats_unsatisfied.n_charging_zones,
        best_config_stats_unsatisfied.tot_n_charging_poles
    )
)

# st.markdown(
#     """
#
# La migliore configurazione in base al tempo di gestione e con domanda soddisfatta > 70%
#  è composta da {} zone (max) con stazioni di ricarica e {} colonnine totali.
#
#     """.format(
#         best_config_stats_relot.n_charging_zones,
#         best_config_stats_relot.tot_n_charging_poles
#     )
# )

# st_cols = st.columns((1, 1, 1))
# st_cols[0].metric(
#     "Aumento utilizzo veicoli",
#     "+ {:.2f} %".format((
#             ((best_config_stats.avg_vehicle_utilisation) \
#              - (original_fleet_stats.avg_vehicle_utilisation)) \
#             / (original_fleet_stats.avg_vehicle_utilisation)
#     ).values[0] * 100)
# )
# st_cols[1].metric(
#     "Aumento domanda soddisfatta per veicolo",
#     "+ {:.2f} %".format((
#             (best_config_stats.percentage_satisfied / best_config_stats.n_vehicles_sim) \
#             - (original_fleet_stats.percentage_satisfied / 600)
#     ).values[0] * 100)
# )
# if original_fleet_stats.profit.values[0] < 0:
#     profit_sign = -1
# else:
#     profit_sign = 1
#
# st_cols[2].metric(
#     "Aumento profitto",
#     "+ {:.2f} %".format((
#             ((best_config_stats.profit) \
#              - (original_fleet_stats.profit)) \
#             / (original_fleet_stats.profit * profit_sign)
#     ).values[0] * 100)
# )
# st_cols = st.columns((1, 1, 1))
# st_cols[0].metric(
#     "Riduzione CO2 emessa",
#     "- {:.2f} %".format((
#             (original_fleet_stats.tot_co2_emissions_kg - best_config_stats.tot_co2_emissions_kg) \
#             / original_fleet_stats.tot_co2_emissions_kg
#     ).values[0] * 100)
# )
#
# st_cols[1].metric(
#     "Riduzione costi veicoli",
#     "- {:.2f} %".format((
#             (original_fleet_stats.cars_cost + original_fleet_stats.vehicle_maintainance_cost \
#              - best_config_stats.cars_cost - best_config_stats.vehicle_maintainance_cost) \
#             / (original_fleet_stats.cars_cost + original_fleet_stats.vehicle_maintainance_cost)
#     ).values[0] * 100)
# )
# st_cols[2].metric(
#     "Riduzione veicoli in circolazione",
#     "- {:.2f} %".format(((600 - best_config_stats.n_vehicles_sim) / 600) * 100)
# )

st.header("Guarda tutti i grafici")

sim_stats_df.n_vehicles_sim = sim_stats_df.n_vehicles_sim.astype(float)

sim_stats_df.tot_n_charging_poles = sim_stats_df.tot_n_charging_poles.astype(float)

selected_n_charging_zones = st.selectbox(
    "Seleziona numero massimo di zone con stazioni di ricarica:", sorted(sim_stats_df.n_charging_zones.unique())
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
