import json
import os
from datetime import datetime
from typing import List, Optional, Dict
from models import User, Event

class Storage:
    def __init__(self, user_file='users.json', event_file='events.json'):
        self.user_file = user_file
        self.event_file = event_file
        self.users: Dict[str, User] = {}
        self.events: List[Event] = []
        self._load_users()
        self._load_events()

    # Пользователи
    def _load_users(self):
        if os.path.exists(self.user_file) and os.path.getsize(self.user_file) > 0:
            try:
                with open(self.user_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for uid, u in data.items():
                        self.users[uid] = User(
                            username=u['username'],
                            password_hash=u['password_hash'],
                            user_id=u['user_id'],
                            token=u['token']
                        )
            except json.JSONDecodeError:
                self.users = {}
        else:
            self.users = {}

    def _save_users(self):
        data = {uid: {
            'username': u.username,
            'password_hash': u.password_hash,
            'user_id': u.user_id,
            'token': u.token
        } for uid, u in self.users.items()}
        with open(self.user_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def add_user(self, user: User):
        self.users[user.user_id] = user
        self._save_users()

    def get_user_by_username(self, username: str) -> Optional[User]:
        for u in self.users.values():
            if u.username == username:
                return u
        return None

    def get_user_by_token(self, token: str) -> Optional[User]:
        for u in self.users.values():
            if u.token == token:
                return u
        return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    # События
    def _load_events(self):
        if os.path.exists(self.event_file) and os.path.getsize(self.event_file) > 0:
            try:
                with open(self.event_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for ev in data:
                        self.events.append(Event(
                            event_id=ev['event_id'],
                            creator_id=ev['creator_id'],
                            participants_ids=ev['participants_ids'],
                            start=datetime.fromisoformat(ev['start']),
                            end=datetime.fromisoformat(ev['end']),
                            title=ev['title']
                        ))
            except json.JSONDecodeError:
                self.events = []
        else:
            self.events = []

    def _save_events(self):
        data = [{
            'event_id': e.event_id,
            'creator_id': e.creator_id,
            'participants_ids': e.participants_ids,
            'start': e.start.isoformat(),
            'end': e.end.isoformat(),
            'title': e.title
        } for e in self.events]
        with open(self.event_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def add_event(self, event: Event):
        self.events.append(event)
        self._save_events()

    def get_user_events(self, user_id: str) -> List[Event]:
        return [e for e in self.events if user_id in e.participants_ids]


    # Проверяем, свободны ли все участники
    def is_available(self, participants_ids: List[str], start: datetime, end: datetime) -> tuple[bool, Optional[str]]:
        for uid in participants_ids:
            for event in self.get_user_events(uid):
                if event.overlaps(Event(event_id='', creator_id='', participants_ids=[], start=start, end=end, title='')):
                    return False, uid
        return True, None