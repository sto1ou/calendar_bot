from flask import Flask, request, jsonify
from datetime import datetime
from models import User, Event
from storage import Storage
from auth import hash_password, verify_password, generate_token, generate_user_id
from notification import Notifier
import uuid

app = Flask(__name__)
storage = Storage()
notifier = Notifier()

# Регистрация пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'username and password required'}), 400

    username = data['username'].strip()
    password = data['password']

    if storage.get_user_by_username(username):
        return jsonify({'error': 'username already exists'}), 409

    user_id = generate_user_id()
    token = generate_token()
    password_hash = hash_password(password)

    user = User(username=username, password_hash=password_hash,
                user_id=user_id, token=token)
    storage.add_user(user)

    return jsonify({
        'user_id': user_id,
        'username': username,
        'token': token
    }), 201


# Вход и выдача токена
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'username and password required'}), 400

    username = data['username']
    password = data['password']
    user = storage.get_user_by_username(username)
    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'invalid credentials'}), 401

    # Генерируем новый токен
    new_token = generate_token()
    user.token = new_token
    storage.add_user(user)  # сохраняем обновлённого пользователя

    return jsonify({'token': new_token, 'user_id': user.user_id}), 200

# Декоратор для проверки токена
def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'missing or invalid token'}), 401
        token = auth_header.split(' ')[1]
        user = storage.get_user_by_token(token)
        if not user:
            return jsonify({'error': 'invalid token'}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated

# Создание события (только авторизованные)
@app.route('/create_event', methods=['POST'])
@require_auth
def create_event():
    data = request.get_json()
    required = ['participants_usernames', 'start', 'end', 'title']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing fields'}), 400

    # Проверяем, что все указанные участники существуют
    participants_ids = []
    for username in data['participants_usernames']:
        user = storage.get_user_by_username(username)
        if not user:
            return jsonify({'error': f'user {username} does not exist'}), 400
        participants_ids.append(user.user_id)

    # Создатель тоже должен быть участником (добавляем автоматически)
    creator = request.current_user
    if creator.user_id not in participants_ids:
        participants_ids.append(creator.user_id)

    try:
        start = datetime.fromisoformat(data['start'])
        end = datetime.fromisoformat(data['end'])
    except ValueError:
        return jsonify({'error': 'invalid datetime format, use ISO 8601'}), 400

    if start >= end:
        return jsonify({'error': 'start must be before end'}), 400

    # Проверка доступности времени для всех участников
    available, busy_user_id = storage.is_available(participants_ids, start, end)
    if not available:
        busy_user = storage.get_user_by_id(busy_user_id)
        return jsonify({'error': f'user {busy_user.username} is already busy at this time'}), 409

    # Создаём событие
    event = Event(
        event_id=str(uuid.uuid4()),
        creator_id=creator.user_id,
        participants_ids=participants_ids,
        start=start,
        end=end,
        title=data['title']
    )
    storage.add_event(event)

    # Уведомляем всех участников
    notifier.notify([storage.get_user_by_id(uid).username for uid in participants_ids], event, storage)

    return jsonify({'status': 'created', 'event_id': event.event_id}), 201

# Получение событий текущего пользователя
@app.route('/events', methods=['GET'])
@require_auth
def get_events():
    user = request.current_user
    events = storage.get_user_events(user.user_id)
    return jsonify([{
        'event_id': e.event_id,
        'title': e.title,
        'creator_id': e.creator_id,
        'creator_username': storage.get_user_by_id(e.creator_id).username,
        'start': e.start.isoformat(),
        'end': e.end.isoformat(),
        'participants': [storage.get_user_by_id(pid).username for pid in e.participants_ids]
    } for e in events])

if __name__ == '__main__':
    app.run(debug=True)