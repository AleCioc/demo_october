import os
import json
import pandas as pd
from utils import *


st.set_page_config(layout="wide")

st.title("Stazioni di ricarica")

st.header("Esplora le disposizioni trovate")

chosen_simulation_readable = st.selectbox("Seleziona scenario:", options=[
    "Dimensionamento ricarica per veicoli elettrici"
])

chosen_sim_scenario = "UNSPECIFIED"

if chosen_simulation_readable == "Dimensionamento ricarica per veicoli elettrici":
    chosen_sim_scenario = "charging_dim_ev"

sim_ids = [f for f in os.listdir("results/Roma/single_run/{}".format(chosen_sim_scenario)) if f != ".DS_Store"]
sim_ids.sort(key=natural_keys)

sim_stats_df = pd.DataFrame()
for sim_id in sim_ids:
    sim_stats = pd.read_csv(
        "results/Roma/single_run/{}/{}/sim_stats.csv".format(chosen_sim_scenario, sim_id), index_col=0
    )
    sim_stats.loc["sim_id"] = sim_id
    sim_stats_df = pd.concat([sim_stats_df, sim_stats.T], ignore_index=True)

selected_n_charging_zones = st.selectbox(
    "Seleziona numero massimo di zone con stazioni di ricarica:", sim_stats_df.n_charging_zones.unique()
)

available_n_charging_poles = list(sim_stats_df.tot_n_charging_poles.unique())
available_n_charging_poles.sort(key=natural_keys)

selected_tot_n_charging_poles = st.selectbox(
    "Seleziona numero di colonnine:", available_n_charging_poles
)


chosen_sim_id = sim_stats_df.loc[
    (sim_stats_df.n_charging_zones == selected_n_charging_zones) & (
            sim_stats_df.tot_n_charging_poles == selected_tot_n_charging_poles
    ), "sim_id"
].values[0]

with open("results/Roma/single_run/{}/{}/n_charging_poles_by_zone.json".format(
        str(chosen_sim_scenario), str(chosen_sim_id)
), "r") as f:
    n_charging_poles_by_zone = json.load(f)

grid = pd.read_pickle(
    "results/Roma/single_run/{}/{}/grid.pickle".format(
        str(chosen_sim_scenario), str(chosen_sim_id)
    )
)

charging_zones = [int(z) for z in n_charging_poles_by_zone.keys()]
charging_poles_by_zone = {int(z): n_charging_poles_by_zone[z] for z in n_charging_poles_by_zone.keys()}

sim_stats = sim_stats_df[sim_stats_df.sim_id == chosen_sim_id]

st_cols = st.columns((1, 1, 1))
st_cols[0].metric(
    "Numero effettivo di zone", len(charging_poles_by_zone.keys()),
    help="L'algoritmo di assegnazione zone può decidere di usarne meno del numero fornito"
)
st_cols[1].metric(
    "Domanda insoddisfatta", sim_stats.percentage_unsatisfied.values[0][:5] + " %",
    help="Percentuale di domanda insoddisfatta complessiva"
)
st_cols[2].metric(
    "Rate medio domanda insoddisfatta per zona", str((grid.unsatisfied_demand_origins / grid.origin_count).mean())[:5],
    help="Percentuale di domanda insoddisfatta media per zona"
)
st_cols = st.columns((1, 1, 1))

st_cols[0].metric(
    "Tempo di gestione", str(sim_stats.cum_relo_ret_t.astype(float).values[0] / 3600)[:-11] + " ore",
    help="Tempo necessario agli spostamenti legati alle ricariche"
)

st_cols[1].metric(
    "Costi di rilocazione", str(sim_stats.relocation_cost.astype(float).values[0])[:-11] + " €",
    help="Costi per sostenere gli spostamenti legati alle ricariche"
)

st_cols[2].metric(
    "Costi infrastruttura", str(sim_stats.charging_infrastructure_cost.astype(float).values[0])[:-11] + " €",
    help="Costi mensili per sostenere l'infrastruttura con ammortamento pari a 10 anni"
)

grid.loc[charging_zones, "poles_count"] = charging_poles_by_zone

mean_lon = grid.centroid.geometry.apply(lambda p: p.x).mean()
mean_lat = grid.centroid.geometry.apply(lambda p: p.y).mean()

import plotly.express as px

st_cols = st.columns((1, 1))

fig = px.choropleth_mapbox(
    grid, geojson=grid.geometry, locations=grid.index, color="poles_count", range_color=(0, 100),
    mapbox_style="carto-positron", center={"lat": mean_lat, "lon": mean_lon},
    opacity=0.5
)
fig.update_layout(title_text='Number of charging poles by zone')
st_cols[0].plotly_chart(fig, use_container_width=True)

fig = px.choropleth_mapbox(
    grid, geojson=grid.geometry, locations=grid.index, color="unsatisfied_demand_origins",
    range_color=(0, 120),
    mapbox_style="carto-positron", center={"lat": mean_lat, "lon": mean_lon},
    opacity=0.5
)
fig.update_layout(title_text='Unsatisfied demand by zone')
st_cols[1].plotly_chart(fig, use_container_width=True)
