from typing import List, Optional
from models.drone import Drone
from utils.sheets import SheetsManager

class DroneInventory:
    def __init__(self, sheets_manager: SheetsManager):
        self.sheets_manager = sheets_manager

    def get_available_drones(self, capability: Optional[str] = None, location: Optional[str] = None) -> List[Drone]:
        drones = self.sheets_manager.get_drones()
        available = [d for d in drones if d.status == "Available"]
        if capability:
            available = [d for d in available if capability in d.capabilities]
        if location:
            available = [d for d in available if d.location == location]
        return available

    def get_drone_by_id(self, drone_id: str) -> Optional[Drone]:
        drones = self.sheets_manager.get_drones()
        for d in drones:
            if d.drone_id == drone_id:
                return d
        return None

    def update_drone_status(self, drone_id: str, new_status: str):
        # For CSV, update the dataframe
        self.sheets_manager.drone_df.loc[self.sheets_manager.drone_df['drone_id'] == drone_id, 'status'] = new_status
        self.sheets_manager.drone_df.to_csv(self.sheets_manager.drone_csv_path, index=False)
