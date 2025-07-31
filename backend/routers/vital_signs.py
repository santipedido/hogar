from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)

# Definir modelo aquí para evitar errores de importación
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

router = APIRouter()

@router.get("/test")
def test_vital_signs():
    return {"message": "vital signs router is working"}

def prepare_vital_sign_data(data: dict) -> dict:
    """Prepara los datos del signo vital para Supabase"""
    # Convertir fechas a string ISO
    if 'taken_at' in data and data['taken_at']:
        if isinstance(data['taken_at'], datetime):
            data['taken_at'] = data['taken_at'].isoformat()
    if 'created_at' in data and data['created_at']:
        if isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
    if 'updated_at' in data and data['updated_at']:
        if isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
    
    # Remover id si existe para creación
    if 'id' in data:
        del data['id']
    
    # Remover timestamps automáticos
    if 'created_at' in data:
        del data['created_at']
    if 'updated_at' in data:
        del data['updated_at']
    
    # Limpiar campos vacíos (excepto 0 que es un valor válido)
    cleaned_data = {}
    for k, v in data.items():
        if v is not None:
            cleaned_data[k] = v
    
    return cleaned_data

@router.get("/vital-signs/", response_model=List[VitalSign])
async def get_all_vital_signs():
    """Obtener todos los signos vitales"""
    try:
        response = supabase_client.table('vital_signs').select("*").order('taken_at', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting vital signs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vital-signs/resident/{resident_id}", response_model=List[VitalSign])
async def get_vital_signs_by_resident(resident_id: str):
    """Obtener signos vitales por residente"""
    try:
        response = supabase_client.table('vital_signs').select("*").eq('resident_id', resident_id).order('taken_at', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting vital signs for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vital-signs/{vital_sign_id}", response_model=VitalSign)
async def get_vital_sign(vital_sign_id: str):
    """Obtener un signo vital específico"""
    try:
        response = supabase_client.table('vital_signs').select("*").eq('id', vital_sign_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Signo vital no encontrado")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error getting vital sign {vital_sign_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vital-signs/", response_model=VitalSign)
async def create_vital_sign(vital_sign: VitalSign):
    """Crear un nuevo signo vital"""
    try:
        # Preparar datos para Supabase
        data = prepare_vital_sign_data(vital_sign.dict())
        logger.info(f"Creating vital sign with data: {data}")
        
        response = supabase_client.table('vital_signs').insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating vital sign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/vital-signs/{vital_sign_id}", response_model=VitalSign)
async def update_vital_sign(vital_sign_id: str, vital_sign: VitalSign):
    """Actualizar un signo vital existente"""
    try:
        # Preparar datos para Supabase
        data = prepare_vital_sign_data(vital_sign.dict())
        logger.info(f"Updating vital sign {vital_sign_id} with data: {data}")
        
        response = supabase_client.table('vital_signs').update(data).eq('id', vital_sign_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Signo vital no encontrado")
            
        logger.info(f"Update response: {response.data}")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating vital sign {vital_sign_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vital-signs/{vital_sign_id}")
async def delete_vital_sign(vital_sign_id: str):
    """Eliminar un signo vital"""
    try:
        response = supabase_client.table('vital_signs').delete().eq('id', vital_sign_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Signo vital no encontrado")
        return {"message": "Signo vital eliminado"}
    except Exception as e:
        logger.error(f"Error deleting vital sign {vital_sign_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vital-signs/resident/{resident_id}/latest", response_model=List[VitalSign])
async def get_latest_vital_signs_by_resident(resident_id: str, limit: int = 5):
    """Obtener los últimos signos vitales de un residente"""
    try:
        response = supabase_client.table('vital_signs').select("*").eq('resident_id', resident_id).order('taken_at', desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting latest vital signs for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vital-signs/resident/{resident_id}/paginated")
async def get_vital_signs_paginated(resident_id: str, page: int = 1, limit: int = 10):
    """Obtener signos vitales paginados de un residente"""
    try:
        # Calcular offset
        offset = (page - 1) * limit
        
        # Obtener el total de registros
        count_response = supabase_client.table('vital_signs').select("*", count="exact").eq('resident_id', resident_id).execute()
        total_count = count_response.count
        
        # Obtener registros paginados
        response = supabase_client.table('vital_signs').select("*").eq('resident_id', resident_id).order('taken_at', desc=True).range(offset, offset + limit - 1).execute()
        
        # Calcular información de paginación
        total_pages = (total_count + limit - 1) // limit  # ceil division
        
        return {
            "data": response.data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    except Exception as e:
        logger.error(f"Error getting paginated vital signs for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vital-signs/calendar/{resident_id}")
async def get_vital_signs_calendar(resident_id: str, year: int, month: int):
    """Obtener datos del calendario de signos vitales para un mes específico"""
    try:
        # Obtener signos vitales del mes
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
            
        response = supabase_client.table('vital_signs').select("*").eq('resident_id', resident_id).gte('taken_at', start_date).lt('taken_at', end_date).order('taken_at', desc=True).execute()
        vital_signs = response.data
        
        # Procesar datos para el calendario
        calendar_data = {}
        
        # Agrupar signos vitales por fecha
        for record in vital_signs:
            date_key = record['taken_at'][:10]  # YYYY-MM-DD
            if date_key not in calendar_data:
                calendar_data[date_key] = []
            calendar_data[date_key].append(record)
        
        return {
            "vital_signs": vital_signs,
            "calendar_data": calendar_data,
            "month": month,
            "year": year
        }
        
    except Exception as e:
        logger.error(f"Error getting vital signs calendar for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))