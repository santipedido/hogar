from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents, upload

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

app.include_router(residents.router)
app.include_router(upload.router)

@app.get("/ping")
def ping():
    return {"message": "pong"} 