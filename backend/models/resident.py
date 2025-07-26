from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class Resident(BaseModel):
    id: Optional[str] = None
    name: str
    status: str = Field(..., description="'independent' o 'semidependent'")
    photo_url: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    admission_date: date
    discharge_date: Optional[date] = None

    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True 