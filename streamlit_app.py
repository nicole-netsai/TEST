import streamlit as st
import random
import time
from datetime import datetime
import pandas as pd
import plotly.express as px

# App Configuration
st.set_page_config(
    page_title="University of Zimbabwe Smart Parking System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# University Parking Data
CAMPUS_PARKING = {
    "Great Hall": {
        "capacity": 31,
        "rate": "0.70/hr",
        "location": "Near Main Entrance",
        "coords": (37.7749, -122.4194),
        "special": "Visitor Parking/ Great Hall Candidates"
    },
    "Faculty of Science": {
        "capacity": 200,
        "rate": "1.00/hr",
        "location": "MLT and SLT Buildings",
        "coords": (37.7755, -122.4180),
        "special": "Reserved for Students and Lecturers"
    },
    "Student Union Lot": {
        "capacity": 40,
        "rate": "1.00/hr",
        "location": "Next to Student Center",
        "coords": (37.7735, -122.4210),
        "special": "Student Permits"
    },
    "Athletics Field Parking": {
        "capacity": 150,
        "rate": "1.50/hr",
        "location": "Near Sports Complex",
        "coords": (37.7760, -122.4200),
        "special": "Event Parking"
    }
}

# Initialize Session State
if 'parking_data' not in st.session_state:
    st.session_state.parking_data = {
        name: {
            "occupied": random.randint(int(info["capacity"]*0.4), int(info["capacity"]*0.8)),
            "last_updated": datetime.now(),
            "reservations": []
        } 
        for name, info in CAMPUS_PARKING.items()
    }

# UI Components
def show_parking_map():
    """Interactive campus parking map"""
    map_data = []
    for name, info in CAMPUS_PARKING.items():
        available = info["capacity"] - st.session_state.parking_data[name]["occupied"]
        map_data.append({
            "Lot": name,
            "Latitude": info["coords"][0],
            "Longitude": info["coords"][1],
            "Available": available,
            "Capacity": info["capacity"],
            "Rate": info["rate"],
            "Status": "🟢 Good" if available > 20 else "🟡 Limited" if available > 0 else "🔴 Full"
        })
    
    df = pd.DataFrame(map_data)
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Lot",
        hover_data=["Available", "Capacity", "Rate", "Status"],
        color="Status",
        zoom=15,
        height=500,
        mapbox_style="open-street-map"
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

def parking_lot_card(name, info):
    """UI card for each parking lot"""
    occupied = st.session_state.parking_data[name]["occupied"]
    available = info["capacity"] - occupied
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(name)
            st.caption(f"📍 {info['location']}")
            st.caption(f"🎯 {info['special']}")
        with col2:
            st.metric("Available", f"{available}/{info['capacity']}")
        
        # Visual indicators
        progress_val = available/info["capacity"]
        if progress_val > 0.3:
            st.progress(progress_val, f"{int(progress_val*100)}% available")
        else:
            st.progress(progress_val, "Limited spaces!", )
        
        # Action buttons
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🔍 View Details", key=f"view_{name}"):
                st.session_state.selected_lot = name
                st.session_state.current_view = "detail"
                st.rerun()
        with btn_col2:
            if st.button("🗺️ Get Directions", key=f"dir_{name}"):
                st.session_state.show_directions = name
                st.rerun()

# Main App
def main():
    # Custom CSS
    st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .lot-card {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://cdn1.iconfinder.com/data/icons/higher-education/66/5-1024.png", width=150)
        st.title("Campus Parking")
        
        view_options = {
            "map": "🗺️ Parking Map",
            "list": "📋 All Parking Lots", 
            "reserve": "🅿️ Reserve Spot",
            "admin": "🔒 Admin Portal"
        }
        
        current_view = st.radio(
            "Navigation",
            options=list(view_options.values()),
            index=0,
            key="current_view"
        )
        
        st.markdown("---")
        st.caption(f"Last Updated: {datetime.now().strftime('%m/%d %I:%M %p')}")

    # Main Content Area
    if current_view == view_options["map"]:
        st.header("Campus Parking Map")
        show_parking_map()
        
        if st.session_state.get("show_directions"):
            lot = st.session_state.show_directions
            st.info(f"Directions to {lot}: {CAMPUS_PARKING[lot]['location']}")
            # Embedded Google Maps would go here
            st.map(pd.DataFrame({
                "lat": [CAMPUS_PARKING[lot]["coords"][0]],
                "lon": [CAMPUS_PARKING[lot]["coords"][1]]
            }), zoom=16)
            
            if st.button("Close Directions"):
                st.session_state.show_directions = None
                st.rerun()

    elif current_view == view_options["list"]:
        st.header("All Parking Facilities")
        
        search = st.text_input("Search parking lots", key="parking_search")
        
        filtered_lots = {
            name: info for name, info in CAMPUS_PARKING.items() 
            if search.lower() in name.lower() or search.lower() in info["location"].lower()
        }
        
        for name, info in filtered_lots.items():
            parking_lot_card(name, info)

    elif current_view == view_options["reserve"]:
        st.header("Reserve Parking Spot")
        
        selected = st.selectbox(
            "Select parking lot",
            options=list(CAMPUS_PARKING.keys()),
            index=0,
            key="reserve_lot"
        )
        
        info = CAMPUS_PARKING[selected]
        occupied = st.session_state.parking_data[selected]["occupied"]
        available = info["capacity"] - occupied
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(selected)
            st.image("https://via.placeholder.com/500x300?text=Lot+"+selected.replace(" ", "+"), 
                    use_column_width=True)
        with col2:
            st.metric("Available Spots", available)
            st.caption(f"Total Capacity: {info['capacity']}")
            st.write(f"**Rate:** {info['rate']}")
            st.write(f"**Location:** {info['location']}")
            st.write(f"**Special:** {info['special']}")
            
            if available > 0:
                with st.form(key="reservation_form"):
                    st.selectbox("Permit Type", ["Student", "Faculty", "Visitor", "Event"])
                    st.text_input("Vehicle License Plate")
                    st.time_input("Estimated Arrival Time")
                    
                    if st.form_submit_button("Reserve Spot", type="primary"):
                        st.session_state.parking_data[selected]["occupied"] += 1
                        st.session_state.parking_data[selected]["reservations"].append({
                            "time": datetime.now(),
                            "plate": "ABC123",  # Would come from form
                            "user": "Current User"  # Would be authenticated user
                        })
                        st.success("Reservation confirmed!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.error("No available spots in this lot")

    elif current_view == view_options["admin"]:
        st.header("Admin Portal")
        
        # Simple auth
        password = st.text_input("Enter admin password", type="password")
        if password != "campus123":
            st.error("Incorrect password")
            st.stop()
        
        st.success("Admin access granted")
        
        tab1, tab2 = st.tabs(["Parking Status", "Analytics"])
        
        with tab1:
            st.subheader("Manage Parking Lots")
            
            for name, info in CAMPUS_PARKING.items():
                with st.expander(name):
                    current = st.session_state.parking_data[name]["occupied"]
                    new_val = st.number_input(
                        "Occupied spots",
                        min_value=0,
                        max_value=info["capacity"],
                        value=current,
                        key=f"admin_{name}"
                    )
                    
                    if st.button(f"Update {name}", key=f"update_{name}"):
                        st.session_state.parking_data[name]["occupied"] = new_val
                        st.session_state.parking_data[name]["last_updated"] = datetime.now()
                        st.success("Updated successfully!")
                        time.sleep(0.5)
                        st.rerun()
        
        with tab2:
            st.subheader("Parking Analytics")
            
            # Sample data visualization
            data = []
            for name, info in CAMPUS_PARKING.items():
                data.append({
                    "Lot": name,
                    "Capacity": info["capacity"],
                    "Occupied": st.session_state.parking_data[name]["occupied"],
                    "Utilization": st.session_state.parking_data[name]["occupied"] / info["capacity"] * 100
                })
            
            df = pd.DataFrame(data)
            
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(df, x="Lot", y=["Capacity", "Occupied"])
            with col2:
                st.metric("Total Campus Capacity", sum(info["capacity"] for info in CAMPUS_PARKING.values()))
                st.metric("Current Utilization", f"{sum(data['Occupied'] for data in df)/sum(data['Capacity'] for data in df)*100:.1f}%")

    # Footer
    st.markdown("---")
    st.caption("© 2023 University Campus Parking System | v1.0")

if __name__ == "__main__":
    main()
