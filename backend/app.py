# /app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_mail import Mail  
from setup_cache import cache
from config import get_config
from model import db, User
from werkzeug.security import check_password_hash
import datetime
from routes.user_authentication import user_auth_bp
from routes.admin_authentication import admin_auth_bp
from routes.user_dashboard import user_dashboard_bp
from routes.admin_dashboard import admin_dashboard_bp
mail = Mail()

def create_app():
    app = Flask(__name__)
    config_class = get_config()
    app.config.from_object(config_class)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    cache.init_app(app)
    # mail = Mail(app)
    mail.init_app(app)

    # Register Blueprints
    app.register_blueprint(user_auth_bp, url_prefix='/api')
    app.register_blueprint(admin_auth_bp, url_prefix='/api')
    app.register_blueprint(user_dashboard_bp, url_prefix='/api')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/api')
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
