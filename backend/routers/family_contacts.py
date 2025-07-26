from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)

class FamilyContact(BaseModel):
    id: Optional[str] = None
    resident_id: str
    name: str
    relationship: str
    phone: Optional[str] = None
    is_primary: bool = False
    address: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True

router = APIRouter()

@router.get("/family-contacts/resident/{resident_id}", response_model=List[FamilyContact])
async def get_resident_contacts(resident_id: str):
    """Obtener todos los contactos familiares de un residente"""
    try:
        response = supabase_client.table('family_contacts').select("*").eq('resident_id', resident_id).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting family contacts for resident {resident_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/family-contacts/{contact_id}", response_model=FamilyContact)
async def get_contact(contact_id: str):
    """Obtener un contacto familiar específico"""
    try:
        response = supabase_client.table('family_contacts').select("*").eq('id', contact_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Contacto familiar no encontrado")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error getting family contact {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/family-contacts/", response_model=FamilyContact)
async def create_contact(contact: FamilyContact):
    """Crear un nuevo contacto familiar"""
    try:
        # Si es contacto primario, desmarcar otros contactos primarios del mismo residente
        if contact.is_primary:
            supabase_client.table('family_contacts')\
                .update({'is_primary': False})\
                .eq('resident_id', contact.resident_id)\
                .execute()

        data = contact.dict(exclude_unset=True)
        if 'id' in data:
            del data['id']
        if 'created_at' in data:
            del data['created_at']
        if 'updated_at' in data:
            del data['updated_at']

        logger.info(f"Creating family contact: {data}")
        response = supabase_client.table('family_contacts').insert(data).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating family contact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/family-contacts/{contact_id}", response_model=FamilyContact)
async def update_contact(contact_id: str, contact: FamilyContact):
    """Actualizar un contacto familiar"""
    try:
        # Si se está marcando como primario, desmarcar otros contactos primarios
        if contact.is_primary:
            supabase_client.table('family_contacts')\
                .update({'is_primary': False})\
                .eq('resident_id', contact.resident_id)\
                .execute()

        data = contact.dict(exclude_unset=True)
        if 'id' in data:
            del data['id']
        if 'created_at' in data:
            del data['created_at']
        if 'updated_at' in data:
            del data['updated_at']

        logger.info(f"Updating family contact {contact_id}: {data}")
        response = supabase_client.table('family_contacts').update(data).eq('id', contact_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Contacto familiar no encontrado")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating family contact {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/family-contacts/{contact_id}")
async def delete_contact(contact_id: str):
    """Eliminar un contacto familiar"""
    try:
        response = supabase_client.table('family_contacts').delete().eq('id', contact_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Contacto familiar no encontrado")
        return {"message": "Contacto familiar eliminado"}
    except Exception as e:
        logger.error(f"Error deleting family contact {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 