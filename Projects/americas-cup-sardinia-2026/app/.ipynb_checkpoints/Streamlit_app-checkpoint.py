import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="America's Cup Analytics",
    page_icon="🌊",
    layout="wide"
)

# ----------------------------
# TITLE
# ----------------------------
st.title("🌊 America’s Cup Cagliari 2026 Analytics")
st.markdown(
    """
Simulated sailing telemetry dashboard inspired by America’s Cup racing.
"""
)

# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/boat_track.csv")

df = load_data()

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.header("Dashboard Controls")

speed_filter = st.sidebar.slider(
    "Minimum Speed",
    float(df["speed_knots"].min()),
    float(df["speed_knots"].max()),
    float(df["speed_knots"].min())
)

filtered_df = df[df["speed_knots"] >= speed_filter]

# ----------------------------
# METRICS
# ----------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Speed",
    f"{filtered_df['speed_knots'].mean():.2f} knots"
)

col2.metric(
    "Maximum Speed",
    f"{filtered_df['speed_knots'].max():.2f} knots"
)

col3.metric(
    "Average Wind",
    f"{filtered_df['wind_speed'].mean():.2f} knots"
)

# ----------------------------
# SPEED CHART
# ----------------------------
st.subheader("⚡ Boat Speed Over Time")

fig_speed = px.line(
    filtered_df,
    x="time",
    y="speed_knots",
    title="Speed Timeline"
)

st.plotly_chart(fig_speed, use_container_width=True)

# ----------------------------
# GPS TRACK
# ----------------------------
st.subheader("🗺️ GPS Boat Track")

map_df = filtered_df.rename(
    columns={
        "lat": "latitude",
        "lon": "longitude"
    }
)

st.map(map_df)

# ----------------------------
# WIND VS SPEED
# ----------------------------
st.subheader("🌬️ Wind vs Boat Speed")

fig_scatter = px.scatter(
    filtered_df,
    x="wind_speed",
    y="speed_knots",
    color="speed_knots",
    hover_data=["heading"],
    title="Wind Impact on Boat Speed"
)

st.plotly_chart(fig_scatter, use_container_width=True)

# ----------------------------
# RAW DATA
# ----------------------------
st.subheader("📊 Raw Telemetry Data")

st.dataframe(filtered_df)

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.caption(
    "Educational project using simulated telemetry data."
)