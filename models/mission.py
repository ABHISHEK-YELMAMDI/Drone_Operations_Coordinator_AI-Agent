from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Mission(BaseModel):
    mission_id: str
    client_name: str
    location: str
    required_skills: List[str]
    required_certifications: List[str]
    start_date: date
    end_date: date
    priority: str
    status: str  # Pending, Assigned, Completed
    assigned_pilot: Optional[str]
    assigned_drone: Optional[str]
    description: str
    special_requirements: Optional[str]
