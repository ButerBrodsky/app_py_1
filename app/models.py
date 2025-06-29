from config import USERS
from flask_jwt_extended import get_jwt_identity

# Получить текущего пользователя из токена
def get_current_user():
    username = get_jwt_identity()
    return USERS.get(username)

# Получить все пользователи
def get_all_users():
    return USERS

# Получить конкретного пользователя
def get_user_by_username(username):
    return USERS.get(username)

# Обновить данные пользователя
def update_user(username, data):
    if username in USERS:
        USERS[username].update(data)
        return True
    return False

# Удалить пользователя
def delete_user(username):
    if username in USERS:
        del USERS[username]
        return True
    return False

# Добавить нового пользователя
def create_user(username, password):
    if username in USERS:
        return False, "User already exists"
    USERS[username] = {"password": password, "role": "user"}
    return True, "User created"