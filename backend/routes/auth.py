from flask import Blueprint, request, jsonify
from models.user import User
from app import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():

    frontend = request.get_json()

    username = frontend.get('username')
    password = frontend.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        return jsonify({
            "user_id" : user.user_id,
            "username" : user.username,
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
        })

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "New user created!", "status":"Success"})
