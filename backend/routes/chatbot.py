from flask import Blueprint
from backend.services.chatbot_service import send_chatbot_response


chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route('/api/chatbot', methods=['POST'])
def chatbot_response():
    return send_chatbot_response()


