from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)

# Modelo Pydantic para signos vitales
class VitalSignBase(BaseModel):
    resident_id: str
    type: str  # Ej: "presion", "temperatura", "fc", "saturacion", etc.
    value: Optional[float] = None
    unit: Optional[str] = None
    systolic: Optional[float] = None  # Solo para presión arterial
    diastolic: Optional[float] = None # Solo para presión arterial
    taken_at: datetime
    notes: Optional[str] = None
    taken_by: Optional[str] = None  # Nombre o ID del personal

class VitalSignCreate(VitalSignBase):
    pass

class VitalSign(VitalSignBase):
    id: str
    class Config:
        orm_mode = True

router = APIRouter(tags=["vital_signs"])

@router.get("/vital-signs/resident/{resident_id}", response_model=List[VitalSign])
async def get_vital_signs(resident_id: str, type: Optional[str] = None):
    """Obtener todos los signos vitales de un residente (opcionalmente filtrar por tipo)"""
    try:
        query = supabase_client.table('vital_signs').select("*").eq('resident_id', resident_id)
        if type:
            query = query.eq('type', type)
        response = query.order('taken_at', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error obteniendo signos vitales: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vital-signs/{vital_sign_id}", response_model=VitalSign)
async def get_vital_sign(vital_sign_id: str):
    """Obtener un registro de signo vital específico"""
    try:
        response = supabase_client.table('vital_signs').select("*").eq('id', vital_sign_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Signo vital no encontrado")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error obteniendo signo vital: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vital-signs/", response_model=VitalSign)
async def create_vital_sign(vital_sign: VitalSignCreate):
    """Crear un nuevo registro de signo vital"""
    try:
        data = vital_sign.dict()
        response = supabase_client.table('vital_signs').insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creando signo vital: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/vital-signs/{vital_sign_id}", response_model=VitalSign)
async def update_vital_sign(vital_sign_id: str, vital_sign: VitalSignCreate):
    """Editar un registro de signo vital"""
    try:
        data = vital_sign.dict()
        response = supabase_client.table('vital_signs').update(data).eq('id', vital_sign_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Signo vital no encontrado")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error editando signo vital: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vital-signs/{vital_sign_id}")
async def delete_vital_sign(vital_sign_id: str):
    """Eliminar un registro de signo vital"""
    try:
        response = supabase_client.table('vital_signs').delete().eq('id', vital_sign_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Signo vital no encontrado")
        return {"message": "Signo vital eliminado"}
    except Exception as e:
        logger.error(f"Error eliminando signo vital: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 