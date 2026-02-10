# Decision Log: Drone Operations Coordinator AI Agent

## Key Assumptions Made

1. **Data Structure**: Assumed Google Sheets would have standard columns for pilots (pilot_id, name, skills, certifications, location, status) and drones (drone_id, model, capabilities, location, status). Added additional fields like experience_level, availability dates, maintenance info for enhanced functionality.

2. **User Interface**: Chose Streamlit for rapid prototyping and conversational interface, assuming web-based access is acceptable. CLI interface provided as backup.

3. **Google Sheets Integration**: Assumed service account credentials would be available and sheets would be shared appropriately. Implemented graceful error handling for missing credentials.

4. **Urgent Reassignments**: Interpreted as detecting conflicts and suggesting alternative assignments based on availability, skills, and location matching.

## Trade-offs Chosen and Why

1. **Tech Stack**: Streamlit + Python vs. full web framework
   - **Why**: Faster development, built-in UI components, easy deployment. Trade-off: Less customization than React/Vue, but sufficient for prototype.

2. **Data Storage**: Google Sheets vs. Database
   - **Why**: Meets requirement for 2-way sync, easy to set up. Trade-off: Performance limitations for large datasets, but adequate for drone operations scale.

3. **AI Integration**: Rule-based + simple NLP vs. full LangChain agent
   - **Why**: Reliable for structured operations, faster implementation. Trade-off: Less conversational flexibility, but covers all required features.

4. **Error Handling**: Graceful degradation vs. comprehensive validation
   - **Why**: Better user experience, prevents crashes. Trade-off: Some edge cases might not be caught, but core functionality protected.

## What I'd Do Differently With More Time

1. **Full AI Agent**: Implement LangChain with GPT-4 for more natural conversation and complex reasoning.

2. **Database Migration**: Move to PostgreSQL with Google Sheets as backup sync layer for better performance and data integrity.

3. **Advanced Conflict Resolution**: Add machine learning for optimal assignment recommendations and predictive conflict detection.

4. **Real-time Updates**: Implement WebSocket connections for live dashboard updates when sheets change.

5. **Comprehensive Testing**: Add unit tests, integration tests, and end-to-end testing with mock Google Sheets.

6. **Security**: Add authentication, input validation, and secure credential management.

## Interpretation of "Urgent Reassignments"

**Interpretation**: The agent should detect scheduling conflicts and automatically suggest alternative assignments by:
- Identifying conflicts (double-booking, skill mismatches, location issues)
- Finding available alternatives (pilots/drones with matching skills and location)
- Presenting options to user for quick resolution
- Allowing one-click reassignment

**Implementation**: Added conflict detection logic that scans all assignments and flags issues. Dashboard shows conflict alerts with suggested alternatives. CLI and UI both support quick reassignments.

## Architecture Overview

**Frontend**: Streamlit web app with dashboard, pilot/drone/mission management, conflict alerts.

**Backend**: Python modules for business logic (roster, assignment, inventory, conflict detection).

**Data Layer**: Google Sheets integration with 2-way sync (read for queries, write for updates).

**AI Layer**: Rule-based decision making with simple NLP for user queries.

**Deployment**: Streamlit Cloud for hosting, with local CLI fallback.
