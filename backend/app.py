from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
from pathlib import Path

# Initialize extensions 
db = SQLAlchemy()

# Load .env
dotenv_path = Path(__file__).parent / "database" / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Reading environment variables for database connection
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    # configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    db.init_app(app)

    # register blueprints (bundles of routes)
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.movies import movies_bp
    app.register_blueprint(movies_bp)

    from routes.search import search_bp
    app.register_blueprint(search_bp)

    from routes.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp)

    return app