import asyncio
import random
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.task_repository import TaskRepository
from sdamgia import SdamGIA

class SdamGiaService:
    def __init__(self):
        self.client = SdamGIA()
        self.subject = 'math'
        self.executor = ThreadPoolExecutor(max_workers=10)

    def _fetch(self, problem_id: str):
        try:
            return self.client.get_problem_by_id(self.subject, problem_id)
        except Exception:
            return None

    async def fetch_and_cache_tasks(self, db: AsyncSession, numbers: list) -> list:
        repo = TaskRepository(db)
        loop = asyncio.get_running_loop()
        async def get_ids(num):
            ids = await loop.run_in_executor(None, self.client.search, self.subject, f"Задание {num}")
            return random.choice(ids) if ids else None
        chosen_ids = await asyncio.gather(*[get_ids(n) for n in numbers])
        chosen_ids = [cid for cid in chosen_ids if cid]
        async def process(prob_id):
            cached = await repo.get_by_sdamgia_id(prob_id)
            if cached:
                return cached
            problem = await loop.run_in_executor(self.executor, self._fetch, prob_id)
            if problem:
                data = self._parse_problem(problem)
                return await repo.create_task(**data)
            return None
        results = []
        for cid in chosen_ids:
            task = await process(cid)
            if task:
                results.append(task)
        return results

    def _parse_problem(self, problem: dict) -> dict:
        return {
            "sdamgia_id": str(problem.get("id")),
            "topic": problem.get("topic", "Неизвестная"),
            "text": problem.get("text", ""),
            "answer": str(problem.get("answer", "")).strip(),
            "difficulty": 1,
            "tags": problem.get("tags", []),
            "part": 1 if problem.get("number", 1) <= 12 else 2
        }