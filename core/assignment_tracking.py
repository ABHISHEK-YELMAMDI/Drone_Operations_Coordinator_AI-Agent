from typing import List, Optional
from models.pilot import Pilot
from models.drone import Drone
from utils.sheets import SheetsManager

class AssignmentTracker:
    def __init__(self, sheets_manager: SheetsManager):
        self.sheets_manager = sheets_manager

    def match_pilot_to_project(self, project_requirements: dict) -> Optional[Pilot]:
        # Simple matching: find available pilot with required skills and location
        pilots = self.sheets_manager.get_pilots()
        required_skills = project_requirements.get('skills', [])
        required_location = project_requirements.get('location')
        for pilot in pilots:
            if pilot.status == "Available" and all(skill in pilot.skills for skill in required_skills):
                if required_location and pilot.location != required_location:
                    continue
                return pilot
        return None

    def assign_pilot(self, pilot_id: str, project: str):
        # Update pilot status to Assigned and set current_assignment
        self.sheets_manager.update_pilot_status(pilot_id, "Assigned")
        # Note: In real Google Sheets, update the assignment column too, but for CSV, we can extend if needed

    def get_active_assignments(self) -> List[dict]:
        pilots = self.sheets_manager.get_pilots()
        assignments = []
        for p in pilots:
            if p.current_assignment:
                assignments.append({
                    'pilot_id': p.pilot_id,
                    'name': p.name,
                    'assignment': p.current_assignment
                })
        return assignments

    # Similar for drones if needed
