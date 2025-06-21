import streamlit as st
import pandas as pd
import folium
import json
from geopy.distance import geodesic
from folium.plugins import LocateControl, MousePosition
from streamlit_folium import st_folium

st.set_page_config(page_title="Nursery Locator", layout="wide")
st.title("🌱 Public Nursery Locator – Khariar Division")

# ✅ Load Excel file
df = pd.read_excel("NURSARY.xlsx")

required_cols = ['Name', 'Latitude', 'Longitude', 'Capacity', 'PlantsAvailable', 'Contact']
if not all(col in df.columns for col in required_cols):
    st.error("❌ Excel must include: " + ", ".join(required_cols))
    st.stop()

# ✅ Load Khariar Boundary GeoJSON
with open("khariar_boundary.geojson", "r") as f:
    khariar_geojson = json.load(f)

# 🧭 Let user pick location manually or use default
st.sidebar.header("📍 Your Location")
use_default = st.sidebar.checkbox("Use default location (Khariar)", value=True)

if use_default:
    user_location = (20.5600, 84.1400)  # Khariar default
else:
    lat = st.sidebar.number_input("Latitude", value=20.5600, format="%.6f")
    lon = st.sidebar.number_input("Longitude", value=84.1400, format="%.6f")
    user_location = (lat, lon)

# 📍 Create folium map
m = folium.Map(location=user_location, zoom_start=12)
LocateControl(auto_start=True).add_to(m)

# Add mouse position tracker
MousePosition().add_to(m)

# Add Khariar boundary
folium.GeoJson(
    khariar_geojson,
    name="Khariar Division",
    style_function=lambda feature: {
        'fillColor': 'yellow',
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.1
    }
).add_to(m)

# Add nursery markers
for _, row in df.iterrows():
    popup = f"<b>{row['Name']}</b><br>Capacity: {row['Capacity']}<br>Plants: {row['PlantsAvailable']}<br>Contact: {row['Contact']}"
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup,
        icon=folium.Icon(color='green', icon='leaf')
    ).add_to(m)

# Add user marker
folium.Marker(
    location=user_location,
    tooltip="Your Location",
    icon=folium.Icon(color='blue', icon='user')
).add_to(m)

# Find and mark nearest nursery
df['Distance_km'] = df.apply(
    lambda row: geodesic(user_location, (row['Latitude'], row['Longitude'])).km,
    axis=1
)
nearest = df.loc[df['Distance_km'].idxmin()]
folium.Marker(
    location=[nearest['Latitude'], nearest['Longitude']],
    popup=f"<b>Nearest Nursery:</b><br>{nearest['Name']}<br>Distance: {nearest['Distance_km']:.2f} km<br>Capacity: {nearest['Capacity']}<br>Plants: {nearest['PlantsAvailable']}<br>Contact: {nearest['Contact']}",
    icon=folium.Icon(color='red', icon='star')
).add_to(m)

# Zoom to Khariar region
m.fit_bounds([[20.4, 83.9], [20.7, 84.3]])

st.subheader("🗺️ Interactive Map")
st_data = st_folium(m, width=1000, height=600)

# 📍 Nearest Nursery Info
st.subheader("📍 Nearest Nursery Details")
st.markdown(f"""
**Name:** {nearest['Name']}  
**Distance:** {nearest['Distance_km']:.2f} km  
**Capacity:** {nearest['Capacity']}  
**Plants Available:** {nearest['PlantsAvailable']}  
**Contact:** {nearest['Contact']}
""")
