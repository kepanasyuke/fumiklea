from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.domain.ports import UserRepositoryPort
from app.infrastructure.database import User

class UserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, username: str) -> User:
        user = User(username=username)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.session.get(User, user_id)