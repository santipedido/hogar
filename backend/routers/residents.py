from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.resident import Resident
from supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
def health_check():
    """Endpoint de salud para verificar que el router funciona"""
    return {"status": "healthy", "router": "residents", "message": "Residents router is working"}

@router.get("/test")
def test_residents():
    """Endpoint de prueba para verificar que el router funciona"""
    return {"message": "Residents router is working"}

@router.get("/residents-test")
def test_residents_specific():
    """Endpoint de prueba específico para residents"""
    return {"message": "Residents router is working", "router": "residents"}

def prepare_resident_data(data: dict) -> dict:
    """Prepara los datos del residente para Supabase"""
    # Convertir fechas a string ISO
    if 'admission_date' in data and data['admission_date']:
        data['admission_date'] = data['admission_date'].isoformat()
    if 'discharge_date' in data and data['discharge_date']:
        data['discharge_date'] = data['discharge_date'].isoformat()
    if 'birth_date' in data and data['birth_date']:
        data['birth_date'] = data['birth_date'].isoformat()
    
    # Remover id si existe
    if 'id' in data:
        del data['id']
    
    # Limpiar campos vacíos y arrays vacíos
    cleaned_data = {}
    for key, value in data.items():
        if value is not None and value != '':
            # Para arrays, solo incluir si no están vacíos
            if isinstance(value, list):
                if value:  # Si el array no está vacío
                    cleaned_data[key] = value
            else:
                cleaned_data[key] = value
    
    return cleaned_data

@router.get("/residents/", response_model=List[Resident])
async def get_residents():
    try:
        response = supabase_client.table('residents').select("*").execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting residents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/residents/{resident_id}/medical-info")
async def get_resident_medical_info(resident_id: str):
    """Obtener información médica específica de un residente"""
    try:
        logger.info(f"Fetching medical info for resident: {resident_id}")
        response = supabase_client.table('residents').select(
            "id, name, document_number, birth_date, pathologies, medical_history, allergies, blood_type"
        ).eq('id', resident_id).execute()
        
        if not response.data:
            logger.warning(f"Resident not found: {resident_id}")
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        
        resident_data = response.data[0]
        logger.info(f"Found resident data: {resident_data}")
        
        # Calcular edad si hay fecha de nacimiento
        age = None
        if resident_data.get('birth_date'):
            from datetime import date
            birth_date = date.fromisoformat(resident_data['birth_date'])
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        result = {
            **resident_data,
            "age": age
        }
        logger.info(f"Returning medical info: {result}")
        return result
    except Exception as e:
        logger.error(f"Error getting medical info for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/residents/{resident_id}", response_model=Resident)
async def get_resident(resident_id: str):
    try:
        response = supabase_client.table('residents').select("*").eq('id', resident_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error getting resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/residents/", response_model=Resident)
async def create_resident(resident: Resident):
    try:
        # Preparar datos para Supabase
        data = prepare_resident_data(resident.dict())
        logger.info(f"Creating resident with data: {data}")
        
        response = supabase_client.table('residents').insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating resident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/residents/{resident_id}", response_model=Resident)
async def update_resident(resident_id: str, resident: Resident):
    try:
        # Preparar datos para Supabase
        data = prepare_resident_data(resident.dict())
        logger.info(f"Updating resident {resident_id} with data: {data}")
        
        response = supabase_client.table('residents').update(data).eq('id', resident_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
            
        logger.info(f"Update response: {response.data}")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/residents/{resident_id}/medical-info")
async def update_resident_medical_info(resident_id: str, medical_data: dict):
    """Actualizar información médica específica de un residente"""
    try:
        # Validar que el residente existe
        existing_response = supabase_client.table('residents').select("id").eq('id', resident_id).execute()
        if not existing_response.data:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        
        # Preparar datos médicos
        allowed_fields = ['document_number', 'birth_date', 'pathologies', 'medical_history', 'allergies', 'blood_type']
        medical_update = {k: v for k, v in medical_data.items() if k in allowed_fields}
        
        # Convertir fechas
        if 'birth_date' in medical_update and medical_update['birth_date']:
            if isinstance(medical_update['birth_date'], str):
                medical_update['birth_date'] = medical_update['birth_date']
        
        logger.info(f"Updating medical info for resident {resident_id}: {medical_update}")
        
        response = supabase_client.table('residents').update(medical_update).eq('id', resident_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
            
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating medical info for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/residents/{resident_id}")
async def delete_resident(resident_id: str):
    try:
        response = supabase_client.table('residents').delete().eq('id', resident_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        return {"message": "Residente eliminado"}
    except Exception as e:
        logger.error(f"Error deleting resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 