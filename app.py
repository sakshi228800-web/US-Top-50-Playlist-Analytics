
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="US Top 50 Playlist Analytics",
    page_icon="🎵",
    layout="wide"
)

st.title("United States Top 50 Playlist Analytics")

st.markdown(
    "Explore song popularity, chart rankings, "
    "artist dominance and playlist trends."
)

# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

DATASET_PATH = (
    Path(__file__).parent / "Atlantic_United_States(1).csv"
)

if not DATASET_PATH.exists():
    st.error("Dataset not found.")

    st.write("Expected dataset location:")
    st.code(str(DATASET_PATH))

    st.info(
        "Make sure Atlantic_United_States(1).csv "
        "is uploaded to the same GitHub folder as app.py."
    )

    st.stop()

try:
    df = pd.read_csv(DATASET_PATH)
    st.success("Playlist dataset loaded successfully!")

except Exception as e:
    st.error(f"Unable to load dataset: {e}")
    st.stop()

# --------------------------------------------------
# VALIDATE DATASET COLUMNS
# --------------------------------------------------

required_columns = [
    "date",
    "position",
    "song",
    "artist",
    "popularity",
    "duration_ms",
    "album_type",
    "is_explicit"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    st.error(f"Missing dataset columns: {missing}")
    st.stop()

# --------------------------------------------------
# DATA PREPARATION
# --------------------------------------------------

df["date"] = pd.to_datetime(
    df["date"],
    dayfirst=True,
    errors="coerce"
)

df["position"] = pd.to_numeric(
    df["position"],
    errors="coerce"
)

df["popularity"] = pd.to_numeric(
    df["popularity"],
    errors="coerce"
)

df["duration_ms"] = pd.to_numeric(
    df["duration_ms"],
    errors="coerce"
)

df["duration_min"] = df["duration_ms"] / 60000

df = df.dropna(
    subset=[
        "date",
        "position",
        "song",
        "artist",
        "popularity"
    ]
)

if df.empty:
    st.error("The dataset contains no valid records.")
    st.stop()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

artists = sorted(
    df["artist"].dropna().unique()
)

selected_artists = st.sidebar.multiselect(
    "Select Artists",
    artists,
    default=artists
)

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    (df["artist"].isin(selected_artists)) &
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
]

if filtered.empty:
    st.warning("No records match your selected filters.")
    st.stop()

# --------------------------------------------------
# KEY PERFORMANCE INDICATORS
# --------------------------------------------------

st.subheader("Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Playlist Records",
    f"{len(filtered):,}"
)

c2.metric(
    "Unique Songs",
    filtered["song"].nunique()
)

c3.metric(
    "Unique Artists",
    filtered["artist"].nunique()
)

c4.metric(
    "Average Popularity",
    round(filtered["popularity"].mean(), 2)
)

c5, c6, c7 = st.columns(3)

c5.metric(
    "Average Chart Rank",
    round(filtered["position"].mean(), 2)
)

c6.metric(
    "Best Chart Position",
    int(filtered["position"].min())
)

c7.metric(
    "Average Song Duration",
    round(filtered["duration_min"].mean(), 2)
)

# --------------------------------------------------
# 1. PLAYLIST POPULARITY TREND
# --------------------------------------------------

st.subheader("1. Playlist Popularity Trend")

trend = (
    filtered.groupby("date")["popularity"]
    .mean()
    .reset_index()
)

fig = px.line(
    trend,
    x="date",
    y="popularity",
    title="Average Popularity Over Time"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# 2. TOP 10 SONGS
# --------------------------------------------------

st.subheader("2. Top 10 Songs")

top_songs = (
    filtered.groupby("song")
    .agg(
        chart_entries=("position", "count"),
        average_popularity=("popularity", "mean")
    )
    .sort_values(
        "chart_entries",
        ascending=False
    )
    .head(10)
    .reset_index()
)

fig = px.bar(
    top_songs,
    x="chart_entries",
    y="song",
    orientation="h",
    title="Top Songs by Chart Entries"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.dataframe(
    top_songs,
    use_container_width=True
)

# --------------------------------------------------
# 3. ARTIST DOMINANCE
# --------------------------------------------------

st.subheader("3. Artist Dominance")

artist_data = (
    filtered.groupby("artist")
    .agg(
        chart_entries=("song", "count"),
        unique_songs=("song", "nunique"),
        average_popularity=("popularity", "mean")
    )
    .sort_values(
        "chart_entries",
        ascending=False
    )
    .head(10)
    .reset_index()
)

fig = px.bar(
    artist_data,
    x="artist",
    y="chart_entries",
    title="Top 10 Artists by Chart Entries"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.dataframe(
    artist_data,
    use_container_width=True
)

# --------------------------------------------------
# 4. POPULARITY VS CHART RANKING
# --------------------------------------------------

st.subheader("4. Popularity vs Playlist Ranking")

fig = px.scatter(
    filtered,
    x="popularity",
    y="position",
    color="album_type",
    hover_data=["song", "artist"],
    title="Popularity vs Chart Position"
)

fig.update_yaxes(
    autorange="reversed"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# 5. EXPLICIT CONTENT ANALYSIS
# --------------------------------------------------

st.subheader("5. Explicit Content Analysis")

explicit_data = (
    filtered.groupby("is_explicit")["popularity"]
    .mean()
    .reset_index()
)

fig = px.bar(
    explicit_data,
    x="is_explicit",
    y="popularity",
    title="Average Popularity by Explicit Content"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# 6. ALBUM TYPE ANALYSIS
# --------------------------------------------------

st.subheader("6. Album Type Analysis")

album_data = (
    filtered.groupby("album_type")["popularity"]
    .mean()
    .reset_index()
)

fig = px.bar(
    album_data,
    x="album_type",
    y="popularity",
    title="Average Popularity by Album Type"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# 7. DOWNLOAD FILTERED DATASET
# --------------------------------------------------

st.subheader("7. Download Filtered Dataset")

csv = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Analysis Data",
    data=csv,
    file_name="US_Top_50_Analysis.csv",
    mime="text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "United States Top 50 Playlist Performance and "
    "Song Popularity Trend Analysis | Python & Streamlit"
)
```
