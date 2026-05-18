from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.domain.ports import TaskRepositoryPort
from app.infrastructure.database import Task

class TaskRepository(TaskRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_sdamgia_id(self, sdamgia_id: str) -> Optional[Task]:
        stmt = select(Task).where(Task.sdamgia_id == sdamgia_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_task(self, **kwargs) -> Task:
        task = Task(**kwargs)
        self.session.add(task)
        await self.session.flush()
        return task

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        return await self.session.get(Task, task_id)