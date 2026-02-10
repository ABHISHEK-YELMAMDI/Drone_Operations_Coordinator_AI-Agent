from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, date
import pandas as pd

@dataclass
class Pilot:
    """Represents a drone pilot"""
    pilot_id: str
    name: str
    skills: List[str]
    certifications: List[str]
    experience_years: int
    current_location: str
    current_assignment: Optional[str]
    status: str  # Available, On Leave, Unavailable, On Assignment
    availability_start: date
    availability_end: date
    contact_email: str

    @classmethod
    def from_series(cls, series):
        """Create Pilot from pandas Series"""
        return cls(
            pilot_id=series.get('pilot_id', ''),
            name=series.get('name', ''),
            skills=[s.strip() for s in str(series.get('skills', '')).split(',')],
            certifications=[c.strip() for c in str(series.get('certifications', '')).split(',')],
            experience_years=int(series.get('experience_years', 0)),
            current_location=series.get('current_location', ''),
            current_assignment=series.get('current_assignment', None),
            status=series.get('status', 'Unknown'),
            availability_start=pd.to_datetime(series.get('availability_start', date.today())).date(),
            availability_end=pd.to_datetime(series.get('availability_end', date.today())).date(),
            contact_email=series.get('contact_email', '')
        )

    def is_available_for(self, start_date: date, end_date: date) -> bool:
        """Check if pilot is available for given dates"""
        if self.status != "Available":
            return False
        return self.availability_start <= start_date and self.availability_end >= end_date

    def has_skills(self, required_skills: List[str]) -> bool:
        """Check if pilot has all required skills"""
        return all(skill in self.skills for skill in required_skills)

    def has_certifications(self, required_certs: List[str]) -> bool:
        """Check if pilot has all required certifications"""
        return all(cert in self.certifications for cert in required_certs)

@dataclass
class Drone:
    """Represents a drone"""
    drone_id: str
    model: str
    capabilities: List[str]
    max_range_km: float
    payload_capacity_kg: float
    current_assignment: Optional[str]
    status: str  # Available, Deployed, Maintenance, Inactive
    location: str
    maintenance_due_date: date
    last_maintenance: date
    flight_hours: int

    @classmethod
    def from_series(cls, series):
        """Create Drone from pandas Series"""
        return cls(
            drone_id=series.get('drone_id', ''),
            model=series.get('model', ''),
            capabilities=[c.strip() for c in str(series.get('capabilities', '')).split(',')],
            max_range_km=float(series.get('max_range_km', 0)),
            payload_capacity_kg=float(series.get('payload_capacity_kg', 0)),
            current_assignment=series.get('current_assignment', None),
            status=series.get('status', 'Unknown'),
            location=series.get('location', ''),
            maintenance_due_date=pd.to_datetime(series.get('maintenance_due_date', date.today())).date(),
            last_maintenance=pd.to_datetime(series.get('last_maintenance', date.today())).date(),
            flight_hours=int(series.get('flight_hours', 0))
        )

    def is_available_for(self, mission_date: date) -> bool:
        """Check if drone is available for mission date"""
        if self.status != "Available":
            return False
        return self.maintenance_due_date > mission_date

    def has_capabilities(self, required_caps: List[str]) -> bool:
        """Check if drone has all required capabilities"""
        return all(cap in self.capabilities for cap in required_caps)

@dataclass
class Mission:
    """Represents a mission/project"""
    mission_id: str
    client_name: str
    location: str
    required_skills: List[str]
    required_certifications: List[str]
    start_date: date
    end_date: date
    priority: str  # Critical, High, Medium, Low
    status: str  # Planning, Active, Completed, Cancelled
    assigned_pilot: Optional[str]
    assigned_drone: Optional[str]
    description: str

    @classmethod
    def from_series(cls, series):
        """Create Mission from pandas Series"""
        return cls(
            mission_id=series.get('mission_id', ''),
            client_name=series.get('client_name', ''),
            location=series.get('location', ''),
            required_skills=[s.strip() for s in str(series.get('required_skills', '')).split(',')],
            required_certifications=[c.strip() for c in str(series.get('required_certifications', '')).split(',')],
            start_date=pd.to_datetime(series.get('start_date', date.today())).date(),
            end_date=pd.to_datetime(series.get('end_date', date.today())).date(),
            priority=series.get('priority', 'Medium'),
            status=series.get('status', 'Planning'),
            assigned_pilot=series.get('assigned_pilot', None),
            assigned_drone=series.get('assigned_drone', None),
            description=series.get('description', '')
        )
