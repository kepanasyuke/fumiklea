from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database import UserStats, AttemptTask, Achievement, UserAchievement, User

class StatsService:
    @staticmethod
    async def update_stats(db: AsyncSession, user_id: int, attempt_id: int):
        stmt = select(UserStats).where(UserStats.user_id == user_id)
        stats = (await db.execute(stmt)).scalar_one_or_none()
        if not stats:
            stats = UserStats(user_id=user_id)
            db.add(stats)
        stmt = select(AttemptTask).where(AttemptTask.attempt_id == attempt_id)
        attempt_tasks = (await db.execute(stmt)).scalars().all()
        score = sum(1 for at in attempt_tasks if at.is_correct)
        max_score = len(attempt_tasks)
        stats.total_attempts += 1
        stats.total_score += score
        stats.avg_score = stats.total_score / stats.total_attempts
        if score > stats.best_score:
            stats.best_score = score
        if not stats.topic_performance:
            stats.topic_performance = {}
        for at in attempt_tasks:
            topic = at.task.topic
            if topic not in stats.topic_performance:
                stats.topic_performance[topic] = {"correct": 0, "total": 0}
            stats.topic_performance[topic]["total"] += 1
            if at.is_correct:
                stats.topic_performance[topic]["correct"] += 1

    @staticmethod
    async def check_achievements(db: AsyncSession, user_id: int, attempt_id: int):
        user = await db.get(User, user_id)
        stmt = select(AttemptTask).where(AttemptTask.attempt_id == attempt_id).order_by(AttemptTask.id)
        attempt_tasks = (await db.execute(stmt)).scalars().all()
        part1_tasks = [at for at in attempt_tasks if at.task.part == 1]
        if part1_tasks and all(at.is_correct for at in part1_tasks):
            await _unlock(db, user, "perfect_part1")
        streak = 0
        max_streak = 0
        for at in attempt_tasks:
            if at.is_correct:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        if max_streak >= 5:
            await _unlock(db, user, "streak5")
        if all(at.is_correct for at in attempt_tasks):
            await _unlock(db, user, "master")
        stmt = select(UserStats).where(UserStats.user_id == user_id)
        stats = (await db.execute(stmt)).scalar_one_or_none()
        if stats and stats.total_attempts >= 10:
            await _unlock(db, user, "10_attempts")

    @staticmethod
    async def get_weak_topics(db: AsyncSession, user_id: int) -> list:
        stmt = select(UserStats).where(UserStats.user_id == user_id)
        stats = (await db.execute(stmt)).scalar_one_or_none()
        if not stats or not stats.topic_performance:
            return []
        weak = []
        for topic, perf in stats.topic_performance.items():
            if perf["total"] >= 3 and (perf["correct"] / perf["total"]) < 0.5:
                weak.append(topic)
        return weak

async def _unlock(db: AsyncSession, user: User, code: str):
    stmt = select(Achievement).where(Achievement.code == code)
    achievement = (await db.execute(stmt)).scalar_one_or_none()
    if not achievement:
        achievement = Achievement(code=code, name=code, description="")
        db.add(achievement)
        await db.flush()
    stmt = select(UserAchievement).where(
        UserAchievement.user_id == user.id,
        UserAchievement.achievement_id == achievement.id
    )
    exists = (await db.execute(stmt)).scalar_one_or_none()
    if not exists:
        db.add(UserAchievement(user_id=user.id, achievement_id=achievement.id))
        await db.flush()