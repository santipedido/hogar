from pydantic import BaseModel
from typing import Optional
from datetime import time, datetime

class MedicationBase(BaseModel):
    resident_id: str
    med_name: str
    dosage: str
    frequency: str
    scheduled_time: Optional[time]
    administered_at: Optional[datetime]
    administered_by_user_id: Optional[str]
    notes: Optional[str]

class MedicationCreate(MedicationBase):
    pass

class Medication(MedicationBase):
    id: str
    class Config:
        orm_mode = True 