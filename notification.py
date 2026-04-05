from models import Event
from typing import List

class Notifier:
    @staticmethod
    def notify(participant_usernames: List[str], event: Event, storage):
        message = (f"Новое событие: {event.title}\n"
                   f"Создатель: {storage.get_user_by_id(event.creator_id).username}\n"
                   f"Время: {event.start} – {event.end}")
        for uid in event.participants_ids:
            user = storage.get_user_by_id(uid)
            if user:
                print(f"[Уведомление для {user.username}]: {message}")