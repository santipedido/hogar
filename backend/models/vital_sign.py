from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VitalSign(BaseModel):
    id: Optional[str] = None
    resident_id: str
    type: str = Field(..., description="Tipo de signo vital: Temperatura, Frecuencia Cardíaca, etc.")
    value: Optional[float] = None
    unit: Optional[str] = None
    systolic: Optional[float] = None
    diastolic: Optional[float] = None
    taken_at: datetime
    notes: Optional[str] = None
    taken_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True