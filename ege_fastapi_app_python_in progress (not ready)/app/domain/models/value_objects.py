from dataclasses import dataclass

@dataclass(frozen=True)
class Score:
    value: int

@dataclass(frozen=True)
class TopicPerformance:
    correct: int
    total: int