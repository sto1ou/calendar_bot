from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class User:
    username: str
    password_hash: str  # для простоты храним хеш
    user_id: str
    token: str          # токен для аутентификации

@dataclass
class Event:
    event_id: str
    creator_id: str
    participants_ids: List[str]
    start: datetime
    end: datetime
    title: str

    def overlaps(self, other: 'Event') -> bool:
        return (self.start < other.end and self.end > other.start)