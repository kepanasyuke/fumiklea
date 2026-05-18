from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.core.security import verify_token
from app.infrastructure.repositories.task_repository import TaskRepository
from app.domain.services.variant_service import VariantService
from app.schemas.task import TaskOut, VariantOut, SubmitRequest, AttemptResult

router = APIRouter(prefix="/tasks", tags=["tasks"])

def _task_to_out(task) -> TaskOut:
    return TaskOut(
        id=task.id,
        sdamgia_id=task.sdamgia_id,
        topic=task.topic,
        text=task.text,
        difficulty=task.difficulty,
        tags=task.tags,
        part=task.part
    )

@router.post("/variant/generate", response_model=VariantOut)
async def generate_variant(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = VariantService(db, repo)
    attempt = await service.generate_full_variant(user_id)
    tasks_out = [_task_to_out(at.task) for at in attempt.attempt_tasks]
    return VariantOut(tasks=tasks_out, attempt_id=attempt.id)

@router.post("/variant/submit", response_model=AttemptResult)
async def submit_variant(
    request: SubmitRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = VariantService(db, repo)
    result = await service.submit(request.attempt_id, request.user_id, {a.task_id: a.answer for a in request.answers})
    return result

@router.post("/time-attack/start", response_model=VariantOut)
async def start_time_attack(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = VariantService(db, repo)
    attempt = await service.generate_time_attack(user_id)
    tasks_out = [_task_to_out(at.task) for at in attempt.attempt_tasks]
    return VariantOut(tasks=tasks_out, attempt_id=attempt.id)