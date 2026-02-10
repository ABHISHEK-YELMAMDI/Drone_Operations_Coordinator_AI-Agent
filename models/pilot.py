from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Pilot(BaseModel):
    pilot_id: str
    name: str
    skills: List[str]
    certifications: List[str]
    experience_level: str
    current_location: str
    current_assignment: Optional[str]
    status: str  # Available, Assigned, On Leave, Unavailable
    availability_start: Optional[date]
    availability_end: Optional[date]
    contact_info: Optional[str]
    last_updated: Optional[date]
