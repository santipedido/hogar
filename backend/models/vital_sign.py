from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VitalSignBase(BaseModel):
    resident_id: str
    recorded_at: Optional[datetime]
    blood_pressure: Optional[str]
    temperature: Optional[float]
    pulse: Optional[int]
    recorded_by_user_id: Optional[str]
    notes: Optional[str]

class VitalSignCreate(VitalSignBase):
    pass

class VitalSign(VitalSignBase):
    id: str
    class Config:
        orm_mode = True 