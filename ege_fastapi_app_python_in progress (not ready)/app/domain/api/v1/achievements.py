from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.core.security import verify_token
from app.infrastructure.repositories.user_repository import UserRepository

router = APIRouter(prefix="/achievements", tags=["achievements"])

@router.get("/{user_id}")
async def user_achievements(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        return []
    return [
        {
            "code": ua.achievement.code,
            "name": ua.achievement.name,
            "description": ua.achievement.description,
            "icon": ua.achievement.icon,
            "unlocked_at": ua.unlocked_at.isoformat()
        }
        for ua in user.achievements
    ]