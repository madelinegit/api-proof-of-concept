import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Tahoe Properties Map", layout="wide")
st.title("Tahoe Properties Map (Geocoded Only)")

# ---- Load data (NO upload) ----
DATA_FILE = "properties_geocoded.csv"

try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    st.error(f"Couldn't find {DATA_FILE} in this folder. Make sure it's next to map_app.py.")
    st.stop()

# ---- Normalize column names just in case ----
df.columns = df.columns.str.strip()

# Required columns
required = ["Latitude", "Longitude"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}. Your CSV must include Latitude and Longitude.")
    st.stop()

# Optional columns for nicer tooltips/table
name_col = "Property Name" if "Property Name" in df.columns else None
addr_col = "Unit Address" if "Unit Address" in df.columns else None

# Keep only rows with valid coordinates
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df_ok = df.dropna(subset=["Latitude", "Longitude"]).copy()

st.caption(f"Loaded {len(df)} rows • Showing {len(df_ok)} geocoded properties")

# ---- Filters ----
left, right = st.columns([2, 1])

with left:
    q = st.text_input("Search (property name or address)", "")
with right:
    show_table = st.checkbox("Show table", value=True)

if q.strip():
    ql = q.strip().lower()
    cols_to_search = []
    if name_col: cols_to_search.append(name_col)
    if addr_col: cols_to_search.append(addr_col)

    if cols_to_search:
        mask = False
        for c in cols_to_search:
            mask = mask | df_ok[c].astype(str).str.lower().str.contains(ql, na=False)
        df_view = df_ok[mask].copy()
    else:
        df_view = df_ok.copy()
else:
    df_view = df_ok.copy()

# ---- Map center (Tahoe default, or based on filtered results) ----
if len(df_view) > 0:
    center_lat = float(df_view["Latitude"].mean())
    center_lon = float(df_view["Longitude"].mean())
else:
    # Tahoe-ish fallback
    center_lat, center_lon = 39.17, -120.14

# ---- Tooltip ----
tooltip_parts = []
if name_col:
    tooltip_parts.append(f"<b>{name_col}:</b> {{{name_col}}}")
if addr_col:
    tooltip_parts.append(f"<b>{addr_col}:</b> {{{addr_col}}}")
tooltip_parts.append("<b>Lat:</b> {Latitude}")
tooltip_parts.append("<b>Lon:</b> {Longitude}")

tooltip = {
    "html": "<br/>".join(tooltip_parts),
    "style": {"backgroundColor": "white", "color": "black"},
}

# ---- Layer ----
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_view,
    get_position=["Longitude", "Latitude"],
    get_radius=35,
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=11,
    pitch=0,
)

st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=None,  # keep default (works without a Mapbox token)
    ),
    use_container_width=True,
)

# ---- Table ----
if show_table:
    display_cols = []
    if name_col: display_cols.append(name_col)
    if addr_col: display_cols.append(addr_col)
    display_cols += ["Latitude", "Longitude"]

    st.dataframe(df_view[display_cols], use_container_width=True)

