from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from typing import Dict, Any

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
        json_encoders = {
            date: lambda v: v.isoformat() if v else None
        }

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        # Excluir campos None por defecto
        kwargs.setdefault("exclude_none", True)
        return super().dict(*args, **kwargs) 