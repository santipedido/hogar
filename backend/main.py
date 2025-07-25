from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import residents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://hogarged.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

app.include_router(residents.router)

@app.get("/ping")
def ping():
    return {"message": "pong"} 