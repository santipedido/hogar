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
    
    # Nuevos campos de información médica
    document_number: Optional[str] = Field(None, description="Número de cédula")
    birth_date: Optional[date] = Field(None, description="Fecha de nacimiento")
    pathologies: Optional[List[str]] = Field(default=[], description="Lista de patologías")
    medical_history: Optional[str] = Field(None, description="Historial clínico básico")
    allergies: Optional[List[str]] = Field(default=[], description="Lista de alergias")
    blood_type: Optional[str] = Field(None, description="Grupo sanguíneo")

    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True 