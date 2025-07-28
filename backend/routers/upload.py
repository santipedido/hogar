from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import os
from PIL import Image
import io
import uuid
from datetime import datetime
from supabase_client import supabase_client
import logging

# Configurar el router
router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
BUCKET_NAME = 'residents'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_image(file_content: bytes) -> bool:
    try:
        img = Image.open(io.BytesIO(file_content))
        img.verify()
        return True
    except Exception as e:
        logger.error(f"Error validando imagen: {str(e)}")
        return False

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info("Iniciando proceso de subida de archivo")
        
        # Verificar extensión
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Formato de archivo no permitido. Use: .jpg, .jpeg, .png o .gif"
            )

        # Mapear extensiones a MIME types correctos
        mime_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        content_type = mime_type_map.get(file_ext, 'image/jpeg')

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

        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_uuid = str(uuid.uuid4())[:8]
        new_filename = f"resident_photo_{timestamp}_{random_uuid}{file_ext}"

        logger.info(f"Intentando subir archivo: {new_filename}")

        try:
            # Verificar si el bucket existe
            buckets = supabase_client.storage.list_buckets()
            logger.info(f"Buckets disponibles: {buckets}")
            
            bucket_exists = False
            for bucket in buckets:
                if bucket.name == BUCKET_NAME:
                    bucket_exists = True
                    break

            if not bucket_exists:
                logger.info(f"El bucket {BUCKET_NAME} no existe, intentando crearlo...")
                try:
                    supabase_client.storage.create_bucket(BUCKET_NAME, {'public': True})
                    logger.info(f"Bucket {BUCKET_NAME} creado exitosamente")
                except Exception as e:
                    logger.error(f"No se pudo crear el bucket: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail="No se pudo crear el bucket de almacenamiento. Por favor, contacta al administrador."
                    )

            # Subir a Supabase Storage
            logger.info("Iniciando subida a Supabase Storage...")
            logger.info(f"Content type: {content_type}")
            logger.info(f"File size: {len(contents)} bytes")
            
            # Intentar con método alternativo
            try:
                response = supabase_client.storage.from_(BUCKET_NAME).upload(
                    path=new_filename,
                    file=contents,
                    file_options={"contentType": content_type, "upsert": True}
                )
            except Exception as e:
                logger.error(f"Error con método upload: {str(e)}")
                # Intentar método alternativo
                response = supabase_client.storage.from_(BUCKET_NAME).upload(
                    path=new_filename,
                    file=contents
                )
            
            logger.info(f"Archivo subido exitosamente: {response}")

            # Obtener URL pública
            file_url = supabase_client.storage.from_(BUCKET_NAME).get_public_url(new_filename)
            logger.info(f"URL pública generada: {file_url}")

            return {"url": file_url}

        except Exception as e:
            logger.error(f"Error en operación de Supabase: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar el archivo en Supabase: {str(e)}"
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        ) 