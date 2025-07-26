from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.resident import Resident
from supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/residents/", response_model=List[Resident])
async def get_residents():
    try:
        response = supabase_client.table('residents').select("*").execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting residents: {str(e)}")
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
        data = resident.dict(exclude_unset=True)
        if 'id' in data:
            del data['id']  # Remove id if present for creation
        
        logger.info(f"Creating resident with data: {data}")
        response = supabase_client.table('residents').insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating resident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/residents/{resident_id}", response_model=Resident)
async def update_resident(resident_id: str, resident: Resident):
    try:
        # Get only the fields that are set
        data = resident.dict(exclude_unset=True)
        
        # Remove id from update data if present
        if 'id' in data:
            del data['id']
        
        logger.info(f"Updating resident {resident_id} with data: {data}")
        
        response = supabase_client.table('residents').update(data).eq('id', resident_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
            
        logger.info(f"Update response: {response.data}")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating resident {resident_id}: {str(e)}")
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