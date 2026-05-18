from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TaskOut(BaseModel):
    id: int
    sdamgia_id: str
    topic: str
    text: str
    difficulty: int
    tags: List[str]
    part: int
    answer: Optional[str] = None

class AnswerSubmit(BaseModel):
    task_id: int
    answer: str

class VariantOut(BaseModel):
    tasks: List[TaskOut]
    attempt_id: int

class SubmitRequest(BaseModel):
    user_id: int
    attempt_id: int
    answers: List[AnswerSubmit]

class AttemptResult(BaseModel):
    attempt_id: int
    score: int
    max_score: int
    type: str
    details: List[dict]

class CompetitionOut(BaseModel):
    id: int
    name: str
    start_time: datetime
    end_time: Optional[datetime]
    is_active: bool

class LeaderboardEntry(BaseModel):
    username: str
    score: int
    max_score: int
    timestamp: datetime

class UserStatsOut(BaseModel):
    total_attempts: int
    avg_score: float
    best_score: int
    weak_topics: List[str]
    achievements: List[str]