import os
from supabase import Client, create_client
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Faltan credenciales de Supabase")
    raise ValueError("SUPABASE_URL y SUPABASE_KEY son requeridas")

try:
    logger.info("Inicializando cliente de Supabase...")
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Verificar la conexión intentando listar los buckets
    try:
        buckets = supabase_client.storage.list_buckets()
        logger.info(f"Conexión exitosa. Buckets disponibles: {buckets}")
    except Exception as e:
        logger.warning(f"No se pudieron listar los buckets: {str(e)}")
    
    logger.info("Cliente de Supabase inicializado correctamente")
except Exception as e:
    logger.error(f"Error al inicializar cliente de Supabase: {str(e)}")
    raise 