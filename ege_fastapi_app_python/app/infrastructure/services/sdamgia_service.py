import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.task_repository import TaskRepository
from sdamgia import SdamGIA

class SdamGiaService:
    def __init__(self):
        self.client = SdamGIA()
        self.subject = 'math'

    def _fetch_problem(self, problem_id: str):
        try:
            return self.client.get_problem_by_id(self.subject, problem_id)
        except Exception:
            return None

    def _search_ids(self, query: str):
        try:
            return self.client.search(self.subject, query)
        except Exception:
            return []

    async def fetch_and_cache_tasks(self, db: AsyncSession, numbers: list) -> list:
        repo = TaskRepository(db)
        loop = asyncio.get_running_loop()
        chosen_ids = []
        for num in numbers:
            ids = await loop.run_in_executor(None, self._search_ids, f"Задание {num}")
            if ids:
                chosen_ids.append(random.choice(ids))
        tasks = []
        for cid in chosen_ids:
            cached = await repo.get_by_sdamgia_id(cid)
            if cached:
                tasks.append(cached)
                continue
            problem = await loop.run_in_executor(None, self._fetch_problem, cid)
            if problem:
                data = self._parse_problem(problem, cid)
                task = await repo.create_task(**data)
                tasks.append(task)
        return tasks

    def _parse_problem(self, problem: dict, sdamgia_id: str) -> dict:
        topic = problem.get("topic", "Неизвестная тема")
        text = problem.get("text", "")
        answer = str(problem.get("answer", "")).strip()
        tags = problem.get("tags", [])
        part = 1
        try:
            num = int(sdamgia_id.split(".")[0]) if "." in sdamgia_id else int(sdamgia_id)
            part = 1 if num <= 12 else 2
        except (ValueError, IndexError):
            pass
        return {
            "sdamgia_id": sdamgia_id,
            "topic": topic,
            "text": text,
            "answer": answer,
            "difficulty": 1,
            "tags": tags,
            "part": part
        }