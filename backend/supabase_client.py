import os
from supabase import create_client
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Usar service role key para tener permisos de admin

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Faltan credenciales de Supabase")
    raise ValueError("SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY son requeridas")

try:
    logger.info(f"Inicializando cliente de Supabase con URL: {SUPABASE_URL}")
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Verificar la conexión intentando listar los buckets
    try:
        logger.info("Verificando conexión a Supabase Storage...")
        buckets = supabase_client.storage.list_buckets()
        logger.info(f"Conexión exitosa. Buckets disponibles: {[bucket.name for bucket in buckets]}")
    except Exception as e:
        logger.warning(f"No se pudieron listar los buckets: {str(e)}")
        logger.warning("Esto podría indicar un problema con los permisos o la configuración de Storage")
    
    logger.info("Cliente de Supabase inicializado correctamente")
except Exception as e:
    logger.error(f"Error al inicializar cliente de Supabase: {str(e)}")
    raise 