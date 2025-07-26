from pydantic import BaseModel

class StaffBase(BaseModel):
    user_id: str
    name: str
    role: str

class StaffCreate(StaffBase):
    pass

class Staff(StaffBase):
    id: str
    class Config:
        orm_mode = True 