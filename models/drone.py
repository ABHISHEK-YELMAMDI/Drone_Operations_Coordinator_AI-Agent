from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Drone(BaseModel):
    drone_id: str
    model: str
    capabilities: List[str]
    max_range: int
    weight_capacity: float
    current_assignment: Optional[str]
    status: str  # Available, Maintenance, Assigned
    location: str
    maintenance_due_date: Optional[date]
    last_maintenance: Optional[date]
    flight_hours: int
    battery_health: int
