import os
import re
import json
import streamlit as st
import pandas as pd
import contextily as ctx
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.sidebar.image("SWITCH - Logo.png", use_column_width=True)

st.header("Stazioni di ricarica")


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

with open("results/Roma/single_run/enjoy_fleet_test/{}/n_charging_poles_by_zone.json".format(str(chosen_simulation)), "r") as f:
    n_charging_poles_by_zone = json.load(f)

grid = pd.read_pickle(
    "results/Roma/single_run/enjoy_fleet_test/{}/grid.pickle".format(
        str(chosen_simulation)
    )
)

#st.write(grid.columns)

charging_zones = [int(z) for z in n_charging_poles_by_zone.keys()]
charging_poles_by_zone = {int(z): n_charging_poles_by_zone[z] for z in n_charging_poles_by_zone.keys()}

grid.loc[charging_zones, "poles_count"] = charging_poles_by_zone

mean_lon = grid.centroid.geometry.apply(lambda p: p.x).mean()
mean_lat = grid.centroid.geometry.apply(lambda p: p.y).mean()

import plotly.express as px

#grid_json = grid[["geometry"]].to_json()
st.write(grid.crs)

st_cols = st.columns((1, 1))

fig = px.choropleth_mapbox(
    grid, geojson=grid.geometry, locations=grid.index, color="poles_count",
    mapbox_style="carto-positron", center={"lat": mean_lat, "lon": mean_lon},
    opacity=0.5
)
fig.update_layout(title_text='Number of charging poles by zone')
st_cols[0].plotly_chart(fig, use_container_width=True)

fig = px.choropleth_mapbox(
    grid, geojson=grid.geometry, locations=grid.index, color="unsatisfied_demand_origins",
    mapbox_style="carto-positron", center={"lat": mean_lat, "lon": mean_lon},
    opacity=0.5
)
fig.update_layout(title_text='Unsatisfied demand by zone')
st_cols[1].plotly_chart(fig, use_container_width=True)


# fig, ax = plt.subplots(figsize=(10, 10))
# plt.title("Number of charging poles by zone")
# grid.to_crs("epsg:3857").plot(ax=ax, column="poles_count", legend=True)
# ctx.add_basemap(ax)
# st_cols[0].pyplot(fig)
#
# fig, ax = plt.subplots(figsize=(10, 10))
# plt.title("Unsatisfied demand by zone")
# grid.to_crs("epsg:3857").plot(ax=ax, column="unsatisfied_demand_origins", legend=True)
# ctx.add_basemap(ax)
# st_cols[1].pyplot(fig)
#
