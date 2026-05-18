from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.domain.api.v1 import tasks, user, competition, achievements, ai
from app.infrastructure.database import init_db

app = FastAPI(title="EGE Math Trainer 2026")

@app.on_event("startup")
async def startup():
    await init_db()

app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
def index():
    return FileResponse("web/index.html")

app.include_router(tasks.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(competition.router, prefix="/api/v1")
app.include_router(achievements.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")