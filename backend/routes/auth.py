from flask import Blueprint, request, jsonify
from backend.models.user import User
from backend.app import db

from backend.utils.auth_utils import create_access_token


auth_bp = Blueprint("auth", __name__)


@auth_bp.route('/api/login', methods=['POST'])
def login():

    frontend = request.get_json()

    username = frontend.get('username')
    password = frontend.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # create token
        token = create_access_token(user.user_id)

        return jsonify({
            "user_id" : user.user_id,
            "username" : user.username,
            "token" : token,
            "message":"Login successful!", 
            "status":"success"
        })

    return jsonify({
        "message":"Invalid credentials", 
        "status":"failure"
    }), 401
    


@auth_bp.route('/api/signup', methods=['POST'])
def signup():

    frontend = request.get_json()


    username = frontend.get('username')
    password = frontend.get('password')
    
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({
            "message": "User already exists!",
            "Status":"Failure"
        }), 409

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "New user created!", "status":"Success"}), 201


