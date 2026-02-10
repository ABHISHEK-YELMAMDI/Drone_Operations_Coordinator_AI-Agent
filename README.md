# Drone Operations Coordinator AI Agent

A comprehensive AI-powered system for managing drone operations, pilot assignments, and fleet coordination with real-time Google Sheets integration.

**Access the deployed application:** [Streamlit Cloud Link](https://droneoperationscoordinatorai-agent-fqztnzjfruhrtt5a75wdla.streamlit.app/)

## Overview

This AI agent automates the complex task of drone operations coordination by handling:
- Pilot roster management and availability tracking
- Drone fleet inventory and maintenance scheduling
- Mission assignment and resource allocation
- Conflict detection and resolution
- Urgent reassignment coordination

## Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  Business Logic │────│ Google Sheets   │
│                 │    │   (Python)      │    │   API            │
│ - Dashboard     │    │                 │    │                 │
│ - Pilot Mgmt    │    │ - RosterManager │    │ - Pilot Roster  │
│ - Drone Mgmt    │    │ - DroneInventory│    │ - Drone Fleet   │
│ - Mission Mgmt  │    │ - AssignmentTracker│ │ - Missions      │
│ - Conflict Det  │    │ - ConflictDetector│  │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

- **Frontend:** Streamlit (Python web framework)
- **Backend:** Python 3.12
- **Data Storage:** Google Sheets (2-way sync)
- **AI/ML:** Google Gemini AI for conversational interface
- **APIs:** Google Sheets API, Google Gemini API
- **Deployment:** Streamlit Cloud

### **Key Features**

#### 1. **Pilot Roster Management**
- View pilot availability by skill, location, status
- Update pilot status with Google Sheets sync
- Filter and search capabilities

#### 2. **Drone Fleet Management**
- Track drone availability and maintenance schedules
- Monitor battery health and flight hours
- Update maintenance due dates

#### 3. **Mission Coordination**
- Create new missions with resource requirements
- Assign pilots and drones to missions
- Track mission progress and status

#### 4. **Conflict Detection**
- Automatic detection of scheduling conflicts
- Skill mismatch identification
- Location conflict alerts
- Urgent reassignment suggestions

#### 5. **Conversational AI**
- Natural language interaction
- Context-aware responses
- Automated action execution

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Google Cloud Project with Sheets API enabled
- OpenAI API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/drone-ops-agent.git
   cd drone-ops-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Sheets**
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create service account credentials
   - Download `credentials.json`
   - Create three Google Sheets: `pilot_roster`, `drone_fleet`, `missions`

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and sheet IDs
   ```

5. **Run the application**
   ```bash
   streamlit run main.py
   ```

## 📊 Data Schema

### Pilot Roster Sheet
| Column | Type | Description |
|--------|------|-------------|
| pilot_id | string | Unique pilot identifier |
| name | string | Pilot full name |
| skills | string | Comma-separated skills |
| certifications | string | Required certifications |
| current_location | string | Current location |
| status | string | Available/On Leave/Unavailable |
| experience_level | string | Junior/Senior/Expert |

### Drone Fleet Sheet
| Column | Type | Description |
|--------|------|-------------|
| drone_id | string | Unique drone identifier |
| model | string | Drone model name |
| capabilities | string | Comma-separated capabilities |
| location | string | Current location |
| status | string | Available/Maintenance/Deployed |
| maintenance_due_date | date | Next maintenance date |
| battery_health | int | Battery health percentage |

### Missions Sheet
| Column | Type | Description |
|--------|------|-------------|
| mission_id | string | Unique mission identifier |
| client_name | string | Client company name |
| location | string | Mission location |
| required_skills | string | Required pilot skills |
| start_date | date | Mission start date |
| end_date | date | Mission end date |
| priority | string | Low/Medium/High/Critical |
| status | string | Planning/Active/Completed |
| assigned_pilot | string | Assigned pilot ID |
| assigned_drone | string | Assigned drone ID |

## 🔧 Configuration

### Environment Variables
```env
# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH=credentials.json
GOOGLE_SHEETS_PILOT_ROSTER_ID=your_sheet_id
GOOGLE_SHEETS_DRONE_FLEET_ID=your_sheet_id
GOOGLE_SHEETS_MISSIONS_ID=your_sheet_id

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
```

### Google Sheets Setup
1. Create three separate Google Sheets
2. Share each sheet with your service account email
3. Add the sheet IDs to your `.env` file

## 🧪 Testing

### Automated Tests
```bash
python -m pytest tests/
```

### Manual Testing Scenarios
- Pilot status updates sync to Google Sheets
- Mission assignment creates conflicts
- Conflict detection identifies overlaps
- Urgent reassignment suggestions work

## 📈 Performance

- **Response Time:** <2 seconds for most operations
- **Concurrent Users:** Supports multiple simultaneous users
- **Data Sync:** Real-time Google Sheets synchronization
- **Error Recovery:** Graceful handling of API failures

## 🔒 Security

- Service account credentials for Google Sheets access
- API key encryption for OpenAI integration
- Input validation and sanitization
- No sensitive data stored locally

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for the Skylark Drones technical assignment
- Uses Streamlit for the web interface
- Powered by OpenAI's GPT models
- Google Sheets for data persistence

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Note:** This is a prototype implementation. For production use, additional security measures and scalability improvements would be recommended.
