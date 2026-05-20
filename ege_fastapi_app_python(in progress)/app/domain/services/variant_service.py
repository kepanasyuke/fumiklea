from datetime import datetime
import urllib.parse
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database import Attempt, AttemptTask
from app.domain.ports import TaskRepositoryPort
from app.core.exceptions import AttemptNotFound, AccessDenied, TimeExpired
from app.infrastructure.services.math_utils import normalize_answer
from app.infrastructure.services.sdamgia_service import _extract_function

class VariantService:
    def __init__(self, db: AsyncSession, task_repo: TaskRepositoryPort):
        self.db = db
        self.task_repo = task_repo

    async def generate_full_variant(self, user_id: int) -> dict:
        tasks = await self._fetch_tasks(range(1, 20))
        attempt = Attempt(user_id=user_id, type="full", max_score=len(tasks))
        self.db.add(attempt)
        await self.db.flush()
        for task in tasks:
            self.db.add(AttemptTask(attempt_id=attempt.id, task_id=task.id))
        await self.db.commit()
        tasks_out = [
            {
                "id": t.id,
                "sdamgia_id": t.sdamgia_id,
                "topic": t.topic,
                "text": t.text,
                "difficulty": t.difficulty,
                "tags": t.tags,
                "part": t.part,
                "graph_url": _build_graph_url(t.text)
            }
            for t in tasks
        ]
        return {"attempt_id": attempt.id, "tasks": tasks_out}

    async def generate_time_attack(self, user_id: int) -> dict:
        tasks = await self._fetch_tasks(range(1, 13))
        if len(tasks) < 12:
            raise RuntimeError("Недостаточно заданий")
        attempt = Attempt(user_id=user_id, type="time_attack", max_score=12, started_at=datetime.utcnow())
        self.db.add(attempt)
        await self.db.flush()
        for task in tasks[:12]:
            self.db.add(AttemptTask(attempt_id=attempt.id, task_id=task.id))
        await self.db.commit()
        tasks_out = [
            {
                "id": t.id,
                "sdamgia_id": t.sdamgia_id,
                "topic": t.topic,
                "text": t.text,
                "difficulty": t.difficulty,
                "tags": t.tags,
                "part": t.part,
                "graph_url": _build_graph_url(t.text)
            }
            for t in tasks[:12]
        ]
        return {"attempt_id": attempt.id, "tasks": tasks_out}

    async def submit(self, attempt_id: int, user_id: int, answers: dict) -> dict:
        attempt = await self.db.get(Attempt, attempt_id)
        if not attempt:
            raise AttemptNotFound()
        if attempt.user_id != user_id:
            raise AccessDenied()
        if attempt.type == "time_attack":
            if (datetime.utcnow() - attempt.started_at).total_seconds() > 600:
                raise TimeExpired()
        stmt = select(AttemptTask).where(AttemptTask.attempt_id == attempt_id)
        result = await self.db.execute(stmt)
        attempt_tasks = result.scalars().all()
        score = 0
        details = []
        answer_map = {}
        if isinstance(answers, list):
            for item in answers:
                if isinstance(item, dict) and 'task_id' in item:
                    answer_map[str(item['task_id'])] = item.get('answer', '')
        elif isinstance(answers, dict):
            answer_map = answers

        for at in attempt_tasks:
            task = at.task
            user_ans = normalize_answer(answer_map.get(str(at.task_id), ""))
            correct_ans = normalize_answer(task.answer)
            is_correct = (user_ans == correct_ans)
            at.user_answer = user_ans
            at.is_correct = is_correct
            if is_correct:
                score += 1
            details.append({
                "task_id": at.task_id,
                "topic": task.topic,
                "your_answer": user_ans,
                "correct_answer": correct_ans,
                "is_correct": is_correct
            })
        attempt.score = score
        await self.db.commit()
        return {"score": score, "max_score": attempt.max_score, "type": attempt.type, "details": details}

    async def _fetch_tasks(self, numbers):
        from app.infrastructure.services.sdamgia_service import SdamGiaService
        sdamgia = SdamGiaService()
        return await sdamgia.fetch_and_cache_tasks(self.db, list(numbers))


def _build_graph_url(task_text: str) -> Optional[str]:
    try:
        func = _extract_function(task_text)
        if not func:
            return None
        encoded = urllib.parse.quote(func)
        return (
            f"https://www.geogebra.org/graphing"
            f"?command=f(x)={encoded}"
            f"&showToolBar=false&showAlgebraInput=false&showMenuBar=false"
            f"&showResetIcon=false&appName=graphing&language=ru"
        )
    except Exception:
        return None