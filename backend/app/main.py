from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.jobs.scheduler import start_scheduler, stop_scheduler
from app.routers import admin, admin_data, auth, cm, notificaciones

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Sistema de gestión de campañas · INNquietus", lifespan=lifespan)

# CORS abierto solo para el servidor de desarrollo de React (Vite); en
# producción el frontend se sirve desde el propio backend (mismo origen).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(admin_data.router)
app.include_router(cm.router)
app.include_router(notificaciones.router)


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


# El build de producción del frontend (npm run build) cae aquí, según
# vite.config.ts. Se monta al final para que las rutas /api/* de arriba
# sigan teniendo prioridad. Si no existe (p. ej. en desarrollo con
# `npm run dev` aparte), el backend sigue funcionando solo como API.
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
