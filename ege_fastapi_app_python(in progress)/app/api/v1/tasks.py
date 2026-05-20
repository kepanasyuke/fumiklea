from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.core.security import verify_token
from app.infrastructure.repositories.task_repository import TaskRepository
from app.domain.services.variant_service import VariantService
from app.domain.services.stats_service import StatsService
from app.infrastructure.services.sdamgia_service import SdamGiaService
from app.schemas.task import VariantOut, SubmitRequest, AttemptResult, TaskBankOut

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/variant/generate", response_model=VariantOut)
async def generate_variant(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = VariantService(db, repo)
    data = await service.generate_full_variant(user_id)
    return VariantOut(**data)

@router.post("/variant/submit", response_model=AttemptResult)
async def submit_variant(
    request: SubmitRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = VariantService(db, repo)
    result = await service.submit(request.attempt_id, request.user_id, {a.task_id: a.answer for a in request.answers})
    await StatsService.update_stats(db, request.user_id, request.attempt_id)
    await StatsService.check_achievements(db, request.user_id, request.attempt_id)
    await db.commit()
    return result

@router.post("/time-attack/start", response_model=VariantOut)
async def start_time_attack(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = VariantService(db, repo)
    data = await service.generate_time_attack(user_id)
    return VariantOut(**data)

@router.get("/bank", response_model=TaskBankOut)
async def get_task_bank(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    service = SdamGiaService()
    bank_data = await service.get_task_bank()
    return TaskBankOut(**bank_data)
