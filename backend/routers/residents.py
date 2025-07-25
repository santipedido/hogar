from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from supabase_client import supabase
import traceback

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

router = APIRouter(prefix="/residents", tags=["residents"])

@router.get("/", response_model=List[Resident])
def get_residents():
    res = supabase.table("residents").select("*").execute()
    return res.data

@router.get("/{resident_id}", response_model=Resident)
def get_resident(resident_id: str):
    res = supabase.table("residents").select("*").eq("id", resident_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    return res.data

@router.post("/", response_model=Resident)
def create_resident(resident: ResidentCreate):
    data = {k: (v if v != "" else None) for k, v in resident.dict().items()}
    # Convertir objetos date a string
    for k, v in data.items():
        if isinstance(v, date):
            data[k] = v.isoformat()
    try:
        res = supabase.table("residents").insert(data).execute()
        return res.data[0]
    except Exception as e:
        print("[ERROR] Al agregar residente:", e)
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{resident_id}", response_model=Resident)
def update_resident(resident_id: str, resident: ResidentCreate):
    data = {k: (v if v != "" else None) for k, v in resident.dict().items()}
    # Convertir objetos date a string
    for k, v in data.items():
        if isinstance(v, date):
            data[k] = v.isoformat()
    res = supabase.table("residents").update(data).eq("id", resident_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    return res.data[0]

@router.delete("/{resident_id}")
def delete_resident(resident_id: str):
    res = supabase.table("residents").delete().eq("id", resident_id).execute()
    if res.count == 0:
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    return {"ok": True} 