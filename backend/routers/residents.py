from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from models.resident import Resident
from supabase_client import supabase_client

router = APIRouter()

@router.get("/residents/", response_model=List[Resident])
async def get_residents():
    try:
        response = supabase_client.table('residents').select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/residents/{resident_id}", response_model=Resident)
async def get_resident(resident_id: str):
    try:
        response = supabase_client.table('residents').select("*").eq('id', resident_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/residents/", response_model=Resident)
async def create_resident(resident: Resident):
    try:
        response = supabase_client.table('residents').insert(resident.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/residents/{resident_id}", response_model=Resident)
async def update_resident(resident_id: str, resident: Resident):
    try:
        response = supabase_client.table('residents').update(resident.dict()).eq('id', resident_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/residents/{resident_id}")
async def delete_resident(resident_id: str):
    try:
        response = supabase_client.table('residents').delete().eq('id', resident_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        return {"message": "Residente eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 