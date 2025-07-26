from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import os
from PIL import Image
import io
import uuid
from datetime import datetime
from supabase_client import supabase_client

router = APIRouter()

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_valid_image(file_content: bytes) -> bool:
    try:
        img = Image.open(io.BytesIO(file_content))
        img.verify()
        return True
    except:
        return False

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Verificar extensión
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Formato de archivo no permitido. Use: .jpg, .jpeg, .png o .gif"
        )

    # Leer el archivo
    contents = await file.read()
    
    # Verificar tamaño
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="El archivo es demasiado grande. Máximo 5MB."
        )

    # Verificar que sea una imagen válida
    if not is_valid_image(contents):
        raise HTTPException(
            status_code=400,
            detail="El archivo no es una imagen válida"
        )

    try:
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_uuid = str(uuid.uuid4())[:8]
        new_filename = f"resident_photo_{timestamp}_{random_uuid}{file_ext}"

        # Subir a Supabase Storage
        response = supabase_client.storage.from_('residents').upload(
            new_filename,
            contents,
            file_options={"content-type": file.content_type}
        )

        if response.error:
            raise HTTPException(
                status_code=500,
                detail="Error al subir el archivo"
            )

        # Obtener URL pública
        file_url = supabase_client.storage.from_('residents').get_public_url(new_filename)

        return {"url": file_url}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el archivo: {str(e)}"
        ) 