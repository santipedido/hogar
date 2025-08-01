from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents, upload, family_contacts, medications
from routers import vital_signs, activities

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hogarged.netlify.app",
        "http://186.119.90.87",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Incluir routers con prefijo /api
app.include_router(residents.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(family_contacts.router, prefix="/api")
app.include_router(medications.router, prefix="/api")
app.include_router(vital_signs.router, prefix="/api")
app.include_router(activities.router, prefix="/api")

@app.get("/ping")
def ping():
    return {"message": "pong", "status": "healthy"} 