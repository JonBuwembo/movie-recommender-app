from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os
from pathlib import Path

# Initialize extensions 
db = SQLAlchemy()

# Load .env
# all files in backend will use this dotenv.
BASE_DIR = Path(__file__).resolve().parent # backend/ is parent
dotenv_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=dotenv_path)

# Reading environment variables for database connection
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)

    if not all([DB_NAME, DB_USER, DB_PASSWORD]):
        raise ValueError("Missing database environment variables")

    # configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints (bundles of routes)
    from backend.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from backend.routes.movies import movies_bp
    app.register_blueprint(movies_bp)

    from backend.routes.search import search_bp
    app.register_blueprint(search_bp)

    from backend.routes.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)