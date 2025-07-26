from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DailyActivityBase(BaseModel):
    resident_id: str
    activity_type: str
    description: Optional[str]
    performed_at: Optional[datetime]
    performed_by_user_id: Optional[str]

class DailyActivityCreate(DailyActivityBase):
    pass

class DailyActivity(DailyActivityBase):
    id: str
    class Config:
        orm_mode = True 