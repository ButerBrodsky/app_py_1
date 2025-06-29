from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
)
from models import (
    get_all_users,
    get_user_by_username,
    update_user,
    delete_user,
    create_user,
)

api = Blueprint("api", __name__)


# Логин
@api.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    from config import USERS

    user = USERS.get(username)
    if user and user["password"] == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401


# Получить свой профиль
@api.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    current_username = get_jwt_identity()
    current_user = get_user_by_username(current_username)

    if not current_user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({
        "username": current_username,
        "role": current_user.get("role", "user")
    }), 200


# Редактировать себя
@api.route("/profile", methods=["PUT"])
@jwt_required()
def edit_profile():
    current_username = get_jwt_identity()
    current_user = get_user_by_username(current_username)

    if not current_user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()

    if update_user(current_username, data):
        return jsonify({"msg": "Profile updated"}), 200
    return jsonify({"msg": "Update failed"}), 400


# Получить всех пользователей (только суперадмин)
@api.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    current_username = get_jwt_identity()
    current_user = get_user_by_username(current_username)

    if not current_user or current_user.get("role") != "superadmin":
        return jsonify({"msg": "Forbidden"}), 403

    users = get_all_users()
    return jsonify(users), 200


# Создать пользователя (только суперадмин)
@api.route("/users", methods=["POST"])
@jwt_required()
def add_user():
    current_username = get_jwt_identity()
    current_user = get_user_by_username(current_username)

    if not current_user or current_user.get("role") != "superadmin":
        return jsonify({"msg": "Forbidden"}), 403

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    success, msg = create_user(username, password)
    if success:
        return jsonify({"msg": msg}), 201
    return jsonify({"msg": msg}), 400


# Получить/удалить/редактировать другого пользователя (только суперадмин)
@api.route("/users/<username>", methods=["GET", "DELETE", "PUT"])
@jwt_required()
def manage_user(username):
    current_username = get_jwt_identity()
    current_user = get_user_by_username(current_username)

    if not current_user or current_user.get("role") != "superadmin":
        return jsonify({"msg": "Forbidden"}), 403

    user = get_user_by_username(username)
    if not user and request.method != "PUT":
        return jsonify({"msg": "User not found"}), 404

    if request.method == "GET":
        return jsonify({username: user}), 200

    elif request.method == "DELETE":
        if delete_user(username):
            return jsonify({"msg": "User deleted"}), 200
        return jsonify({"msg": "User not found"}), 404

    elif request.method == "PUT":
        data = request.get_json()
        if not data:
            return jsonify({"msg": "No data provided"}), 400

        if user:
            if update_user(username, data):
                return jsonify({"msg": "User updated"}), 200
            return jsonify({"msg": "User update failed"}), 400
        else:
            # Если пользователь не существует, можно создать
            password = data.get("password")
            if not password:
                return jsonify({"msg": "Password is required to create a new user"}), 400
            success, msg = create_user(username, password)
            if success:
                return jsonify({"msg": msg}), 201
            return jsonify({"msg": msg}), 400