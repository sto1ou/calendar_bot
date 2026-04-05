import pytest
import tempfile
import os
from calendar_bot import app
from storage import Storage


@pytest.fixture
def client():
    # Создаём временные файлы
    uf = tempfile.NamedTemporaryFile(suffix='_users.json', delete=False)
    ef = tempfile.NamedTemporaryFile(suffix='_events.json', delete=False)
    uf.close()
    ef.close()

    # Создаём новый экземпляр с временными файлами
    from calendar_bot import storage
    storage.user_file = uf.name
    storage.event_file = ef.name

    storage._load_users()
    storage._load_events()

    with app.test_client() as client:
        yield client

    # Удаляем временные файлы после тестов
    os.unlink(uf.name)
    os.unlink(ef.name)


def test_register_and_login(client):
    resp = client.post('/register', json={
        'username': 'Алиса',
        'password': 'secret'
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'token' in data
    token = data['token']

    resp = client.post('/login', json={
        'username': 'Алиса',
        'password': 'secret'
    })
    assert resp.status_code == 200
    assert resp.get_json()['token'] != token


def test_create_event_success(client):
    client.post('/register', json={'username': 'Алиса', 'password': 'pass'})
    client.post('/register', json={'username': 'Боб', 'password': 'pass'})

    login_resp = client.post('/login', json={'username': 'Алиса', 'password': 'pass'})
    token = login_resp.get_json()['token']

    resp = client.post('/create_event',
                       headers={'Authorization': f'Bearer {token}'},
                       json={
                           'participants_usernames': ['Боб'],
                           'start': '2025-05-01T10:00:00',
                           'end': '2025-05-01T11:00:00',
                           'title': 'Встреча'
                       })
    assert resp.status_code == 201


def test_create_event_nonexistent_user(client):
    client.post('/register', json={'username': 'Алиса', 'password': 'pass'})
    login_resp = client.post('/login', json={'username': 'Алиса', 'password': 'pass'})
    token = login_resp.get_json()['token']

    resp = client.post('/create_event',
                       headers={'Authorization': f'Bearer {token}'},
                       json={
                           'participants_usernames': ['charlie'],
                           'start': '2025-05-01T10:00:00',
                           'end': '2025-05-01T11:00:00',
                           'title': 'Встреча'
                       })
    assert resp.status_code == 400
    assert 'does not exist' in resp.get_json()['error']


def test_event_overlap(client):
    client.post('/register', json={'username': 'Алиса', 'password': 'pass'})
    client.post('/register', json={'username': 'Боб', 'password': 'pass'})
    login_resp = client.post('/login', json={'username': 'Алиса', 'password': 'pass'})
    token = login_resp.get_json()['token']

    client.post('/create_event',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'participants_usernames': ['Боб'],
                    'start': '2025-05-01T10:00:00',
                    'end': '2025-05-01T11:00:00',
                    'title': 'Важно'
                })
    resp = client.post('/create_event',
                       headers={'Authorization': f'Bearer {token}'},
                       json={
                           'participants_usernames': ['Боб'],
                           'start': '2025-05-01T10:30:00',
                           'end': '2025-05-01T11:30:00',
                           'title': 'Событие'
                       })
    assert resp.status_code == 409
    assert 'already busy' in resp.get_json()['error']