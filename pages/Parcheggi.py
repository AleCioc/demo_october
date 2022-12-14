import os
import pandas as pd
import plotly.express as px
from utils import *

import warnings
warnings.simplefilter("ignore")

st.set_page_config(layout="wide")

st.title("Analisi parcheggi")

st.header("Calcolo degli indici")

chosen_simulation_readable = st.selectbox("Seleziona scenario:", options=[
    "Dimensionamento con veicoli a benzina", "Dimensionamento con veicoli elettrici"
])

chosen_sim_scenario = "UNSPECIFIED"

if chosen_simulation_readable == "Dimensionamento con veicoli a benzina":
    chosen_sim_scenario = "fleet_dim_fuel"
elif chosen_simulation_readable == "Dimensionamento con veicoli elettrici":
    chosen_sim_scenario = "fleet_dim_ev"

sim_ids = [f for f in os.listdir("results/Roma/single_run/{}".format(chosen_sim_scenario)) if f != ".DS_Store"]
sim_ids.sort(key=natural_keys)

sim_stats_df = pd.DataFrame()
for sim_id in sim_ids:
    sim_stats = pd.read_csv("results/Roma/single_run/{}/{}/sim_stats.csv".format(chosen_sim_scenario, sim_id), index_col=0)
    sim_stats.loc["sim_id"] = sim_id
    sim_stats_df = pd.concat([sim_stats_df, sim_stats.T], ignore_index=True)

chosen_n_vehicles = st.selectbox("Seleziona numero di veicoli:", sim_stats_df.n_vehicles_sim.unique())
chosen_sim_id = sim_stats_df.loc[sim_stats_df.n_vehicles_sim == chosen_n_vehicles, "sim_id"].values[0]

#chosen_sim_id = st.selectbox("Seleziona simulation_id:", sim_ids)

grid = pd.read_pickle(
    "results/Roma/single_run/{}/{}/grid.pickle".format(
        str(chosen_sim_scenario), str(chosen_sim_id)
    )
)

# st.write(grid)

zones_history = pd.read_csv(
    "results/Roma/single_run/{}/{}/zones_history.csv".format(
        str(chosen_sim_scenario), str(chosen_sim_id)
    ),
    index_col=0
)

n_vehicles_parked_by_zone = zones_history[zones_history.vehicles_parked > 0].groupby("zone_id").vehicles_parked.median()
n_vehicles_parked_by_zone = n_vehicles_parked_by_zone[n_vehicles_parked_by_zone > n_vehicles_parked_by_zone.median()]
grid["parking_index_1"] = n_vehicles_parked_by_zone

n_vehicles_parked_by_zone_max = zones_history.groupby("zone_id").vehicles_parked.max()
n_vehicles_parked_by_zone_max = n_vehicles_parked_by_zone_max[
    n_vehicles_parked_by_zone_max > n_vehicles_parked_by_zone_max.median()
]
n_vehicles_parked_by_zone_max = n_vehicles_parked_by_zone_max[
    n_vehicles_parked_by_zone_max > 10
]
grid["parking_index_2"] = n_vehicles_parked_by_zone_max

n_vehicles_parked_by_zone.name = "parking_index_1"
n_vehicles_parked_by_zone_max.name = "parking_index_2"

parking_indices_df = pd.concat([
    n_vehicles_parked_by_zone,
    n_vehicles_parked_by_zone_max
], axis=1)

mean_lon = grid.centroid.geometry.apply(lambda p: p.x).median()
mean_lat = grid.centroid.geometry.apply(lambda p: p.y).median()

critical_zones = grid.loc[
    (grid.parking_index_1 > 0) & (grid.parking_index_2 > 0)
].sort_values("parking_index_1", ascending=False).zone_id.values

st_cols = st.columns((1, 1))


@st.experimental_memo
def plotly_chart_1():
    fig = px.choropleth_mapbox(
        grid, geojson=grid.geometry, locations=grid.index, color="parking_index_1",
        mapbox_style="carto-positron", center={"lat": mean_lat, "lon": mean_lon},
        opacity=0.5, color_continuous_scale="jet"
    )
    fig.update_layout(title_text='Parking index 1')
    return fig


@st.experimental_memo
def plotly_chart_2():
    fig = px.choropleth_mapbox(
        grid, geojson=grid.geometry, locations=grid.index, color="parking_index_2",
        mapbox_style="carto-positron", center={"lat": mean_lat, "lon": mean_lon},
        opacity=0.5, color_continuous_scale="jet"
    )
    fig.update_layout(title_text='Parking index 2')
    return fig


st_cols[0].plotly_chart(plotly_chart_1(), use_container_width=True)
st_cols[1].plotly_chart(plotly_chart_2(), use_container_width=True)

st.header("Identificazione zone critiche")

if len(critical_zones):

    st.warning("Attenzione! Sono state individuate le seguenti zone critiche:")
    st.warning(" - ".join(list([str(int(z)) for z in critical_zones])))

    st.subheader("Analisi zone critiche")

    with st.expander("Clicca per vedere gli indici di parcheggio delle zone critiche"):
        st.dataframe(parking_indices_df.loc[critical_zones])

    st_cols = st.columns((1, 3))

    selected_zone = st_cols[0].selectbox(
        "Seleziona la zona per vedere la storia dei parcheggi:", critical_zones
    )

    zone_df = zones_history[zones_history.zone_id == selected_zone]
    zone_df.t = pd.to_datetime(zone_df.t)

    import altair as alt

    fig = alt.Chart(zone_df).properties(height=400).mark_line(point=True, interpolate='step-after').encode(
        x='t',
        y=alt.Y('vehicles_parked', scale=alt.Scale(domain=[0, zones_history.vehicles_parked.max()])),
        tooltip=["t", "vehicles_parked"]
    ).interactive()
    st_cols[1].altair_chart(fig, use_container_width=True)

    grid_xy = pd.DataFrame(index=grid.index)
    grid_xy["zone_id"] = grid.zone_id
    grid_xy["x"] = grid.centroid.geometry.apply(lambda p: p.x)
    grid_xy["y"] = grid.centroid.geometry.apply(lambda p: p.y)

    data = pd.merge(zones_history, grid_xy, on='zone_id')
    data = data[data.zone_id.isin(critical_zones)]


    # -> The chart below is very cool but heavy
    # -> Check Altair limitations for complex charts

    @st.experimental_memo
    def create_altair_chart():

        selector = alt.selection_single(empty='all', fields=['zone_id'])

        base = alt.Chart(data).add_selection(selector)

        points = base.mark_point(filled=True, size=200).encode(
            x=alt.X('x', scale=alt.Scale(domain=[grid_xy.x.min(), grid_xy.x.max()])),
            y=alt.Y('y', scale=alt.Scale(domain=[grid_xy.y.min(), grid_xy.y.max()])),
            color=alt.condition(selector, 'zone_id', alt.value('lightgray'), legend=None),
        )

        timeseries = base.mark_line().properties(width=500).encode(
            x=alt.Y('t:T'),
            y=alt.Y('vehicles_parked', scale=alt.Scale(domain=(0, 30))),
            color=alt.Color('zone_id', legend=None)
        ).transform_filter(
            selector
        ).interactive()

        alt_fig = points | timeseries

        return alt_fig


    #alt_fig = create_altair_chart()
    #st.altair_chart(alt_fig, use_container_width=True)

else:

    st.success("Congratulazioni! Nessuna zona critica di parcheggio trovata!")
