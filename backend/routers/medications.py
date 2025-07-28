from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, time
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
    """Marcar una medicación como administrada"""
    try:
        data = {
            'administered_at': datetime.now().isoformat(),
            'administered_by_user_id': user_id
        }
        
        logger.info(f"Administering medication {medication_id} by user {user_id}")
        response = supabase_client.table('medications').update(data).eq('id', medication_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Medicación no encontrada")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error administering medication {medication_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 