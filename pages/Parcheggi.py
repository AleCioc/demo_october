from matplotlib.backends.backend_agg import RendererAgg
_lock = RendererAgg.lock

import os
import re
import streamlit as st
import pandas as pd
import contextily as ctx
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.sidebar.image("SWITCH - Logo.png", use_column_width=True)

st.header("Analisi parcheggi")


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]


sim_ids = os.listdir("results/Roma/single_run/enjoy_fleet_test")
sim_ids.sort(key=natural_keys)

chosen_simulation = st.selectbox("Seleziona scenario:", sim_ids)

grid = pd.read_pickle(
    "results/Roma/single_run/enjoy_fleet_test/{}/grid.pickle".format(
        str(chosen_simulation)
    )
)

# st.write(grid)

zones_history = pd.read_csv(
    "results/Roma/single_run/enjoy_fleet_test/{}/zones_history.csv".format(str(chosen_simulation)),
    index_col=0
)

n_vehicles_parked_by_zone = zones_history.groupby("zone_id").vehicles_parked.mean()
grid["n_vehicles_parked_by_zone"] = n_vehicles_parked_by_zone
n_vehicles_parked_by_zone = zones_history.groupby("zone_id").vehicles_parked.max()
grid["n_vehicles_parked_by_zone_max"] = n_vehicles_parked_by_zone

mean_lon = grid.centroid.geometry.apply(lambda p: p.x).mean()
mean_lat = grid.centroid.geometry.apply(lambda p: p.y).mean()

import plotly.express as px

#grid_json = grid[["geometry"]].to_json()
st.write(grid.crs)

st_cols = st.columns((1, 1))

fig = px.choropleth_mapbox(
    grid, geojson=grid.geometry, locations=grid.index, color="n_vehicles_parked_by_zone",
    mapbox_style="carto-positron", center={"lat": mean_lat, "lon": mean_lon},
    opacity=0.5
)
fig.update_layout(title_text='Mean parking index')
st_cols[0].plotly_chart(fig, use_container_width=True)

fig = px.choropleth_mapbox(
    grid, geojson=grid.geometry, locations=grid.index, color="n_vehicles_parked_by_zone_max",
    mapbox_style="carto-positron", center={"lat": mean_lat, "lon": mean_lon},
    opacity=0.5
)
fig.update_layout(title_text='Max parking index')
st_cols[1].plotly_chart(fig, use_container_width=True)

