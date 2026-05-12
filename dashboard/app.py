import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

con = duckdb.connect("../nexus_mods.duckdb")

st.set_page_config(page_title="Junimo Metrics", layout="wide")

st.title("Junimo Metrics Dashboard for Mods Analytics")
st.caption("Synthetic modding analytics platform with dbt models, tested marts, and lifecycle audiences.")

game_growth = con.execute("""
    select * from mart_game_growth
    order by download_starts desc
""").df()

audiences = con.execute("""
    select lifecycle_audience, count(*) as users
    from mart_lifecycle_audiences
    group by 1
    order by users desc
""").df()

col1, col2, col3 = st.columns(3)

col1.metric("Games", game_growth["game_id"].nunique())
col2.metric("Download Starts", int(game_growth["download_starts"].sum()))
col3.metric("Completion Rate", f"{game_growth['completed_downloads'].sum() / game_growth['download_starts'].sum():.1%}")

st.subheader("Game Growth")
st.dataframe(game_growth)

fig = px.bar(
    game_growth,
    x="game_name",
    y="download_starts",
    color="completion_rate",
    title="Download Starts by Game"
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Lifecycle Audiences")
st.dataframe(audiences)

fig2 = px.bar(
    audiences,
    x="lifecycle_audience",
    y="users",
    title="Lifecycle Audience Sizes"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Metric Catalogue")
metrics = con.execute("select * from metric_catalogue").df()
st.dataframe(metrics)