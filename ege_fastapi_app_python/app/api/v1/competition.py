from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.dependencies import get_db
from app.core.security import verify_token
from app.infrastructure.repositories.task_repository import TaskRepository
from app.domain.services.competition_service import CompetitionService
from app.domain.services.stats_service import StatsService
from app.schemas.task import CompetitionOut, VariantOut, SubmitRequest, AttemptResult, LeaderboardEntry

router = APIRouter(prefix="/competition", tags=["competition"])

@router.post("/create", response_model=CompetitionOut)
async def create_competition(
    name: str,
    duration_minutes: int = 60,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = CompetitionService(db, repo)
    comp = await service.create(name, duration_minutes)
    return CompetitionOut(
        id=comp.id,
        name=comp.name,
        start_time=comp.start_time,
        end_time=comp.end_time,
        is_active=True
    )

@router.post("/{comp_id}/join", response_model=VariantOut)
async def join_competition(
    comp_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = CompetitionService(db, repo)
    try:
        attempt = await service.join(comp_id, user_id)
        tasks_out = [
            {
                "id": at.task.id,
                "sdamgia_id": at.task.sdamgia_id,
                "topic": at.task.topic,
                "text": at.task.text,
                "difficulty": at.task.difficulty,
                "tags": at.task.tags,
                "part": at.task.part
            }
            for at in attempt.attempt_tasks
        ]
        return VariantOut(tasks=tasks_out, attempt_id=attempt.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/submit", response_model=AttemptResult)
async def submit_competition(
    request: SubmitRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = CompetitionService(db, repo)
    try:
        result = await service.submit(request.attempt_id, request.user_id, {a.task_id: a.answer for a in request.answers})
        await StatsService.update_stats(db, request.user_id, request.attempt_id)
        await StatsService.check_achievements(db, request.user_id, request.attempt_id)
        await db.commit()
        return result
    except Exception as e:
        raise HTTPException(status_code=getattr(e, 'status_code', 400), detail=str(e))

@router.get("/{comp_id}/leaderboard", response_model=List[LeaderboardEntry])
async def leaderboard(
    comp_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = TaskRepository(db)
    service = CompetitionService(db, repo)
    board = await service.leaderboard(comp_id, limit)
    return board