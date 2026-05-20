from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1 import tasks, user, competition, achievements, ai
from app.infrastructure.database import init_db

ROOT_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="EGE Math Trainer 2026",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()

app.mount("/static", StaticFiles(directory=ROOT_DIR / "web"), name="static")

@app.get("/")
def index():
    return FileResponse(ROOT_DIR / "web" / "index.html")

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(competition.router, prefix="/api/v1")
app.include_router(achievements.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")