from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import Competition, Attempt, AttemptTask
from app.domain.ports import TaskRepositoryPort
from app.core.exceptions import AccessDenied, TimeExpired, AttemptNotFound

class CompetitionService:
    def __init__(self, db: AsyncSession, task_repo: TaskRepositoryPort):
        self.db = db
        self.task_repo = task_repo

    async def create(self, name: str, duration_minutes: int) -> Competition:
        now = datetime.utcnow()
        comp = Competition(
            name=name,
            start_time=now,
            end_time=now + timedelta(minutes=duration_minutes),
            is_active=1
        )
        self.db.add(comp)
        await self.db.commit()
        return comp

    async def join(self, comp_id: int, user_id: int) -> Attempt:
        comp = await self.db.get(Competition, comp_id)
        if not comp or not self._is_active(comp):
            raise ValueError("Соревнование неактивно")
        tasks = await self._fetch_tasks()
        attempt = Attempt(
            user_id=user_id,
            competition_id=comp_id,
            type="competition",
            max_score=len(tasks),
            started_at=datetime.utcnow()
        )
        self.db.add(attempt)
        await self.db.flush()
        for task in tasks:
            self.db.add(AttemptTask(attempt_id=attempt.id, task_id=task.id))
        await self.db.commit()
        return attempt

    async def submit(self, attempt_id: int, user_id: int, answers: dict) -> dict:
        attempt = await self.db.get(Attempt, attempt_id)
        if not attempt:
            raise AttemptNotFound()
        if attempt.user_id != user_id:
            raise AccessDenied()
        if attempt.competition_id:
            comp = await self.db.get(Competition, attempt.competition_id)
            if comp and not self._is_active(comp):
                raise TimeExpired()
        from app.infrastructure.services.math_utils import normalize_answer
        from sqlalchemy import select
        stmt = select(AttemptTask).where(AttemptTask.attempt_id == attempt_id)
        result = await self.db.execute(stmt)
        attempt_tasks = result.scalars().all()
        score = 0
        details = []
        for at in attempt_tasks:
            task = at.task
            ua = normalize_answer(answers.get(str(at.task_id), ""))
            ca = normalize_answer(task.answer)
            is_correct = (ua == ca)
            at.user_answer = ua
            at.is_correct = is_correct
            if is_correct:
                score += 1
            details.append({
                "task_id": at.task_id,
                "topic": task.topic,
                "your_answer": ua,
                "correct_answer": ca,
                "is_correct": is_correct
            })
        attempt.score = score
        await self.db.commit()
        return {"score": score, "max_score": attempt.max_score, "type": attempt.type, "details": details}

    async def leaderboard(self, comp_id: int, limit: int = 50) -> list:
        from sqlalchemy import select
        from app.infrastructure.database import User
        comp = await self.db.get(Competition, comp_id)
        if not comp:
            return []
        stmt = select(Attempt).where(Attempt.competition_id == comp_id).order_by(Attempt.score.desc()).limit(limit)
        attempts = (await self.db.execute(stmt)).scalars().all()
        board = []
        for a in attempts:
            user = await self.db.get(User, a.user_id)
            board.append({
                "username": user.username,
                "score": a.score,
                "max_score": a.max_score,
                "timestamp": a.timestamp.isoformat()
            })
        return board

    def _is_active(self, comp: Competition) -> bool:
        if not comp.is_active:
            return False
        if comp.end_time and datetime.utcnow() > comp.end_time:
            return False
        return True

    async def _fetch_tasks(self):
        from app.infrastructure.services.sdamgia_service import SdamGiaService
        sdamgia = SdamGiaService()
        return await sdamgia.fetch_and_cache_tasks(self.db, list(range(1, 20)))