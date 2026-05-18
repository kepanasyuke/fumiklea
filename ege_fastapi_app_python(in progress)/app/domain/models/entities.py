from datetime import datetime
from typing import List, Optional

class User:
    def __init__(self, id: int, username: str, created_at: datetime):
        self.id = id
        self.username = username
        self.created_at = created_at
        self.stats = None
        self.achievements = []

class Task:
    def __init__(
        self,
        id: int,
        sdamgia_id: str,
        topic: str,
        text: str,
        answer: str,
        difficulty: int,
        tags: List[str],
        part: int
    ):
        self.id = id
        self.sdamgia_id = sdamgia_id
        self.topic = topic
        self.text = text
        self.answer = answer
        self.difficulty = difficulty
        self.tags = tags
        self.part = part

class Attempt:
    def __init__(
        self,
        id: int,
        user_id: int,
        competition_id: Optional[int],
        timestamp: datetime,
        started_at: datetime,
        score: int,
        max_score: int,
        type: str
    ):
        self.id = id
        self.user_id = user_id
        self.competition_id = competition_id
        self.timestamp = timestamp
        self.started_at = started_at
        self.score = score
        self.max_score = max_score
        self.type = type
        self.attempt_tasks = []

class AttemptTask:
    def __init__(self, id: int, attempt_id: int, task_id: int, user_answer: str, is_correct: bool):
        self.id = id
        self.attempt_id = attempt_id
        self.task_id = task_id
        self.user_answer = user_answer
        self.is_correct = is_correct

class Competition:
    def __init__(
        self,
        id: int,
        name: str,
        start_time: datetime,
        end_time: Optional[datetime],
        is_active: bool
    ):
        self.id = id
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.is_active = is_active