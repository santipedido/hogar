from pydantic import BaseModel, Field
from typing import Optional, List
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
    
    # Nuevos campos de información médica - simplificados temporalmente
    document_number: Optional[str] = None
    birth_date: Optional[date] = None
    pathologies: Optional[List[str]] = None
    medical_history: Optional[str] = None
    allergies: Optional[List[str]] = None
    blood_type: Optional[str] = None

    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True 