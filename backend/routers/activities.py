from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging
from supabase_client import supabase_client

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

from typing import List, Dict, Any

class Participant(BaseModel):
    type: str = Field(..., description="Tipo de participante: resident, staff, family")
    id: Optional[str] = Field(None, description="ID del residente (solo para type=resident)")
    name: str = Field(..., description="Nombre del participante")

class Activity(BaseModel):
    id: Optional[str] = None
    resident_id: str
    type: str = Field(..., description="Tipo de actividad: Físicas, Recreativas, Sociales, Terapéuticas")
    subtype: str = Field(..., description="Subcategoría específica de la actividad")
    title: str = Field(..., description="Título de la actividad")
    description: Optional[str] = None
    scheduled_at: datetime
    completed_at: Optional[datetime] = None
    participants: str = Field(..., description="Participantes: Residente solo, Con otros residentes, Con personal, Con familiares, Grupo mixto")
    participants_data: Optional[List[Dict[str, Any]]] = Field(default=[], description="Datos detallados de participantes")
    notes: Optional[str] = None
    registered_by: Optional[str] = None
    status: str = Field(default="scheduled", description="Estado: scheduled, completed, cancelled")
    is_recurring: bool = Field(default=False, description="Si es actividad semanal")
    recurrence_day: Optional[str] = Field(None, description="Día de la semana para actividades recurrentes")
    parent_activity_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True

@router.get("/test")
def test_activities():
    """Endpoint de prueba para verificar que el router funciona"""
    return {"message": "Activities router is working"}

def prepare_activity_data(data: dict) -> dict:
    """Preparar datos de actividad para Supabase"""
    # Remover campos que no deben enviarse a Supabase
    data.pop('id', None)
    data.pop('created_at', None)
    data.pop('updated_at', None)
    
    # Convertir datetime a string ISO si es necesario
    if 'scheduled_at' in data and isinstance(data['scheduled_at'], datetime):
        data['scheduled_at'] = data['scheduled_at'].isoformat()
    
    if 'completed_at' in data and data['completed_at'] and isinstance(data['completed_at'], datetime):
        data['completed_at'] = data['completed_at'].isoformat()
    
    return data

@router.get("/activities/", response_model=List[Activity])
async def get_all_activities():
    """Obtener todas las actividades"""
    try:
        response = supabase_client.table('activities').select("*").order('scheduled_at', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting all activities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/resident/{resident_id}", response_model=List[Activity])
async def get_activities_by_resident(resident_id: str):
    """Obtener actividades de un residente específico"""
    try:
        response = supabase_client.table('activities').select("*").eq('resident_id', resident_id).order('scheduled_at', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting activities for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/{activity_id}", response_model=Activity)
async def get_activity(activity_id: str):
    """Obtener una actividad específica"""
    try:
        response = supabase_client.table('activities').select("*").eq('id', activity_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error getting activity {activity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activities/", response_model=Activity)
async def create_activity(activity: Activity):
    """Crear una nueva actividad"""
    try:
        data = prepare_activity_data(activity.dict())
        logger.info(f"Creating activity with data: {data}")
        
        # Validar que los campos obligatorios estén presentes
        required_fields = ['resident_id', 'type', 'subtype', 'title', 'scheduled_at', 'participants']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=422, 
                detail=f"Campos obligatorios faltantes: {', '.join(missing_fields)}"
            )
        
        response = supabase_client.table('activities').insert(data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="No se pudo crear la actividad")
            
        logger.info(f"Create response: {response.data}")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/activities/{activity_id}", response_model=Activity)
async def update_activity(activity_id: str, activity: Activity):
    """Actualizar una actividad existente"""
    try:
        data = prepare_activity_data(activity.dict())
        logger.info(f"Updating activity {activity_id} with data: {data}")
        
        response = supabase_client.table('activities').update(data).eq('id', activity_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
            
        logger.info(f"Update response: {response.data}")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating activity {activity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/activities/{activity_id}")
async def delete_activity(activity_id: str):
    """Eliminar una actividad"""
    try:
        response = supabase_client.table('activities').delete().eq('id', activity_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        return {"message": "Actividad eliminada"}
    except Exception as e:
        logger.error(f"Error deleting activity {activity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/resident/{resident_id}/paginated")
async def get_activities_paginated(resident_id: str, page: int = 1, limit: int = 10):
    """Obtener actividades paginadas de un residente"""
    try:
        # Calcular offset
        offset = (page - 1) * limit
        
        # Obtener el total de registros
        count_response = supabase_client.table('activities').select("*", count="exact").eq('resident_id', resident_id).execute()
        total_count = count_response.count
        
        # Obtener registros paginados
        response = supabase_client.table('activities').select("*").eq('resident_id', resident_id).order('scheduled_at', desc=True).range(offset, offset + limit - 1).execute()
        
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
        logger.error(f"Error getting paginated activities for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/calendar/{resident_id}")
async def get_activities_calendar(resident_id: str, year: int, month: int):
    """Obtener datos del calendario de actividades para un mes específico"""
    try:
        # Obtener actividades del mes
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
            
        response = supabase_client.table('activities').select("*").eq('resident_id', resident_id).gte('scheduled_at', start_date).lt('scheduled_at', end_date).order('scheduled_at', desc=True).execute()
        activities = response.data
        
        # Procesar datos para el calendario
        calendar_data = {}
        
        # Agrupar actividades por fecha
        for record in activities:
            date_key = record['scheduled_at'][:10]  # YYYY-MM-DD
            if date_key not in calendar_data:
                calendar_data[date_key] = []
            calendar_data[date_key].append(record)
        
        return {
            "activities": activities,
            "calendar_data": calendar_data,
            "month": month,
            "year": year
        }
        
    except Exception as e:
        logger.error(f"Error getting activities calendar for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/resident/{resident_id}/recurring")
async def get_recurring_activities(resident_id: str):
    """Obtener actividades recurrentes de un residente"""
    try:
        response = supabase_client.table('activities').select("*").eq('resident_id', resident_id).eq('is_recurring', True).order('scheduled_at', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting recurring activities for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))