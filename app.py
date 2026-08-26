import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import contextlib

# ==============================================================================
# 1. Backend Imports
# ==============================================================================
from Parkinglot import ParkingLot
from parkingspot import ParkingSpot
from DataManager import DataManager
from Car import Car
from Motorcycle import Motorcycle
from Truck import Truck
from Simulation import ParkingSimulation
from exceptions import (
    DuplicateVehicleError,
    VehicleNotFoundError,
    InvalidSpotError,
    DataFileError
)

# ==============================================================================
# 2. Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="Smart Parking Management System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 3. Custom CSS & Styling (Modern SaaS Theme)
# ==============================================================================
def load_custom_css():
    """Injects custom CSS styling for a polished, modern SaaS interface."""
    st.markdown("""
    <style>
        /* Main background and font adjustments */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Top Branding Header Styling (Feature 1) */
        .brand-header-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            padding: 22px 28px;
            border-radius: 16px;
            color: #ffffff;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.12);
        }
        .brand-header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            padding-bottom: 12px;
            margin-bottom: 12px;
        }
        .brand-logo-title {
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #ffffff;
        }
        .brand-tagline {
            display: block;
            color: #94a3b8;
            font-size: 13px;
            font-weight: 500;
            margin-top: 2px;
        }
        .brand-location-badge {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: #e2e8f0;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        .brand-page-info h2 {
            color: #f8fafc;
            margin: 0;
            font-size: 20px;
            font-weight: 700;
        }
        .brand-page-info p {
            color: #cbd5e1;
            margin: 3px 0 0 0;
            font-size: 13px;
        }

        /* KPI Metric Cards */
        .kpi-container {
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }
        .kpi-card {
            background: #ffffff;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            transition: all 0.25s ease;
        }
        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
            border-color: #cbd5e1;
        }
        .kpi-title {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 26px;
            font-weight: 700;
            color: #0f172a;
            margin: 0;
        }
        .kpi-subtext {
            font-size: 12px;
            margin-top: 4px;
            color: #10b981;
            font-weight: 500;
        }

        /* Parking Spot Cards */
        .spot-card {
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 16px;
            transition: all 0.25s ease;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
            position: relative;
            overflow: hidden;
        }
        .spot-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
        }
        .spot-available {
            background: linear-gradient(to bottom right, #f0fdf4, #dcfce7);
            border: 1.5px solid #86efac;
        }
        .spot-occupied {
            background: linear-gradient(to bottom right, #fef2f2, #fee2e2);
            border: 1.5px solid #fca5a5;
        }
        .spot-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            border-bottom: 1px dashed rgba(0,0,0,0.1);
            padding-bottom: 8px;
        }
        .spot-id {
            font-size: 18px;
            font-weight: 700;
            color: #1e293b;
        }

        /* Badges & Chips */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .badge-available {
            background-color: #10b981;
            color: #ffffff;
        }
        .badge-occupied {
            background-color: #ef4444;
            color: #ffffff;
        }
        .badge-regular {
            background-color: #e0e7ff;
            color: #3730a3;
        }
        .badge-large {
            background-color: #fef3c7;
            color: #92400e;
        }
        .badge-plate {
            background-color: #1e293b;
            color: #f8fafc;
            font-family: monospace;
            font-size: 13px;
            padding: 4px 8px;
            border-radius: 6px;
        }

        /* Payment Receipt Box */
        .receipt-card {
            background: #ffffff;
            border-radius: 14px;
            padding: 24px;
            border: 2px dashed #cbd5e1;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            margin-top: 16px;
        }
        .receipt-header {
            text-align: center;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 12px;
            margin-bottom: 16px;
        }
        .receipt-total {
            background: #f8fafc;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            margin-top: 16px;
            border: 1px solid #e2e8f0;
        }
        
        /* Modern Buttons & Forms */
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            padding: 8px 16px;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(67, 97, 238, 0.25);
        }
        
        /* Sidebar Polish (Light & High Contrast) */
        [data-testid="stSidebar"] {
            background-color: #f8fafc !important;
            border-right: 1px solid #e2e8f0;
        }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div {
            color: #0f172a;
        }
        [data-testid="stSidebar"] .stRadio label {
            color: #1e293b !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            padding: 6px 10px;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            background-color: #e2e8f0 !important;
            color: #4361ee !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: #e2e8f0 !important;
        }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# 4. Session State Initialization
# ==============================================================================
def init_system():
    """
    Initializes ParkingLot and DataManager instances once in session state.
    Creates 5 initial spots (3 Regular: IDs 1-3, 2 Large: IDs 4-5) as in main.py.
    """
    if "parking_lot" not in st.session_state:
        # Create ParkingLot instance
        lot = ParkingLot("Main City Parking")
        
        # Add default spots
        lot.add_spot(ParkingSpot(1, "Regular"))
        lot.add_spot(ParkingSpot(2, "Regular"))
        lot.add_spot(ParkingSpot(3, "Regular"))
        lot.add_spot(ParkingSpot(4, "Large"))
        lot.add_spot(ParkingSpot(5, "Large"))
        
        # Connect DataManager to ParkingLot
        dm = DataManager(lot)
        
        # Persist instances in session_state
        st.session_state.parking_lot = lot
        st.session_state.data_manager = dm
        st.session_state.parking_lot_name = "Main City Parking"

# Run state initialization
init_system()

# Shortcuts to persistent instances
parking_lot: ParkingLot = st.session_state.parking_lot
data_manager: DataManager = st.session_state.data_manager


# ==============================================================================
# Helper Functions
# ==============================================================================
def get_transaction_log_list(dm: DataManager):
    """Safely retrieves the transaction log list from DataManager."""
    if hasattr(dm, "get_transaction_log"):
        return dm.get_transaction_log()
    return getattr(dm, "_DataManager__transaction_log", [])


def render_page_header(title: str, subtitle: str, icon: str = "🚗"):
    """
    Renders a custom branded header at the top of the app (Feature 1):
    - Project name ('🚗 ParkEase') in bold, large custom typography
    - Tagline ('Smart Parking, Simplified') in muted text
    - Facility badge & active page title context
    """
    st.markdown(f"""
    <div class="brand-header-card">
        <div class="brand-header-top">
            <div>
                <span class="brand-logo-title">🚗 ParkEase</span>
                <span class="brand-tagline">Smart Parking, Simplified</span>
            </div>
            <div class="brand-location-badge">
                📍 {st.session_state.parking_lot_name}
            </div>
        </div>
        <div class="brand-page-info">
            <h2>{icon} {title}</h2>
            <p>{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_empty_state(icon: str, message: str, subtext: str = ""):
    """Renders a visually pleasing, centered empty state container."""
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 20px; background: #ffffff; border-radius: 14px; border: 1.5px dashed #cbd5e1; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
        <div style="font-size: 48px; margin-bottom: 10px;">{icon}</div>
        <h3 style="color: #1e293b; margin: 0 0 6px 0; font-size: 18px; font-weight: 700;">{message}</h3>
        {f'<p style="color: #64748b; font-size: 13px; margin: 0;">{subtext}</p>' if subtext else ''}
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 5. Page 1: 🏠 Dashboard
# ==============================================================================
def page_dashboard():
    render_page_header(
        title="Smart Parking Dashboard",
        subtitle=f"Facility: {st.session_state.parking_lot_name} • Real-time live status monitor",
        icon="🏠"
    )

    spots = parking_lot.get_spots()
    total_spots = len(spots)
    occupied_spots = sum(1 for s in spots if s.is_occupied())
    available_spots = total_spots - occupied_spots
    occupancy_rate = (occupied_spots / total_spots * 100) if total_spots > 0 else 0.0

    # Calculate Total Revenue from transaction logs
    log = get_transaction_log_list(data_manager)
    total_revenue = sum(float(entry.get("cost", 0) or 0) for entry in log if entry.get("action") == "exit")

    # Top KPI Metrics Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Capacity</div>
            <div class="kpi-value">{total_spots}</div>
            <div class="kpi-subtext">Total Managed Spots</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Available Spots</div>
            <div class="kpi-value" style="color: #10b981;">{available_spots}</div>
            <div class="kpi-subtext" style="color: #10b981;">● Ready for Entry</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Occupied Spots</div>
            <div class="kpi-value" style="color: #ef4444;">{occupied_spots}</div>
            <div class="kpi-subtext" style="color: #ef4444;">● Currently In Use</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Occupancy Rate</div>
            <div class="kpi-value">{occupancy_rate:.1f}%</div>
            <div class="kpi-subtext">Revenue: {total_revenue:.2f} EGP</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🅿️ Live Parking Spots Grid")

    # Visual Interactive Spot Cards
    spot_columns = st.columns(min(5, max(1, total_spots)))
    for idx, spot in enumerate(spots):
        with spot_columns[idx % len(spot_columns)]:
            spot_id = spot.get_spot_id()
            spot_type = spot.get_spot_type()
            is_occ = spot.is_occupied()
            type_class = "badge-regular" if spot_type == "Regular" else "badge-large"

            if is_occ:
                v = spot.get_vehicle()
                v_type = v.get_vehicle_type()
                plate = v.get_license_plate()
                entry_t = v.get_entry_time()
                time_str = entry_t.strftime("%H:%M:%S") if isinstance(entry_t, datetime) else str(entry_t)
                v_icon = "🚗" if v_type == "Car" else ("🏍️" if v_type == "Motorcycle" else "🚚")
                
                st.markdown(f"""
                <div class="spot-card spot-occupied">
                    <div class="spot-header">
                        <span class="spot-id">Spot #{spot_id}</span>
                        <span class="badge badge-occupied">Occupied</span>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span class="badge {type_class}">{spot_type}</span>
                    </div>
                    <p style="margin: 4px 0; font-size: 13px; font-weight: 600;">{v_icon} {v_type}</p>
                    <p style="margin: 4px 0;"><span class="badge-plate">{plate}</span></p>
                    <p style="margin: 6px 0 0 0; font-size: 12px; color: #64748b;">⏱️ In: <b>{time_str}</b></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="spot-card spot-available">
                    <div class="spot-header">
                        <span class="spot-id">Spot #{spot_id}</span>
                        <span class="badge badge-available">Available</span>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span class="badge {type_class}">{spot_type}</span>
                    </div>
                    <p style="color: #10b981; font-size: 13px; font-weight: 600; margin: 12px 0 4px 0;">✓ Open for Parking</p>
                    <p style="font-size: 12px; color: #64748b; margin: 0;">Fits: {spot_type}</p>
                </div>
                """, unsafe_allow_html=True)

    # Detailed Summary Dataframe
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Detailed Spot Inventory")
    table_rows = []
    for spot in spots:
        is_occ = spot.is_occupied()
        v = spot.get_vehicle() if is_occ else None
        table_rows.append({
            "Spot ID": spot.get_spot_id(),
            "Spot Type": spot.get_spot_type(),
            "Status": "Occupied 🔴" if is_occ else "Available 🟢",
            "Vehicle Type": v.get_vehicle_type() if v else "-",
            "License Plate": v.get_license_plate() if v else "-",
            "Entry Time": v.get_entry_time().strftime("%Y-%m-%d %H:%M:%S") if (v and isinstance(v.get_entry_time(), datetime)) else (str(v.get_entry_time()) if v else "-"),
            "Duration (Hrs)": f"{v.get_duration_hours():.2f}" if v else "-",
            "Current Cost (EGP)": f"{v.calculate_cost():.2f}" if v else "-"
        })
    
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)


# ==============================================================================
# 6. Page 2: 🚗 Park Vehicle
# ==============================================================================
def page_park_vehicle():
    render_page_header(
        title="Park a New Vehicle",
        subtitle="Register incoming vehicle details and allocate an optimal parking space",
        icon="🚗"
    )

    col_form, col_rules = st.columns([2, 1])

    with col_rules:
        st.markdown("""
        <div class="kpi-card" style="border-left: 4px solid #4361ee;">
            <h4 style="margin: 0 0 10px 0; color: #1e293b;">📋 Parking Policy & Rates</h4>
            <ul style="padding-left: 20px; font-size: 13px; color: #475569; margin-bottom: 0;">
                <li><b>🚗 Car:</b> 20.00 EGP/hour (Regular or Large)</li>
                <li><b>🏍️ Motorcycle:</b> 10.00 EGP/hour (Regular or Large)</li>
                <li><b>🚚 Truck:</b> 30.00 EGP/hour (Large Only)</li>
                <li><b>Minimum Charge:</b> 1 hour minimum billing.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_form:
        with st.form("park_vehicle_form", clear_on_submit=True):
            v_type = st.selectbox(
                "Select Vehicle Type",
                ["Car", "Motorcycle", "Truck"],
                index=0
            )

            plate_input = st.text_input(
                "License Plate Number",
                placeholder="e.g. ABC-123 or XYZ-909",
                help="Enter standard license plate alphanumeric identifier"
            )

            submit_btn = st.form_submit_button("Park Vehicle Now 🚗", use_container_width=True)

            if submit_btn:
                clean_plate = plate_input.strip().upper()

                if not clean_plate:
                    st.warning("⚠️ Please provide a non-empty license plate number.")
                else:
                    # Instantiate matching vehicle object
                    if v_type == "Car":
                        new_vehicle = Car(clean_plate)
                    elif v_type == "Motorcycle":
                        new_vehicle = Motorcycle(clean_plate)
                    elif v_type == "Truck":
                        new_vehicle = Truck(clean_plate)
                    else:
                        new_vehicle = Car(clean_plate)

                    # Execute registration with visual spinner
                    with st.spinner("Allocating spot and registering vehicle..."):
                        try:
                            data_manager.add_vehicle(new_vehicle)
                            
                            # Find allocated spot
                            _, spot = parking_lot.find_vehicle(clean_plate)
                            spot_id = spot.get_spot_id() if spot else "N/A"
                            spot_type = spot.get_spot_type() if spot else "N/A"

                            st.success(f"🎉 **Success!** Vehicle **{clean_plate}** ({v_type}) successfully parked in Spot **#{spot_id}** ({spot_type}).")
                            st.balloons()

                        except DuplicateVehicleError as e:
                            st.error(f"❌ **Duplicate Vehicle Error:** {e}")
                        except InvalidSpotError as e:
                            st.error(f"❌ **Spot Allocation Failed:** {e}")
                        except Exception as e:
                            st.error(f"❌ **System Error:** {e}")


# ==============================================================================
# 7. Page 3: 🚪 Exit Vehicle
# ==============================================================================
def page_exit_vehicle():
    render_page_header(
        title="Exit Vehicle & Settlement",
        subtitle="Process vehicle departure, release parking bay, and compute total fees",
        icon="🚪"
    )

    # Fetch currently occupied spots
    occupied_spots = [s for s in parking_lot.get_spots() if s.is_occupied()]

    if not occupied_spots:
        st.info("ℹ️ **No vehicles currently parked in the parking lot.** Park a vehicle first to test exit processing.")
        return

    col_action, col_rates = st.columns([2, 1])

    with col_rates:
        st.markdown("""
        <div class="kpi-card" style="border-left: 4px solid #10b981;">
            <h4 style="margin: 0 0 10px 0; color: #1e293b;">💳 Billing Calculator</h4>
            <p style="font-size: 13px; color: #475569; margin-bottom: 0;">
                Calculates elapsed duration and multiplies by vehicle hourly rate. Fractions of an hour rounded by standard duration formulas.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_action:
        # Build user-friendly selection list
        options = [
            f"{s.get_vehicle().get_license_plate()} ({s.get_vehicle().get_vehicle_type()} — Spot #{s.get_spot_id()})"
            for s in occupied_spots
        ]

        selected_str = st.selectbox("Select Parked Vehicle", options)
        target_plate = selected_str.split(" ")[0]

        # Duration simulation slider for testing various billing scenarios
        simulated_hours = st.slider(
            "Simulate Parking Duration (Hours) for Testing",
            min_value=0.0,
            max_value=24.0,
            value=2.0,
            step=0.5,
            help="Allows simulating test durations to verify cost calculation"
        )

        if st.button("Process Exit & Generate Bill 💳", type="primary", use_container_width=True):
            with st.spinner("Processing checkout and settling account..."):
                try:
                    # Get vehicle info before removal
                    v, spot = parking_lot.find_vehicle(target_plate)
                    v_type = v.get_vehicle_type()
                    entry_time = v.get_entry_time() if v else datetime.now()
                    
                    # Compute custom exit time based on simulation slider
                    custom_exit = entry_time + timedelta(hours=simulated_hours) if entry_time else datetime.now()

                    # Process exit via DataManager
                    cost = data_manager.delete_vehicle(target_plate, exit_time=custom_exit)

                    st.success("✅ **Vehicle exit processed successfully!**")

                    # Display Styled Receipt Card
                    st.markdown(f"""
                    <div class="receipt-card">
                        <div class="receipt-header">
                            <h3 style="margin: 0; color: #0f172a;">🧾 Official Parking Receipt</h3>
                            <p style="margin: 4px 0 0 0; color: #64748b; font-size: 12px;">{st.session_state.parking_lot_name}</p>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span><b>License Plate:</b></span>
                            <span class="badge-plate">{target_plate}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span><b>Vehicle Type:</b></span>
                            <span>{v_type}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span><b>Spot Freed:</b></span>
                            <span>Spot #{spot.get_spot_id()} ({spot.get_spot_type()})</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span><b>Entry Timestamp:</b></span>
                            <span>{entry_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(entry_time, datetime) else entry_time}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span><b>Exit Timestamp:</b></span>
                            <span>{v.get_exit_time().strftime('%Y-%m-%d %H:%M:%S') if isinstance(v.get_exit_time(), datetime) else v.get_exit_time()}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span><b>Billed Duration:</b></span>
                            <span>{v.get_duration_hours():.2f} hours</span>
                        </div>
                        <div class="receipt-total">
                            <div style="font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase;">Total Fee Due</div>
                            <div style="font-size: 28px; font-weight: 700; color: #10b981;">{cost:.2f} EGP</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                except VehicleNotFoundError as e:
                    st.error(f"❌ **Vehicle Not Found:** {e}")
                except Exception as e:
                    st.error(f"❌ **Exit Error:** {e}")


# ==============================================================================
# 8. Page 4: 🔍 Search
# ==============================================================================
def page_search():
    render_page_header(
        title="Vehicle Search & Query Center",
        subtitle="Lookup active parked vehicles by license plate, vehicle category, or sorted index",
        icon="🔍"
    )

    tab_plate, tab_type, tab_sort = st.tabs([
        "🔎 Search by License Plate",
        "🏷️ Search by Vehicle Type",
        "🔀 Sorted Active Vehicles"
    ])

    # --- Tab 1: Search by License Plate ---
    with tab_plate:
        st.subheader("Query by License Plate")
        search_input = st.text_input("Enter License Plate Number", placeholder="e.g. ABC-123")
        
        if st.button("Search Vehicle 🔍", key="search_plate_btn"):
            query_plate = search_input.strip().upper()
            if not query_plate:
                st.warning("⚠️ Please provide a license plate to search.")
            else:
                try:
                    v = data_manager.search_by_plate(query_plate)
                    _, spot = parking_lot.find_vehicle(query_plate)

                    st.success(f"✅ Record Found for License Plate: **{query_plate}**")
                    
                    entry_formatted = v.get_entry_time().strftime("%Y-%m-%d %H:%M:%S") if isinstance(v.get_entry_time(), datetime) else str(v.get_entry_time())
                    
                    res_col1, res_col2 = st.columns(2)
                    with res_col1:
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="kpi-title">Vehicle Specifications</div>
                            <p><b>Plate:</b> <span class="badge-plate">{v.get_license_plate()}</span></p>
                            <p><b>Type:</b> {v.get_vehicle_type()}</p>
                            <p><b>Assigned Spot:</b> Spot #{spot.get_spot_id()} ({spot.get_spot_type()})</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with res_col2:
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="kpi-title">Live Stay Information</div>
                            <p><b>Entry Time:</b> {entry_formatted}</p>
                            <p><b>Elapsed Duration:</b> {v.get_duration_hours():.2f} hours</p>
                            <p><b>Accrued Charges:</b> <b style="color:#10b981;">{v.calculate_cost():.2f} EGP</b></p>
                        </div>
                        """, unsafe_allow_html=True)

                except VehicleNotFoundError as e:
                    st.error(f"❌ **Search Result:** {e}")

    # --- Tab 2: Search by Vehicle Type ---
    with tab_type:
        st.subheader("Filter by Vehicle Type")
        filter_type = st.selectbox("Select Type to Filter", ["Car", "Motorcycle", "Truck"])
        
        vehicles_found = data_manager.search_by_type(filter_type)

        if vehicles_found:
            st.success(f"Found **{len(vehicles_found)}** parked **{filter_type}(s)**.")
            type_rows = []
            for v in vehicles_found:
                _, spot = parking_lot.find_vehicle(v.get_license_plate())
                type_rows.append({
                    "License Plate": v.get_license_plate(),
                    "Vehicle Type": v.get_vehicle_type(),
                    "Spot ID": spot.get_spot_id() if spot else "-",
                    "Spot Type": spot.get_spot_type() if spot else "-",
                    "Entry Time": v.get_entry_time().strftime("%Y-%m-%d %H:%M:%S") if isinstance(v.get_entry_time(), datetime) else str(v.get_entry_time()),
                    "Duration (Hours)": f"{v.get_duration_hours():.2f}",
                    "Accrued Cost (EGP)": f"{v.calculate_cost():.2f}"
                })
            st.dataframe(pd.DataFrame(type_rows), use_container_width=True, hide_index=True)
        else:
            st.info(f"ℹ️ No active **{filter_type}s** currently parked.")

    # --- Tab 3: Sorted Active Vehicles ---
    with tab_sort:
        st.subheader("Sort Active Parked Vehicles")
        sort_mode = st.radio("Select Sorting Metric:", ["Entry Time (Oldest to Newest)", "Current Cost (Highest to Lowest)"], horizontal=True)

        if sort_mode == "Entry Time (Oldest to Newest)":
            sorted_list = data_manager.sort_by_entry_time()
        else:
            sorted_list = data_manager.sort_by_cost(descending=True)

        if sorted_list:
            sort_rows = []
            for v in sorted_list:
                _, spot = parking_lot.find_vehicle(v.get_license_plate())
                sort_rows.append({
                    "License Plate": v.get_license_plate(),
                    "Vehicle Type": v.get_vehicle_type(),
                    "Spot": f"Spot #{spot.get_spot_id()} ({spot.get_spot_type()})" if spot else "-",
                    "Entry Time": v.get_entry_time().strftime("%Y-%m-%d %H:%M:%S") if isinstance(v.get_entry_time(), datetime) else str(v.get_entry_time()),
                    "Duration (Hours)": f"{v.get_duration_hours():.2f}",
                    "Cost (EGP)": f"{v.calculate_cost():.2f}"
                })
            st.dataframe(pd.DataFrame(sort_rows), use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ No active parked vehicles available to sort.")


# ==============================================================================
# 9. Page 5: 📋 Parking History
# ==============================================================================
def page_parking_history():
    render_page_header(
        title="Parking Transaction Audit Trail",
        subtitle="Historical log of all vehicle check-ins, check-outs, and collected revenues",
        icon="📋"
    )

    raw_log = get_transaction_log_list(data_manager)

    if not raw_log:
        st.info("ℹ️ No transaction history recorded yet. Enter or exit vehicles to generate logs.")
        return

    df_log = pd.DataFrame(raw_log)

    # Standardize column structure
    for col in ["action", "plate", "type", "time", "cost"]:
        if col not in df_log.columns:
            df_log[col] = None

    df_log = df_log[["action", "plate", "type", "time", "cost"]]
    df_log.columns = ["Action", "License Plate", "Vehicle Type", "Timestamp", "Cost (EGP)"]

    # History KPIs
    entries_count = (df_log["Action"] == "entry").sum()
    exits_count = (df_log["Action"] == "exit").sum()
    total_rev = df_log["Cost (EGP)"].dropna().astype(float).sum()

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Entries Logged", entries_count)
    with k2:
        st.metric("Total Exits Completed", exits_count)
    with k3:
        st.metric("Historical Revenue", f"{total_rev:.2f} EGP")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Transaction Log Filters")

    # Filters
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        selected_actions = st.multiselect("Filter by Action", options=["entry", "exit"], default=["entry", "exit"])
    with f_col2:
        selected_types = st.multiselect("Filter by Vehicle Type", options=["Car", "Motorcycle", "Truck"], default=["Car", "Motorcycle", "Truck"])

    filtered_df = df_log[df_log["Action"].isin(selected_actions) & df_log["Vehicle Type"].isin(selected_types)]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📥 Export & Import Audit Trail")
    exp_col, imp_col = st.columns(2)

    with exp_col:
        csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Transactions CSV",
            data=csv_bytes,
            file_name=f"parking_audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with imp_col:
        uploaded_csv = st.file_uploader("Import CSV Transaction File", type=["csv"])
        if uploaded_csv is not None:
            try:
                temp_path = "imported_audit_log.csv"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_csv.getbuffer())

                imported_entries = data_manager.load_log_from_csv(temp_path)
                st.success(f"✅ Successfully loaded {len(imported_entries)} transaction entries from CSV!")
                st.rerun()
            except DataFileError as e:
                st.error(f"❌ Failed to load CSV file: {e}")


# ==============================================================================
# 10. Page 6: 📊 Simulation & Charts
# ==============================================================================
# ==============================================================================
# 10. Page 6: 📊 Simulation & Charts
# ==============================================================================
def page_charts():
    render_page_header(
        title="Traffic Simulation & Behavioral Analytics",
        subtitle="High-fidelity discrete-event simulation engine with stochastic rush-hour traffic & telemetry",
        icon="📊"
    )

    st.subheader("⚙️ Simulation Controls")

    # Simulation Controls Top Card
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])

    with ctrl_col1:
        sim_duration = st.slider(
            "Simulation Duration (Hours)",
            min_value=1,
            max_value=168,
            value=24,
            step=1,
            help="Configure simulated duration between 1 hour and 1 full week (168 hours)."
        )

    with ctrl_col2:
        st.write("") # Spacer for vertical alignment
        st.write("")
        run_simulation_btn = st.button("▶️ Run Simulation", type="primary", use_container_width=True)

    with ctrl_col3:
        st.write("") # Spacer for vertical alignment
        st.write("")
        clear_sim_btn = st.button("🔄 Clear Results", use_container_width=True)

    # Handle Reset / Clear
    if clear_sim_btn:
        st.session_state.sim_results = None
        st.rerun()

    # Handle Run Simulation
    if run_simulation_btn:
        with st.spinner(f"🚀 Running stochastic simulation for {sim_duration} hours (15-minute intervals)..."):
            try:
                # 1. ISOLATED ENVIRONMENT: Create completely separate temporary instances
                temp_lot = ParkingLot("Simulation Sandbox Facility")
                temp_lot.add_spot(ParkingSpot(1, "Regular"))
                temp_lot.add_spot(ParkingSpot(2, "Regular"))
                temp_lot.add_spot(ParkingSpot(3, "Regular"))
                temp_lot.add_spot(ParkingSpot(4, "Large"))
                temp_lot.add_spot(ParkingSpot(5, "Large"))

                temp_dm = DataManager(temp_lot)

                # 2. Instantiate and run simulation
                sim = ParkingSimulation(temp_dm, temp_lot)

                # Suppress internal stdout prints during simulation run
                with contextlib.redirect_stdout(io.StringIO()):
                    stats = sim.run(duration_hours=sim_duration)

                # Collect results
                event_log = sim.get_event_log()
                occupancy_history = sim.get_occupancy_history()

                # 3. Store result payload in session_state
                st.session_state.sim_results = {
                    "stats": stats,
                    "event_log": event_log,
                    "occupancy_history": occupancy_history,
                    "duration": sim_duration,
                    "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                st.success(f"✅ Simulation completed successfully for **{sim_duration} hours**!")

            except Exception as e:
                st.error(f"❌ Error during simulation run: {e}")

    # Check if results exist
    sim_data = st.session_state.get("sim_results")

    if not sim_data:
        show_empty_state(
            icon="📊",
            message="No simulation run yet.",
            subtext="Set your desired duration above and click '▶️ Run Simulation' to generate rich analytical telemetry."
        )
        return

    # Extract stored results
    stats = sim_data["stats"]
    event_log = sim_data["event_log"]
    occupancy_history = sim_data["occupancy_history"]
    duration = sim_data["duration"]
    completed_at = sim_data.get("completed_at", "")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 12px 18px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
        <span style="font-size: 14px; color: #1e293b;"><b>Active Simulation Run:</b> {duration} Hours</span>
        <span style="font-size: 13px; color: #64748b;">Completed: {completed_at}</span>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # A) KPI Cards Row (7 Key Metrics)
    # ==========================================
    k_col1, k_col2, k_col3, k_col4 = st.columns(4)
    with k_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Vehicles Generated</div>
            <div class="kpi-value">{stats['total_entries']}</div>
            <div class="kpi-subtext">Arrival Attempts</div>
        </div>
        """, unsafe_allow_html=True)
    with k_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Successful Entries</div>
            <div class="kpi-value" style="color: #10b981;">{stats['successful_entries']}</div>
            <div class="kpi-subtext" style="color: #10b981;">✓ Parked Successfully</div>
        </div>
        """, unsafe_allow_html=True)
    with k_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Failed Entries</div>
            <div class="kpi-value" style="color: #ef4444;">{stats['failed_entries']}</div>
            <div class="kpi-subtext" style="color: #ef4444;">✕ Rejected (Full Lot)</div>
        </div>
        """, unsafe_allow_html=True)
    with k_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Exits</div>
            <div class="kpi-value">{stats['total_exits']}</div>
            <div class="kpi-subtext">Completed Parking Stays</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    k_col5, k_col6, k_col7 = st.columns(3)
    with k_col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Revenue</div>
            <div class="kpi-value" style="color: #10b981;">{stats['total_revenue']:.2f} EGP</div>
            <div class="kpi-subtext">Generated from Exits</div>
        </div>
        """, unsafe_allow_html=True)
    with k_col6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Occupancy</div>
            <div class="kpi-value">{stats['average_occupancy']:.1f}%</div>
            <div class="kpi-subtext">Mean Facility Utilization</div>
        </div>
        """, unsafe_allow_html=True)
    with k_col7:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Maximum Occupancy</div>
            <div class="kpi-value" style="color: #4361ee;">{stats['maximum_occupancy']:.1f}%</div>
            <div class="kpi-subtext">Peak Capacity Reached</div>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # B) Occupancy Over Time Area Chart
    # ==========================================
    if occupancy_history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📈 Space Utilization Over Time")
        df_occ = pd.DataFrame(occupancy_history)
        df_occ['time'] = pd.to_datetime(df_occ['time'])

        fig_occ = px.area(
            df_occ,
            x="time",
            y="occupancy",
            title="Occupancy Percentage Progression (%)",
            labels={"time": "Simulated Timeline", "occupancy": "Occupancy (%)"},
            color_discrete_sequence=["#4361ee"]
        )
        fig_occ.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
            yaxis=dict(range=[0, 105], title="Occupancy (%)"),
            xaxis=dict(title="Simulated Time"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_occ, use_container_width=True)

    # ==========================================
    # C & D) Hourly Traffic & Vehicle Type Distribution
    # ==========================================
    if event_log:
        df_events = pd.DataFrame(event_log)
        df_events['time'] = pd.to_datetime(df_events['time'])

        st.markdown("<br>", unsafe_allow_html=True)
        ch_col1, ch_col2 = st.columns(2)

        # C) Entries vs Exits Grouped by Hour
        with ch_col1:
            st.subheader("📊 Hourly Traffic: Entries vs Exits")
            # Group by 1-hour time buckets
            df_events['Hour'] = df_events['time'].dt.floor('h')
            traffic_counts = df_events.groupby(['Hour', 'action']).size().reset_index(name='Count')
            traffic_counts['Action'] = traffic_counts['action'].map({'entry': 'Entries', 'exit': 'Exits'})

            fig_traffic = px.bar(
                traffic_counts,
                x="Hour",
                y="Count",
                color="Action",
                barmode="group",
                color_discrete_map={"Entries": "#06b6d4", "Exits": "#f59e0b"},
                labels={"Hour": "Simulated Hour", "Count": "Vehicles"}
            )
            fig_traffic.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_traffic, use_container_width=True)

        # D) Vehicle Type Distribution Donut
        with ch_col2:
            st.subheader("🚗 Vehicle Type Distribution")
            df_entries = df_events[df_events['action'] == 'entry']
            if not df_entries.empty:
                v_type_counts = df_entries['type'].value_counts().reset_index()
                v_type_counts.columns = ['Vehicle Type', 'Count']

                fig_donut = px.pie(
                    v_type_counts,
                    names="Vehicle Type",
                    values="Count",
                    hole=0.5,
                    color="Vehicle Type",
                    color_discrete_map={"Car": "#4361ee", "Motorcycle": "#3a0ca3", "Truck": "#7209b7"}
                )
                fig_donut.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("No entry events recorded.")

        # ==========================================
        # E) Cumulative Revenue Over Time Chart
        # ==========================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💰 Cumulative Revenue Trajectory")
        df_exits = df_events[df_events['action'] == 'exit'].sort_values('time').copy()

        if not df_exits.empty and 'cost' in df_exits.columns:
            # Running cumulative revenue sum
            df_exits['Cumulative Revenue'] = df_exits['cost'].cumsum()

            fig_rev_line = px.line(
                df_exits,
                x="time",
                y="Cumulative Revenue",
                title="Accumulated Revenue Progression (EGP)",
                labels={"time": "Simulated Timeline", "Cumulative Revenue": "Revenue (EGP)"},
                color_discrete_sequence=["#10b981"],
                markers=True
            )
            fig_rev_line.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                hovermode="x unified",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_rev_line, use_container_width=True)
        else:
            st.info("ℹ️ No vehicles completed their parking duration in this window to generate revenue.")

        # ==========================================
        # F) Full Event Log Expander & CSV Export
        # ==========================================
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 View Full Simulation Event Ledger", expanded=False):
            # Format display dataframe
            display_events = df_events.copy()
            if 'time' in display_events.columns:
                display_events['time'] = display_events['time'].dt.strftime("%Y-%m-%d %H:%M:%S")

            st.dataframe(display_events, use_container_width=True, hide_index=True)

            csv_log_bytes = df_events.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Simulation Event Log (CSV)",
                data=csv_log_bytes,
                file_name=f"sim_events_{duration}h_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )


# ==============================================================================
# 11. Main Application Entrypoint
# ==============================================================================
def main():
    # Load custom styling
    load_custom_css()

    # Sidebar Header & Branding (Light Card Style)
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 12px 10px; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
        <h2 style="margin: 0; color: #0f172a; font-size: 22px; font-weight: 700;">🚗 SmartPark</h2>
        <p style="margin: 4px 0 0 0; color: #64748b; font-size: 12px; font-weight: 500;">Enterprise Parking Manager</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    menu_options = [
        "🏠 Dashboard",
        "🚗 Park Vehicle",
        "🚪 Exit Vehicle",
        "🔍 Search",
        "📋 Parking History",
        "📊 Simulation & Charts"
    ]

    selected_page = st.sidebar.radio("Navigation Menu", menu_options)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="font-size: 11px; color: #64748b; text-align: center; background: #ffffff; padding: 10px; border-radius: 10px; border: 1px solid #e2e8f0;">
        <b>Smart Parking System v2.0</b><br>
        <span style="color: #4361ee; font-weight: 600;">Streamlit & Plotly Edition</span>
    </div>
    """, unsafe_allow_html=True)

    # Route to designated page function
    if selected_page == "🏠 Dashboard":
        page_dashboard()
    elif selected_page == "🚗 Park Vehicle":
        page_park_vehicle()
    elif selected_page == "🚪 Exit Vehicle":
        page_exit_vehicle()
    elif selected_page == "🔍 Search":
        page_search()
    elif selected_page == "📋 Parking History":
        page_parking_history()
    elif selected_page == "📊 Simulation & Charts":
        page_charts()


if __name__ == "__main__":
    main()