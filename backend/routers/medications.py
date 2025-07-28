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
        
        # Guardar en historial (siempre se guarda)
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

@router.get("/medications/today-status/{resident_id}")
async def get_today_medication_status(resident_id: str):
    """Obtener el estado de administración de medicamentos para hoy"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Obtener todas las medicaciones del residente
        medications_response = supabase_client.table('medications').select("*").eq('resident_id', resident_id).execute()
        medications = medications_response.data
        
        # Obtener administraciones de hoy
        history_response = supabase_client.table('medication_history').select("*").eq('resident_id', resident_id).gte('administered_at', f"{today}T00:00:00").lt('administered_at', f"{today}T23:59:59").execute()
        today_history = history_response.data
        
        # Procesar estado de cada medicación
        medication_status = []
        
        for medication in medications:
            # Contar cuántas veces se administró hoy
            today_count = len([h for h in today_history if h['medication_id'] == medication['id']])
            
            # Determinar cuántas veces debería administrarse según la frecuencia
            expected_count = get_expected_admin_count(medication['frequency'])
            
            medication_status.append({
                **medication,
                'administered_today': today_count,
                'expected_today': expected_count,
                'can_administer': today_count < expected_count,
                'last_administered': get_last_administered(today_history, medication['id'])
            })
        
        return {
            "date": today,
            "medications": medication_status
        }
        
    except Exception as e:
        logger.error(f"Error getting today's medication status for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_expected_admin_count(frequency: str) -> int:
    """Determinar cuántas veces se debe administrar según la frecuencia"""
    frequency_lower = frequency.lower()
    if 'una vez' in frequency_lower:
        return 1
    elif 'dos veces' in frequency_lower:
        return 2
    elif 'tres veces' in frequency_lower:
        return 3
    elif 'cada 8 horas' in frequency_lower:
        return 3  # 24/8 = 3 veces al día
    elif 'cada 12 horas' in frequency_lower:
        return 2  # 24/12 = 2 veces al día
    elif 'según necesidad' in frequency_lower:
        return 5  # Máximo 5 veces por día para "según necesidad"
    else:
        return 1  # Por defecto

def get_last_administered(history: list, medication_id: str) -> str:
    """Obtener la última hora de administración de hoy"""
    medication_history = [h for h in history if h['medication_id'] == medication_id]
    if medication_history:
        # Ordenar por hora y tomar la más reciente
        medication_history.sort(key=lambda x: x['administered_at'], reverse=True)
        return medication_history[0]['administered_at']
    return None 