import jwt
from datetime import datetime, timedelta
from flask import abort

from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables from .env file
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def create_access_token(user_id: int):
    payload = {
        "user_id" : user_id,
        "exp" : datetime.utcnow() + timedelta(hours=7)
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def get_current_user(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        abort(401, description="Missing token")

    try:
        token = auth_header.split(" ")[1]
        
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload["user_id"]

    except jwt.ExpiredSignatureError:
        abort(401, description="Token expired")
    except jwt.InvalidTokenError:
        abort(401, description="Invalid token")