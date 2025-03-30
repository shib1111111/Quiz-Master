# /app.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail  
from setup_cache import cache
from config import get_config
from model import db
from routes.admin_authentication import admin_auth_bp
from routes.admin_dashboard import admin_dashboard_bp
from routes.admin_subject import admin_subject_bp
from routes.admin_chapter import admin_chapter_bp
from routes.admin_quiz import admin_quiz_bp
from routes.admin_question import admin_question_bp
from routes.admin_summary import admin_summary_bp

from routes.user_dashboard import user_dashboard_bp
from routes.user_authentication import user_auth_bp
from routes.user_score import user_score_bp
from routes.user_payment import user_payment_bp
from routes.user_cart import user_cart_bp
from routes.user_exam_interface import user_exam_interface_bp
from routes.user_summary import user_summary_bp


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
    mail.init_app(app)

    # Register Blueprints
    app.register_blueprint(admin_auth_bp, url_prefix='/api')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/api')
    app.register_blueprint(admin_subject_bp, url_prefix='/api')
    app.register_blueprint(admin_chapter_bp, url_prefix='/api')
    app.register_blueprint(admin_quiz_bp, url_prefix='/api')
    app.register_blueprint(admin_question_bp, url_prefix='/api')
    app.register_blueprint(admin_summary_bp, url_prefix='/api')

    app.register_blueprint(user_auth_bp, url_prefix='/api')
    app.register_blueprint(user_dashboard_bp, url_prefix='/api')
    app.register_blueprint(user_score_bp, url_prefix='/api')
    app.register_blueprint(user_payment_bp, url_prefix='/api')
    app.register_blueprint(user_cart_bp, url_prefix='/api')
    app.register_blueprint(user_exam_interface_bp, url_prefix='/api')
    app.register_blueprint(user_summary_bp, url_prefix='/api')
    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
