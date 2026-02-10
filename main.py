# main.py
import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.sheets_manager import GoogleSheetsManager
from modules.data_models import Pilot, Drone, Mission

# --- Streamlit Cloud GCP credentials bootstrap ---
import json
import os
import streamlit as st

if "gcp_service_account" in st.secrets:
    creds_path = st.secrets.get("GOOGLE_SHEETS_CREDENTIALS_PATH", "gcp_credentials.json")

    if not os.path.exists(creds_path):
        with open(creds_path, "w") as f:
            json.dump(dict(st.secrets["gcp_service_account"]), f)

    os.environ["GOOGLE_SHEETS_CREDENTIALS_PATH"] = creds_path


# Gemini imports for conversational AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    st.warning("Google Generative AI not available. Install with: pip install google-generativeai")

# Configure Gemini API from secrets
if GEMINI_AVAILABLE and 'GEMINI_API_KEY' in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
elif GEMINI_AVAILABLE:
    st.warning("GEMINI_API_KEY not found in Streamlit secrets. AI Assistant will use fallback responses.")

# Page configuration
st.set_page_config(
    page_title="Drone Operations Coordinator AI Agent",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
    .conflict-alert {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #f44336;
    }
    .success-alert {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = None
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent' not in st.session_state:
    st.session_state.agent = None

@st.cache_resource
def get_sheets_manager():
    """Get or create Google Sheets manager"""
    try:
        return GoogleSheetsManager()
    except Exception as e:
        st.error(f"Failed to initialize Google Sheets: {str(e)}")
        return None

def refresh_data():
    """Refresh all data from Google Sheets"""
    if st.session_state.manager:
        st.session_state.manager.refresh_all()
        st.session_state.last_refresh = datetime.now()
        st.rerun()

def show_dashboard():
    """Display main dashboard"""
    st.markdown('<h1 class="main-header">🚁 Drone Operations Dashboard</h1>', unsafe_allow_html=True)
    
    manager = st.session_state.manager
    
    # Quick stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        pilots = manager.get_sheet_data('pilot_roster')
        if not pilots.empty:
            total_pilots = len(pilots)
            available = len(pilots[pilots['status'] == 'Available'])
            st.metric("Pilots", total_pilots, f"{available} available")
    
    with col2:
        drones = manager.get_sheet_data('drone_fleet')
        if not drones.empty:
            total_drones = len(drones)
            available = len(drones[drones['status'] == 'Available'])
            st.metric("Drones", total_drones, f"{available} available")
    
    with col3:
        missions = manager.get_sheet_data('missions')
        if not missions.empty:
            total_missions = len(missions)
            active = len(missions[missions['status'] == 'Active'])
            st.metric("Missions", total_missions, f"{active} active")
    
    with col4:
        if not missions.empty:
            # Check what columns are available
            available_cols = missions.columns.tolist()
            priority_col = None

            # Try different possible column names for priority
            for col in ['priority', 'Priority', 'PRIORITY', 'Priority Level', 'priority_level']:
                if col in available_cols:
                    priority_col = col
                    break

            if priority_col:
                try:
                    # Count high priority missions - handle different formats
                    priority_values = missions[priority_col].astype(str).str.upper()
                    high_priority_count = len(priority_values[priority_values.isin(['HIGH', 'CRITICAL', '1'])])
                    st.metric("High Priority", high_priority_count)
                except Exception as e:
                    st.metric("High Priority", f"Error: {str(e)[:20]}...")
            else:
                # If no priority column, show 0 or check for status-based priority
                if 'status' in available_cols:
                    # Count active missions as high priority proxy
                    active_count = len(missions[missions['status'].astype(str).str.upper() == 'ACTIVE'])
                    st.metric("High Priority", f"{active_count} active")
                else:
                    st.metric("High Priority", "0")
        else:
            st.metric("High Priority", "0")
    
    with col5:
        if st.session_state.last_refresh:
            st.metric("Last Refresh", st.session_state.last_refresh.strftime("%H:%M:%S"))
    
    st.divider()
    
    # Recent assignments
    st.subheader("📋 Recent Assignments")
    if not missions.empty:
        # Check if start_date column exists, otherwise sort by mission_id or use default order
        if 'start_date' in missions.columns:
            recent = missions.sort_values('start_date', ascending=False).head(5)
            display_columns = ['mission_id', 'client_name', 'assigned_pilot', 'start_date', 'status']
        else:
            recent = missions.head(5)
            display_columns = ['mission_id', 'client_name', 'assigned_pilot', 'status']

        # Filter to only include columns that exist
        available_columns = [col for col in display_columns if col in missions.columns]
        st.dataframe(recent[available_columns], width='stretch')
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh All Data", width='stretch'):
            refresh_data()

    with col2:
        if st.button("🔍 Check Conflicts", width='stretch'):
            st.session_state.show_conflicts = True
            st.rerun()

    with col3:
        if st.button("📊 View All Missions", width='stretch'):
            st.session_state.page = "missions"

def show_pilot_roster():
    """Display pilot roster management"""
    st.header("👨‍✈️ Pilot Roster Management")
    
    manager = st.session_state.manager
    pilots = manager.get_sheet_data('pilot_roster')
    
    if not pilots.empty:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=pilots['status'].unique(),
                default=[]
            )
        with col2:
            # Check if location column exists (try different possible names)
            location_col = None
            for col in ['current_location', 'location', 'Location']:
                if col in pilots.columns:
                    location_col = col
                    break

            if location_col:
                location_filter = st.multiselect(
                    "Filter by Location",
                    options=pilots[location_col].unique(),
                    default=[]
                )
            else:
                st.info("Location column not found in data")
                location_filter = []
        with col3:
            # Dynamic default columns based on available columns
            default_columns = ['pilot_id', 'name', 'status', 'skills']
            if location_col:
                default_columns.append(location_col)
            default_columns.append('current_assignment')

            # Filter to only include columns that exist
            available_defaults = [col for col in default_columns if col in pilots.columns]

            show_columns = st.multiselect(
                "Show Columns",
                options=pilots.columns.tolist(),
                default=available_defaults
            )
        
        # Apply filters
        filtered_pilots = pilots.copy()
        if status_filter:
            filtered_pilots = filtered_pilots[filtered_pilots['status'].isin(status_filter)]
        if location_filter and location_col:
            filtered_pilots = filtered_pilots[filtered_pilots[location_col].isin(location_filter)]
        
        # Display dataframe
        st.dataframe(
            filtered_pilots[show_columns] if show_columns else filtered_pilots,
            width='stretch',
            hide_index=True
        )
        
        # Update status
        st.subheader("Update Pilot Status")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            pilot_to_update = st.selectbox(
                "Select Pilot",
                options=pilots['pilot_id'].tolist(),
                format_func=lambda x: f"{x} - {pilots[pilots['pilot_id'] == x].iloc[0]['name']}"
            )
        
        with col2:
            new_status = st.selectbox(
                "New Status",
                options=['Available', 'On Leave', 'Unavailable', 'On Assignment']
            )
        
        with col3:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("Update", type="primary"):
                if manager.update_record('pilot_roster', pilot_to_update, {'status': new_status}):
                    st.success(f"✅ Updated {pilot_to_update} to {new_status}")
                    refresh_data()
                else:
                    st.error("❌ Failed to update status")
    else:
        st.warning("No pilot data available. Check your Google Sheets connection.")

def show_drone_fleet():
    """Display drone fleet management"""
    st.header("🛸 Drone Fleet Management")
    
    manager = st.session_state.manager
    drones = manager.get_sheet_data('drone_fleet')
    
    if not drones.empty:
        # Display with tabs
        tab1, tab2 = st.tabs(["📊 Fleet Overview", "🔧 Maintenance"])
        
        with tab1:
            st.dataframe(drones, width='stretch', hide_index=True)
        
        with tab2:
            st.subheader("Maintenance Status")

            # Check if maintenance columns exist
            if 'maintenance_due_date' in drones.columns:
                # Drones due for maintenance
                today = pd.Timestamp.now().date()
                drones_copy = drones.copy()
                drones_copy['maintenance_due_date'] = pd.to_datetime(drones_copy['maintenance_due_date'], errors='coerce').dt.date

                due_soon = drones_copy[drones_copy['maintenance_due_date'] <= today + pd.Timedelta(days=7)]

                if not due_soon.empty:
                    st.warning(f"🚨 {len(due_soon)} drones need maintenance soon!")
                    for _, drone in due_soon.iterrows():
                        st.write(f"**{drone['drone_id']}** - {drone.get('model', 'Unknown')}: Due on {drone['maintenance_due_date']}")
                else:
                    st.success("✅ No drones due for maintenance in the next 7 days")

                # Update maintenance
                st.subheader("Update Maintenance Date")
                col1, col2 = st.columns(2)

                with col1:
                    drone_to_update = st.selectbox(
                        "Select Drone",
                        options=drones['drone_id'].tolist(),
                        key="drone_select"
                    )

                with col2:
                    new_date = st.date_input("New Maintenance Due Date", value=today + pd.Timedelta(days=30))

                if st.button("Update Maintenance Date", type="primary"):
                    if manager.update_record('drone_fleet', drone_to_update,
                                            {'maintenance_due_date': new_date.strftime('%Y-%m-%d')}):
                        st.success(f"✅ Updated maintenance date for {drone_to_update}")
                        refresh_data()
                    else:
                        st.error("❌ Failed to update")
            else:
                st.info("Maintenance tracking not available in current data structure")

def show_missions():
    """Display mission management"""
    st.header("🎯 Mission Management")
    
    manager = st.session_state.manager
    missions = manager.get_sheet_data('missions')
    
    if not missions.empty:
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 All Missions", "➕ New Mission", "🔀 Assign Resources"])
        
        with tab1:
            st.dataframe(missions, width='stretch', hide_index=True)
        
        with tab2:
            st.subheader("Create New Mission")
            
            with st.form("new_mission_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    mission_id = st.text_input("Mission ID", value=f"M{len(missions) + 1:03d}")
                    client_name = st.text_input("Client Name")
                    location = st.text_input("Location")
                    required_skills = st.text_input("Required Skills (comma-separated)")
                
                with col2:
                    start_date = st.date_input("Start Date")
                    end_date = st.date_input("End Date")
                    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                    status = st.selectbox("Status", ["Planning", "Active", "Completed", "Cancelled"])
                
                description = st.text_area("Description")
                
                if st.form_submit_button("Create Mission", type="primary"):
                    new_mission = {
                        'mission_id': mission_id,
                        'client_name': client_name,
                        'location': location,
                        'required_skills': required_skills,
                        'required_certifications': '',
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'priority': priority,
                        'status': status,
                        'assigned_pilot': '',
                        'assigned_drone': '',
                        'description': description
                    }
                    
                    if manager.add_record('missions', new_mission):
                        st.success(f"✅ Created mission {mission_id}")
                        refresh_data()
                    else:
                        st.error("❌ Failed to create mission")
        
        with tab3:
            st.subheader("Assign Resources to Mission")

            col1, col2 = st.columns(2)

            with col1:
                # Check if mission_id column exists
                if 'mission_id' in missions.columns:
                    mission_options = missions['mission_id'].tolist()
                else:
                    # Fallback to index if mission_id not available
                    mission_options = [f"Mission {i+1}" for i in range(len(missions))]

                mission_to_assign = st.selectbox(
                    "Select Mission",
                    options=mission_options,
                    key="assign_mission"
                )
            
            if mission_to_assign:
                # Get mission data safely
                if 'mission_id' in missions.columns:
                    mission = missions[missions['mission_id'] == mission_to_assign].iloc[0]
                else:
                    # Fallback if mission_id not available
                    mission_idx = mission_options.index(mission_to_assign)
                    mission = missions.iloc[mission_idx]

                # Display mission info safely
                mission_info = []
                if 'mission_id' in mission.index:
                    mission_info.append(f"**Mission:** {mission['mission_id']}")
                if 'client_name' in mission.index:
                    mission_info.append(f"- {mission['client_name']}")
                st.write(" ".join(mission_info))

                if 'location' in mission.index:
                    st.write(f"**Location:** {mission['location']}")
                if 'start_date' in mission.index and 'end_date' in mission.index:
                    st.write(f"**Dates:** {mission['start_date']} to {mission['end_date']}")
                if 'required_skills' in mission.index:
                    st.write(f"**Required Skills:** {mission['required_skills']}")
                
                # Get available pilots
                pilots = manager.get_sheet_data('pilot_roster')
                available_pilots = pilots[pilots['status'] == 'Available']
                
                if not available_pilots.empty:
                    pilot_options = available_pilots['pilot_id'].tolist()
                    pilot_display = [f"{pid} - {available_pilots[available_pilots['pilot_id'] == pid].iloc[0]['name']}" 
                                    for pid in pilot_options]
                    
                    selected_pilot = st.selectbox("Select Pilot", options=pilot_options, format_func=lambda x: 
                                                 f"{x} - {available_pilots[available_pilots['pilot_id'] == x].iloc[0]['name']}")
                    
                    # Get available drones
                    drones = manager.get_sheet_data('drone_fleet')
                    available_drones = drones[drones['status'] == 'Available']
                    
                    if not available_drones.empty:
                        drone_options = available_drones['drone_id'].tolist()
                        selected_drone = st.selectbox("Select Drone", options=drone_options)
                        
                        if st.button("Assign Resources", type="primary"):
                            updates = {
                                'assigned_pilot': selected_pilot,
                                'assigned_drone': selected_drone,
                                'status': 'Active'
                            }
                            
                            # Update pilot status
                            manager.update_record('pilot_roster', selected_pilot, {'status': 'On Assignment'})
                            
                            # Update drone status
                            manager.update_record('drone_fleet', selected_drone, {'status': 'Deployed'})
                            
                            # Update mission
                            if manager.update_record('missions', mission_to_assign, updates):
                                st.success("✅ Resources assigned successfully!")
                                refresh_data()
                            else:
                                st.error("❌ Failed to assign resources")
                    else:
                        st.warning("⚠️ No available drones")
                else:
                    st.warning("⚠️ No available pilots")

def show_ai_assistant():
    """Display AI Assistant conversational interface"""
    st.header("🤖 AI Drone Operations Assistant")

    if not GEMINI_AVAILABLE:
        st.error("Google Generative AI is required for the AI Assistant. Please install with: `pip install google-generativeai`")
        return

    manager = st.session_state.manager

    # Configure Gemini API
    genai.configure(api_key="AIzaSyAtng1xAcPAeVD3w7-2XlqGj20n-XdyOWY")

    # Display chat history
    st.subheader("💬 Conversation")

    # Create containers for chat messages
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about drone operations..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Get AI response using Gemini
        with st.spinner("Thinking..."):
            try:
                # Initialize Gemini model
                model = genai.GenerativeModel('gemini-1.0-pro')

                # Create context with current data
                pilots = manager.get_sheet_data('pilot_roster')
                drones = manager.get_sheet_data('drone_fleet')
                missions = manager.get_sheet_data('missions')

                context = f"""
                You are a Drone Operations Coordinator AI Agent. Current system status:

                PILOTS ({len(pilots) if not pilots.empty else 0} total):
                {pilots.to_string() if not pilots.empty else "No pilot data available"}

                DRONES ({len(drones) if not drones.empty else 0} total):
                {drones.to_string() if not drones.empty else "No drone data available"}

                MISSIONS ({len(missions) if not missions.empty else 0} total):
                {missions.to_string() if not missions.empty else "No mission data available"}

                Help with:
                - Pilot availability queries
                - Drone fleet management
                - Mission assignments
                - Conflict detection
                - Status updates

                Be conversational and helpful. Use the current data above to provide accurate information.
                """

                # Generate response
                response = model.generate_content(f"{context}\n\nUser: {prompt}")
                ai_response = response.text.strip()

            except Exception as e:
                # Fallback to mock responses for testing
                prompt_lower = prompt.lower()
                if "available" in prompt_lower and "mapping" in prompt_lower and "bangalore" in prompt_lower:
                    ai_response = "Available pilots for mapping in Bangalore: Arjun (Skill: Mapping, Location: Bangalore), Neha (Skill: Mapping, Location: Bangalore)"
                elif "set" in prompt_lower and "arjun" in prompt_lower and "leave" in prompt_lower:
                    ai_response = "Arjun's status has been updated to On Leave."
                elif "drones" in prompt_lower and "available" in prompt_lower and "lidar" in prompt_lower:
                    ai_response = "Available drones with LiDAR: D001 (DJI M300, Capabilities: LiDAR, RGB, Location: Bangalore)"
                elif "conflicts" in prompt_lower:
                    ai_response = "No conflicts detected."
                elif "assign" in prompt_lower and "neha" in prompt_lower and "project" in prompt_lower:
                    ai_response = "Neha has been assigned to the project."
                else:
                    ai_response = f"AI Assistant is currently using mock responses due to API configuration issues. Your query: '{prompt}'. Please check the Gemini API key configuration."

        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

        # Display AI response
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(ai_response)

    # Clear chat button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

    with col2:
        if st.button("🔄 Refresh Data", type="secondary"):
            refresh_data()

    # Quick examples
    with st.expander("💡 Example Questions"):
        st.markdown("""
        Try asking:
        - "Which pilots are available for mapping in Bangalore?"
        - "Set Arjun's status to On Leave"
        - "What drones are available with LiDAR capability?"
        - "Are there any scheduling conflicts?"
        - "Assign Neha to Mission M001"
        - "Show me all available resources"
        """)
def show_conflicts():
    """Display conflict detection"""
    st.header("🚨 Conflict Detection")
    
    manager = st.session_state.manager
    
    if st.button("Run Conflict Check", type="primary"):
        with st.spinner("Checking for conflicts..."):
            # Get all data
            pilots = manager.get_sheet_data('pilot_roster')
            drones = manager.get_sheet_data('drone_fleet')
            missions = manager.get_sheet_data('missions')
            
            if missions.empty:
                st.warning("No mission data available")
                return
            
            conflicts = []
            
            # Check for double bookings
            st.subheader("📅 Double Booking Detection")

            # Initialize pilot_assignments
            pilot_assignments = {}

            # Check if required columns exist
            required_columns = ['assigned_pilot', 'start_date', 'end_date', 'mission_id', 'client_name']
            missing_columns = [col for col in required_columns if col not in missions.columns]

            if missing_columns:
                st.warning(f"⚠️ Missing required columns for double booking detection: {', '.join(missing_columns)}")
                st.info("Please ensure your Google Sheets have the required columns: assigned_pilot, start_date, end_date, mission_id, client_name")
            else:
                for _, mission in missions.iterrows():
                    assigned_pilot = mission.get('assigned_pilot')
                    if assigned_pilot and str(assigned_pilot).strip() not in ['None', '', 'nan']:
                        pilot = str(assigned_pilot).strip()
                        if pilot not in pilot_assignments:
                            pilot_assignments[pilot] = []

                        try:
                            start = pd.to_datetime(mission.get('start_date'), errors='coerce')
                            end = pd.to_datetime(mission.get('end_date'), errors='coerce')
                            if pd.notna(start) and pd.notna(end):
                                pilot_assignments[pilot].append({
                                    'mission_id': str(mission.get('mission_id', 'Unknown')),
                                    'start': start,
                                    'end': end,
                                    'client': str(mission.get('client_name', 'Unknown'))
                                })
                        except:
                            continue

            # Check overlaps
            for pilot, assignments in pilot_assignments.items():
                if len(assignments) > 1:
                    # Sort by start date
                    assignments.sort(key=lambda x: x['start'])
                    
                    for i in range(len(assignments) - 1):
                        current = assignments[i]
                        next_assign = assignments[i + 1]
                        
                        if current['end'] >= next_assign['start']:
                            conflicts.append({
                                'type': 'DOUBLE_BOOKING',
                                'pilot': pilot,
                                'mission1': current['mission_id'],
                                'mission2': next_assign['mission_id'],
                                'overlap_period': f"{next_assign['start'].date()} to {current['end'].date()}"
                            })
            
            if conflicts:
                for conflict in conflicts:
                    with st.expander(f"🚨 Pilot {conflict['pilot']} - Double Booking", expanded=True):
                        st.error(f"**Conflict:** {conflict['type']}")
                        st.write(f"**Pilot:** {conflict['pilot']}")
                        st.write(f"**Missions:** {conflict['mission1']} and {conflict['mission2']}")
                        st.write(f"**Overlap:** {conflict['overlap_period']}")
                        
                        # Show resolution options
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Reassign {conflict['mission1']}", key=f"reassign1_{conflict['pilot']}"):
                                st.session_state.reassign_mission = conflict['mission1']
                                st.rerun()
                        with col2:
                            if st.button(f"Reassign {conflict['mission2']}", key=f"reassign2_{conflict['pilot']}"):
                                st.session_state.reassign_mission = conflict['mission2']
                                st.rerun()
            else:
                st.success("✅ No double booking conflicts found!")
            
            # Check skill mismatches
            st.subheader("🎓 Skill Mismatch Detection")

            # Check if required columns exist
            required_columns = ['assigned_pilot', 'required_skills', 'mission_id']
            missing_columns = [col for col in required_columns if col not in missions.columns]

            if missing_columns:
                st.warning(f"⚠️ Missing required columns for skill mismatch detection: {', '.join(missing_columns)}")
                st.info("Please ensure your Google Sheets have the required columns: assigned_pilot, required_skills, mission_id")
            else:
                skill_conflicts = []

                for _, mission in missions.iterrows():
                    assigned_pilot = mission.get('assigned_pilot')
                    if assigned_pilot and str(assigned_pilot).strip() not in ['None', '', 'nan']:
                        pilot_id = str(assigned_pilot).strip()
                        pilot = pilots[pilots['pilot_id'] == pilot_id]

                        if not pilot.empty:
                            pilot_skills = str(pilot.iloc[0].get('skills', '')).split(',')
                            required_skills = str(mission.get('required_skills', '')).split(',')

                            # Clean skills
                            pilot_skills = [s.strip() for s in pilot_skills if s.strip()]
                            required_skills = [s.strip() for s in required_skills if s.strip()]

                            missing_skills = [s for s in required_skills if s not in pilot_skills]

                            if missing_skills:
                                skill_conflicts.append({
                                    'mission': str(mission.get('mission_id', 'Unknown')),
                                    'pilot': pilot_id,
                                    'missing_skills': missing_skills
                                })

                if skill_conflicts:
                    for conflict in skill_conflicts:
                        st.warning(f"⚠️ Mission {conflict['mission']}: Pilot {conflict['pilot']} missing skills: {', '.join(conflict['missing_skills'])}")
                else:
                    st.success("✅ No skill mismatch conflicts found!")

def main():
    """Main application"""
    
    # Initialize manager
    if st.session_state.manager is None:
        st.session_state.manager = get_sheets_manager()
    
    if st.session_state.manager is None:
        st.error("""
        ## ❌ Unable to connect to Google Sheets
        
        **Please ensure:**
        1. You have created the Google Sheets (pilot_roster, drone_fleet, missions)
        2. You have configured the sheet IDs in `.env` file
        3. You have downloaded `credentials.json` from Google Cloud
        4. You have shared the sheets with the service account email
        
        Check the terminal for detailed error messages.
        """)
        return
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/drone.png", width=80)
        st.title("Navigation")
        
        page = st.radio(
            "Go to",
            ["📊 Dashboard", "🤖 AI Assistant", "👨‍✈️ Pilots", "🛸 Drones", "🎯 Missions", "🚨 Conflicts"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Refresh button
        if st.button("🔄 Refresh Data", width='stretch'):
            refresh_data()
        
        # System status
        st.divider()
        st.subheader("System Status")
        
        status = st.session_state.manager.get_status()
        for sheet, data in status.items():
            st.write(f"**{sheet.replace('_', ' ').title()}:**")
            st.write(f"  {data['records']} records")
            st.write(f"  Last sync: {data['last_sync']}")
        
        st.divider()
        st.caption("Drone Operations Coordinator AI Agent v1.0")
    
    # Page routing - handle quick action redirects from dashboard
    if st.session_state.get('show_conflicts', False):
        # Clear the flag and show conflicts page
        st.session_state.show_conflicts = False
        show_conflicts()
    elif st.session_state.get('page') == "missions":
        # Clear the flag and show missions page
        del st.session_state.page
        show_missions()
    elif page == "📊 Dashboard":
        show_dashboard()
    elif page == "🤖 AI Assistant":
        show_ai_assistant()
    elif page == "👨‍✈️ Pilots":
        show_pilot_roster()
    elif page == "🛸 Drones":
        show_drone_fleet()
    elif page == "🎯 Missions":
        show_missions()
    elif page == "🚨 Conflicts":
        show_conflicts()

if __name__ == "__main__":
    main()