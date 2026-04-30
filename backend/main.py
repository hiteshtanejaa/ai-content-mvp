from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.services.database import Base, engine
from src.services import models  # noqa: F401 — ensure models are registered
from src.api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Content Calendar API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
