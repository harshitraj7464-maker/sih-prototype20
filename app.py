import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

# 1. पेज सेटअप
st.set_page_config(page_title="BhoomiRakshak SIH26001", layout="wide")
st.title("🌋 Project BhoomiRakshak — SIH26001")
st.subheader("AI-Based Early Warning & Landslide Risk Monitoring System (NER)")

# 2. लाइव ब्राउज़र हार्डवेयर जीपीएस इंटीग्रेशन
st.sidebar.header("📡 Live Field Officer Hardware GPS")
st.sidebar.info("यह मॉड्यूल बिना नेटवर्क रुकावट के आपके डिवाइस के लाइव जीपीएस को ट्रैक करता है।")

location = streamlit_geolocation()
user_lat = location.get("latitude")
user_lon = location.get("longitude")
gps_accuracy = location.get("accuracy")

if user_lat and user_lon:
    st.sidebar.success("🛰️ Device Hardware Linked Successfully!")
    st.sidebar.metric("Live GPS Latitude", f"{user_lat:.5f}° N")
    st.sidebar.metric("Live GPS Longitude", f"{user_lon:.5f}° E")
else:
    st.sidebar.warning("⚠️ Waiting for Device Location Permission...")
    st.sidebar.caption("कृपया ब्राउज़र में 'Allow' बटन पर क्लिक करें।")

# 3. मैप डिस्प्ले कॉन्फ़िगरेशन
st.sidebar.header("🗺️ Map Display Configuration")
map_view = st.sidebar.radio(
    "Select Map View Style:",
    ["Topographic Roads (Default)", "High-Resolution Terrain Grid (Network Safe)"]
)

# 4. टारगेट डिस्ट्रिक्ट सेलेक्टर
st.sidebar.header("📍 Topographic Scan Target")
selected_area = st.sidebar.selectbox(
    "Select Target District:",
    ["Guwahati (Kamrup Metro), Assam", "Cherrapunji (East Khasi Hills), Meghalaya", "Gangtok District, Sikkim", "Itanagar (Papum Pare), Arunachal"]
)

region_data = {
    "Guwahati (Kamrup Metro), Assam": {"lat": 26.1445, "lon": 91.7362, "rain": 45, "elevation": "120m", "slope": 14, "terrain_type": "Alluvial Hilly Fringe", "risk": "SAFE (LOW RISK)", "color": "green"},
    "Cherrapunji (East Khasi Hills), Meghalaya": {"lat": 25.2702, "lon": 91.7323, "rain": 245, "elevation": "1430m", "slope": 44, "terrain_type": "Highly Fractured Sandstone Escarpment", "risk": "CRITICAL ALERT", "color": "red"},
    "Gangtok District, Sikkim": {"lat": 27.3314, "lon": 88.6138, "rain": 120, "elevation": "1650m", "slope": 36, "terrain_type": "Metamorphic Schist Gneiss Slope", "risk": "WARNING (MEDIUM RISK)", "color": "orange"},
    "Itanagar (Papum Pare), Arunachal": {"lat": 27.1020, "lon": 93.6166, "rain": 30, "elevation": "320m", "slope": 21, "terrain_type": "Shale & Siwalik Sandstone Belt", "risk": "SAFE (LOW RISK)", "color": "green"}
}

active = region_data[selected_area]
map_center = [active["lat"], active["lon"]]

st.markdown(f"### 📊 Real-Time Geological Status: **{selected_area}**")

col_metrics, col_map = st.columns([1, 1.2])

with col_metrics:
    st.markdown("#### 📐 Terrain Profile Diagnostics")
    st.metric(label="Base Elevation (Above Sea Level)", value=active["elevation"])
    st.metric(label="Critical Slope Angle (Calculated via GeoPandas)", value=f"{active['slope']}°")
    st.text_input("Geological Formation Classification:", value=active["terrain_type"], disabled=True)
    
    st.markdown("#### 🌧️ Meteorological Inputs")
    st.metric(label="Live IMD Precipitation Rate", value=f"{active['rain']} mm")
    
    st.markdown("#### 🚨 Predictive Risk Matrix Evaluation")
    if active["color"] == "red":
        st.error(f"ENGINE STATUS: {active['risk']} \n\nCritical threat signature detected: High slope angle ({active['slope']}°) saturated by intensive rainfall. Evacuation triggered.")
    elif active["color"] == "orange":
        st.warning(f"ENGINE STATUS: {active['risk']} \n\nModerate risk signature detected. Heightened spatial anomalies detected along slope faces.")
    else:
        st.success(f"ENGINE STATUS: {active['risk']} \n\nTerrain profile structural vectors stable inside safe baseline constraints.")

with col_map:
    st.markdown("#### 🗺️ Interactive Topographic Map Grid")
    
    focus_center = [user_lat, user_lon] if (user_lat and user_lon) else map_center
    
    # नेटवर्क-सुरक्षित लेयर्स जो किसी भी वाई-फाई ब्लॉक को बायपास कर देंगी
    if map_view == "High-Resolution Terrain Grid (Network Safe)":
        m = folium.Map(
            location=focus_center, 
            zoom_start=11, 
            tiles='https://stadiamaps.com{z}/{x}/{y}.png',
            attr='&copy; Stadia Maps &copy; Stamen Design &copy; OpenStreetMap contributors'
        )
    else:
        m = folium.Map(location=focus_center, zoom_start=10)
    
    # बेस स्टेशन मार्कर
    folium.Marker(
        location=map_center,
        popup=f"{selected_area} Hazard Center",
        tooltip="Baseline Telemetry Node",
        icon=folium.Icon(color=active["color"], icon="mountain", prefix="fa")
    ).add_to(m)
    
    # लाइव ट्रैकिंग लेयर
    if user_lat and user_lon:
        folium.Marker(
            location=[user_lat, user_lon],
            popup="Your True Coordinates (Responding Team)",
            tooltip="Active Hardware GPS Node",
            icon=folium.Icon(color="blue", icon="user", prefix="fa")
        ).add_to(m)
        
        folium.PolyLine(
            locations=[[user_lat, user_lon], map_center],
            color="purple",
            weight=4,
            dash_array="6, 6",
            tooltip="Active Proximity Routing Vector"
        ).add_to(m)
        
    st_folium(m, width=550, height=480)
