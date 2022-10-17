import os
import json
import pandas as pd
from utils import *


st.set_page_config(layout="wide")

add_logo()

st.header("Stazioni di ricarica")

chosen_sim_scenario = st.selectbox("Seleziona scenario:", ["charging_dim_ev"])

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

st.metric("Numero effettivo di zone con stazioni", len(charging_poles_by_zone.keys()))

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
