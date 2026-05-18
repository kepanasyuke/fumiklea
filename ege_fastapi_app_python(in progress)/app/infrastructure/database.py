from datetime import datetime
from pathlib import Path
from sqlalchemy import (Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text, Boolean)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    stats = relationship("UserStats", back_populates="user", uselist=False)
    achievements = relationship("UserAchievement", back_populates="user")

class UserStats(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_attempts = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    best_score = Column(Integer, default=0)
    avg_score = Column(Float, default=0.0)
    topic_performance = Column(JSON, default=dict)
    current_streak = Column(Integer, default=0)
    user = relationship("User", back_populates="stats")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    sdamgia_id = Column(String, unique=True, index=True)
    topic = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    answer = Column(String, nullable=False)
    difficulty = Column(Integer, default=1)
    tags = Column(JSON, default=list)
    part = Column(Integer, default=1)
    attempt_tasks = relationship("AttemptTask", back_populates="task")

class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Integer, default=0)
    max_score = Column(Integer, default=0)
    type = Column(String, default="full")
    attempt_tasks = relationship("AttemptTask", back_populates="attempt", cascade="all, delete")
    competition = relationship("Competition", back_populates="attempts")

class AttemptTask(Base):
    __tablename__ = "attempt_tasks"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_answer = Column(String, nullable=True)
    is_correct = Column(Boolean, default=False)
    attempt = relationship("Attempt", back_populates="attempt_tasks")
    task = relationship("Task", back_populates="attempt_tasks")

class Competition(Base):
    __tablename__ = "competitions"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)
    attempts = relationship("Attempt", back_populates="competition")

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)
    description = Column(String)
    icon = Column(String, default="🏆")

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")

async def init_db():
    if settings.DATABASE_URL.startswith("sqlite+aiosqlite:///"):
        db_path = Path(settings.DATABASE_URL.removeprefix("sqlite+aiosqlite:///"))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()