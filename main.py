import os
import shutil
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import content, gifts, payments


app = FastAPI(title="Wedding Gift API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gifts.router, prefix="/api/gifts", tags=["gifts"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.mount("/static", StaticFiles(directory="static"), name="static")
uploads_dir = Path(os.getenv("UPLOADS_DIR", "uploads"))
uploads_seed_dir = Path(os.getenv("UPLOADS_SEED_DIR", "uploads_seed"))
uploads_dir.mkdir(parents=True, exist_ok=True)
if uploads_seed_dir.exists() and not any(uploads_dir.iterdir()):
    for item in uploads_seed_dir.iterdir():
        destination = uploads_dir / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


def prepare_seed_database():
    database_url = settings.database_url
    if not database_url.startswith("sqlite:///"):
        return

    database_path = Path(database_url.removeprefix("sqlite:///"))
    seed_path = Path(os.getenv("SEED_DATABASE_PATH", "seed_wedding.db"))
    if database_path.exists() or not seed_path.exists():
        return

    database_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(seed_path, database_path)


@app.on_event("startup")
def on_startup():
    prepare_seed_database()
    init_db()


@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend do site de casamento rodando"}


@app.get("/")
@app.get("/pagamento/sucesso")
@app.get("/pagamento/falha")
@app.get("/pagamento/pendente")
def serve_site():
    return FileResponse("static/index.html")
