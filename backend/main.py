from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents, upload

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(residents.router, prefix="/api", tags=["residents"])
app.include_router(upload.router, prefix="/api", tags=["upload"])

@app.get("/")
def read_root():
    return {"Hello": "World"} 