from typing import List, Optional
from models.pilot import Pilot
from utils.sheets import SheetsManager

class RosterManager:
    def __init__(self, sheets_manager: SheetsManager):
        self.sheets_manager = sheets_manager

    def get_available_pilots(self, skill: Optional[str] = None, location: Optional[str] = None) -> List[Pilot]:
        pilots = self.sheets_manager.get_pilots()
        available = [p for p in pilots if p.status == "Available"]
        if skill:
            available = [p for p in available if skill in p.skills]
        if location:
            available = [p for p in available if p.location == location]
        return available

    def update_pilot_status(self, pilot_id: str, new_status: str):
        self.sheets_manager.update_pilot_status(pilot_id, new_status)

    def get_pilot_by_id(self, pilot_id: str) -> Optional[Pilot]:
        pilots = self.sheets_manager.get_pilots()
        for p in pilots:
            if p.pilot_id == pilot_id:
                return p
        return None
