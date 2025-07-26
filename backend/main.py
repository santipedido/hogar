from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents, upload, family_contacts

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hogarged.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Incluir routers
app.include_router(residents.router)
app.include_router(upload.router)
app.include_router(family_contacts.router)

@app.get("/ping")
def ping():
    return {"message": "pong"} 