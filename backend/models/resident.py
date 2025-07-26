from pydantic import BaseModel
from typing import Optional
from datetime import date

class ResidentBase(BaseModel):
    name: str
    status: str  # 'independent' o 'semidependent'
    photo_url: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    admission_date: date
    discharge_date: Optional[date]

class ResidentCreate(ResidentBase):
    pass

class Resident(ResidentBase):
    id: str
    class Config:
        orm_mode = True 