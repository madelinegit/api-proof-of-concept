import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import time

st.title("Property Map Prototype")

uploaded_file = st.file_uploader(
    "Upload CSV with an Address or Unit Address column", type=["csv"]
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Detect which column contains addresses
    address_col = None

    if "Address" in df.columns:
        address_col = "Address"
    elif "Unit Address" in df.columns:
        address_col = "Unit Address"
    else:
        st.error("CSV must contain a column named 'Address' or 'Unit Address'")
        st.stop()

    geolocator = Nominatim(user_agent="property_mapper")

    coords = []
    st.write("Geocoding addresses...")

    for address in df[address_col]:
        try:
            location = geolocator.geocode(address)
            if location:
                coords.append((location.latitude, location.longitude))
            else:
                coords.append((None, None))
            time.sleep(1)  # Avoid rate limiting
        except:
            coords.append((None, None))

    df["Latitude"] = [c[0] for c in coords]
    df["Longitude"] = [c[1] for c in coords]

    valid_rows = df.dropna(subset=["Latitude", "Longitude"])

    if len(valid_rows) > 0:
        center_lat = valid_rows.iloc[0]["Latitude"]
        center_lon = valid_rows.iloc[0]["Longitude"]

        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

        for _, row in valid_rows.iterrows():
            folium.Marker(
                [row["Latitude"], row["Longitude"]],
                popup=str(row[address_col])
            ).add_to(m)

        st_folium(m, width=700, height=500)
    else:
        st.warning("No addresses could be mapped.")
