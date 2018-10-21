from playhouse.shortcuts import model_to_dict, dict_to_model
from flask import Blueprint, jsonify
from src.model.user import User

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route("/")
def users():
    users = []
    for u in User.select():
        users.append(model_to_dict(u))
    return jsonify(users)
