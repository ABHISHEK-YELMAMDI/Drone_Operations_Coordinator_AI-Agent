from typing import List, Dict
from models.pilot import Pilot
from models.drone import Drone
from core.roster_management import RosterManager
from core.assignment_tracking import AssignmentTracker
from core.drone_inventory import DroneInventory

class ConflictDetector:
    def __init__(self, roster_manager: RosterManager, assignment_tracker: AssignmentTracker, drone_inventory: DroneInventory):
        self.roster_manager = roster_manager
        self.assignment_tracker = assignment_tracker
        self.drone_inventory = drone_inventory

    def detect_conflicts(self) -> List[Dict]:
        conflicts = []
        pilots = self.roster_manager.sheets_manager.get_pilots()
        drones = self.drone_inventory.sheets_manager.get_drones()

        # Check for pilot double-booking (simplified, assuming no dates in CSV)
        assigned_pilots = [p for p in pilots if p.status == "Assigned"]
        # For now, assume no overlapping dates; in real, check dates

        # Check skill mismatches (if assigned pilot lacks required skills for project)
        # This would require project requirements; placeholder

        # Check drone maintenance
        for drone in drones:
            if drone.status == "Maintenance" and drone.current_assignment:
                conflicts.append({
                    "type": "drone_maintenance",
                    "message": f"Drone {drone.drone_id} is in maintenance but assigned to {drone.current_assignment}"
                })

        # Check location mismatches
        for pilot in assigned_pilots:
            if pilot.current_assignment:
                # Assume project location; placeholder
                pass

        return conflicts

    def suggest_reassignment(self, conflict: Dict) -> Dict:
        # For urgent reassignments: if conflict, suggest alternative pilot/drone
        if conflict["type"] == "drone_maintenance":
            drone_id = conflict["message"].split()[1]
            # Find alternative available drone
            alternatives = self.drone_inventory.get_available_drones()
            if alternatives:
                return {"suggestion": f"Reassign to drone {alternatives[0].drone_id}"}
        return {"suggestion": "No alternative available"}
