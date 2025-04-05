import streamlit as st
import cv2
import numpy as np
from datetime import datetime
import time
import pandas as pd
from app-model import ParkingModel
from app.utils import ParkingUtils
from app.config import PARKING_LOTS, ADMIN_CREDENTIALS, GOOGLE_MAPS_API_KEY

# Initialize parking model
parking_model = ParkingModel()

# Database simulation
parking_data = {
    lot_name: {
        "total": lot["capacity"],
        "occupied": random.randint(int(lot["capacity"]*0.5), int(lot["capacity"]*0.8)),
        "last_updated": datetime.now()
    } for lot_name, lot in PARKING_LOTS.items()
}

def main():
    st.set_page_config(page_title="Smart Parking System", layout="wide")
    st.title("University Campus Parking Management")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.header("Navigation")
    app_mode = st.sidebar.selectbox("Choose a view", 
                                  ["Parking Availability", "Find Parking", "Reserve & Pay", "Admin Dashboard"])
    
    if app_mode == "Parking Availability":
        show_parking_availability()
    elif app_mode == "Find Parking":
        show_find_parking()
    elif app_mode == "Reserve & Pay":
        show_reserve_pay()
    elif app_mode == "Admin Dashboard":
        show_admin_dashboard()

def show_parking_availability():
    st.header("Real-time Parking Availability")
    
    cols = st.columns(len(PARKING_LOTS))
    for idx, (lot_name, lot) in enumerate(PARKING_LOTS.items()):
        with cols[idx]:
            show_lot_status(lot_name, lot)
    
    st.subheader("Campus Parking Map")
    show_campus_map()

def show_lot_status(lot_name, lot):
    st.subheader(lot_name)
    
    # Get video frame
    frame, _ = ParkingUtils.get_video_frame(lot["video"], int(time.time()) % 30)
    st.image(frame, caption=f"Live feed: {lot_name}", use_column_width=True)
    
    # Process with VGG16 model
    with st.spinner("Analyzing parking spots..."):
        vacant = parking_model.predict_vacancy(frame)
    
    # Update parking data
    if vacant:
        parking_data[lot_name]["occupied"] = max(0, parking_data[lot_name]["occupied"] - 1)
    else:
        parking_data[lot_name]["occupied"] = min(
            lot["capacity"], 
            parking_data[lot_name]["occupied"] + 1
        )
    parking_data[lot_name]["last_updated"] = datetime.now()
    
    # Display info
    available = parking_data[lot_name]["total"] - parking_data[lot_name]["occupied"]
    st.metric("Available Spots", value=available)
    st.progress(available / parking_data[lot_name]["total"])
    
    if st.button(f"Directions to {lot_name}"):
        st.markdown(f"[Open in Google Maps]({ParkingUtils.get_google_maps_direction(lot['coords'])})", 
                   unsafe_allow_html=True)

def show_campus_map():
    markers = "&".join([
        f"markers=color:{'green' if (parking_data[lot]['total'] - parking_data[lot]['occupied']) > 5 else 'orange' if (parking_data[lot]['total'] - parking_data[lot]['occupied']) > 0 else 'red'}"
        f"%7C{data['coords'][0]},{data['coords'][1]}"
        for lot, data in PARKING_LOTS.items()
    ])
    
    map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={CAMPUS_COORDINATES[0]},{CAMPUS_COORDINATES[1]}&zoom=16&size=800x400&maptype=roadmap&{markers}&key={GOOGLE_MAPS_API_KEY}"
    st.image(map_url, use_column_width=True)
    st.caption("Green: Available, Orange: Limited, Red: Full")

# [Other functions (show_find_parking, show_reserve_pay, show_admin_dashboard) would be implemented similarly]

if __name__ == "__main__":
    main()
