from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.dependencies import get_db
from app.core.security import verify_token
from app.infrastructure.repositories.user_repository import UserRepository
from app.domain.services.stats_service import StatsService
from app.schemas.task import UserStatsOut

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/register")
async def register(
    username: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = UserRepository(db)
    try:
        user = await repo.create_user(username)
        await db.commit()
        return {"user_id": user.id, "username": user.username}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Пользователь с таким именем уже существует")

@router.get("/stats/{user_id}", response_model=UserStatsOut)
async def get_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    weak = await StatsService.get_weak_topics(db, user_id)
    achievements = [ua.achievement.code for ua in user.achievements]
    stats = user.stats
    if not stats:
        return UserStatsOut(total_attempts=0, avg_score=0.0, best_score=0, weak_topics=[], achievements=[])
    return UserStatsOut(
        total_attempts=stats.total_attempts,
        avg_score=stats.avg_score,
        best_score=stats.best_score,
        weak_topics=weak,
        achievements=achievements
    )