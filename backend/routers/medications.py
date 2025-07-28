from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, time, date
from pydantic import BaseModel
from supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)

# Definir modelos aquí para evitar errores de importación
class MedicationBase(BaseModel):
    resident_id: str
    med_name: str
    dosage: str
    frequency: str
    scheduled_time: Optional[time] = None
    notes: Optional[str] = None

class MedicationCreate(MedicationBase):
    pass

class Medication(MedicationBase):
    id: str
    administered_at: Optional[datetime] = None
    administered_by_user_id: Optional[str] = None
    class Config:
        orm_mode = True

class MedicationHistory(BaseModel):
    id: str
    medication_id: str
    resident_id: str
    med_name: str
    dosage: str
    administered_at: datetime
    administered_by_user_id: str
    notes: Optional[str] = None
    class Config:
        orm_mode = True

router = APIRouter()

@router.get("/medications/resident/{resident_id}", response_model=List[Medication])
async def get_resident_medications(resident_id: str):
    """Obtener todas las medicaciones de un residente"""
    try:
        response = supabase_client.table('medications').select("*").eq('resident_id', resident_id).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting medications for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medications/{medication_id}", response_model=Medication)
async def get_medication(medication_id: str):
    """Obtener una medicación específica"""
    try:
        response = supabase_client.table('medications').select("*").eq('id', medication_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Medicación no encontrada")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error getting medication {medication_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/medications/", response_model=Medication)
async def create_medication(medication: MedicationCreate):
    """Crear una nueva medicación"""
    try:
        data = medication.dict()
        
        # Convertir time a string si existe
        if data.get('scheduled_time'):
            if isinstance(data['scheduled_time'], time):
                data['scheduled_time'] = data['scheduled_time'].strftime('%H:%M:%S')

        logger.info(f"Creating medication: {data}")
        response = supabase_client.table('medications').insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating medication: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/medications/{medication_id}", response_model=Medication)
async def update_medication(medication_id: str, medication: MedicationCreate):
    """Actualizar una medicación"""
    try:
        data = medication.dict()
        
        # Convertir time a string si existe
        if data.get('scheduled_time'):
            if isinstance(data['scheduled_time'], time):
                data['scheduled_time'] = data['scheduled_time'].strftime('%H:%M:%S')

        logger.info(f"Updating medication {medication_id}: {data}")
        response = supabase_client.table('medications').update(data).eq('id', medication_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Medicación no encontrada")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating medication {medication_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/medications/{medication_id}")
async def delete_medication(medication_id: str):
    """Eliminar una medicación"""
    try:
        response = supabase_client.table('medications').delete().eq('id', medication_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Medicación no encontrada")
        return {"message": "Medicación eliminada"}
    except Exception as e:
        logger.error(f"Error deleting medication {medication_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/medications/{medication_id}/administer")
async def administer_medication(medication_id: str, user_id: str):
    """Marcar una medicación como administrada y guardar en historial"""
    try:
        # Obtener información de la medicación
        medication_response = supabase_client.table('medications').select("*").eq('id', medication_id).execute()
        if not medication_response.data:
            raise HTTPException(status_code=404, detail="Medicación no encontrada")
        
        medication = medication_response.data[0]
        now = datetime.now()
        
        # Actualizar la medicación
        update_data = {
            'administered_at': now.isoformat(),
            'administered_by_user_id': user_id
        }
        
        supabase_client.table('medications').update(update_data).eq('id', medication_id).execute()
        
        # Guardar en historial
        history_data = {
            'medication_id': medication_id,
            'resident_id': medication['resident_id'],
            'med_name': medication['med_name'],
            'dosage': medication['dosage'],
            'administered_at': now.isoformat(),
            'administered_by_user_id': user_id,
            'notes': medication.get('notes')
        }
        
        supabase_client.table('medication_history').insert(history_data).execute()
        
        logger.info(f"Medication {medication_id} administered by user {user_id}")
        return {"message": "Medicación administrada y registrada en historial"}
        
    except Exception as e:
        logger.error(f"Error administering medication {medication_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medications/history/resident/{resident_id}", response_model=List[MedicationHistory])
async def get_medication_history(resident_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Obtener historial de administración de medicamentos de un residente"""
    try:
        query = supabase_client.table('medication_history').select("*").eq('resident_id', resident_id)
        
        if start_date:
            query = query.gte('administered_at', start_date)
        if end_date:
            query = query.lte('administered_at', end_date)
            
        response = query.order('administered_at', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting medication history for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medications/history/calendar/{resident_id}")
async def get_medication_calendar(resident_id: str, year: int, month: int):
    """Obtener datos del calendario de administración para un mes específico"""
    try:
        # Obtener todas las medicaciones del residente
        medications_response = supabase_client.table('medications').select("*").eq('resident_id', resident_id).execute()
        medications = medications_response.data
        
        # Obtener historial del mes
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
            
        history_response = supabase_client.table('medication_history').select("*").eq('resident_id', resident_id).gte('administered_at', start_date).lt('administered_at', end_date).execute()
        history = history_response.data
        
        # Procesar datos para el calendario
        calendar_data = {}
        
        # Agrupar administraciones por fecha
        for record in history:
            date_key = record['administered_at'][:10]  # YYYY-MM-DD
            if date_key not in calendar_data:
                calendar_data[date_key] = []
            calendar_data[date_key].append(record)
        
        return {
            "medications": medications,
            "history": calendar_data,
            "month": month,
            "year": year
        }
        
    except Exception as e:
        logger.error(f"Error getting medication calendar for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 