from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database import Attempt, AttemptTask, Task
from app.domain.ports import TaskRepositoryPort
from app.core.exceptions import AttemptNotFound, AccessDenied, TimeExpired
from app.infrastructure.services.math_utils import normalize_answer

class VariantService:
    def __init__(self, db: AsyncSession, task_repo: TaskRepositoryPort):
        self.db = db
        self.task_repo = task_repo

    async def generate_full_variant(self, user_id: int) -> dict:
        tasks = []
        for i in range(1, 20):
            task = Task(
                sdamgia_id=f"test_{i}",
                topic="Тестовая тема",
                text=f"Тестовое задание №{i}",
                answer="42",
                difficulty=1,
                tags=[],
                part=1 if i <= 12 else 2
            )
            self.db.add(task)
            tasks.append(task)
        await self.db.flush()
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
            }
            for t in tasks
        ]
        return {"attempt_id": attempt.id, "tasks": tasks_out}

    async def generate_time_attack(self, user_id: int) -> dict:
        tasks = []
        for i in range(1, 13):
            task = Task(
                sdamgia_id=f"test_ta_{i}",
                topic="Тестовая тема",
                text=f"Тестовое задание Time Attack №{i}",
                answer="42",
                difficulty=1,
                tags=[],
                part=1
            )
            self.db.add(task)
            tasks.append(task)
        await self.db.flush()
        attempt = Attempt(user_id=user_id, type="time_attack", max_score=12, started_at=datetime.utcnow())
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
            }
            for t in tasks
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
        for at in attempt_tasks:
            task = at.task
            user_ans = normalize_answer(answers.get(str(at.task_id), ""))
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
