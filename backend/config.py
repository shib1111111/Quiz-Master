# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False

    # General Config
    try:
        SECRET_KEY = os.environ["SECRET_KEY"]
        SECURITY_PASSWORD_SALT = os.environ["SECURITY_PASSWORD_SALT"]
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")

    # Database
    try:
        SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
        SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "false").lower() == "true"
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")

    # JWT Authentication
    try:
        JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
        JWT_TOKEN_LOCATION = os.getenv("JWT_TOKEN_LOCATION", ["headers"])
        JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
        JWT_HEADER_NAME = os.getenv("JWT_HEADER_NAME", "Authorization")
        JWT_HEADER_TYPE = os.getenv("JWT_HEADER_TYPE", "Bearer")
        JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 7200))  # Default: 2 hour
        JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 86400))  # Default: 1 day
        JWT_COOKIE_CSRF_PROTECT = os.getenv("JWT_COOKIE_CSRF_PROTECT")
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")


    # Redis Cache
    try:
        CACHE_TYPE = os.environ["CACHE_TYPE"]
        CACHE_REDIS_HOST = os.environ["CACHE_REDIS_HOST"]
        CACHE_REDIS_PORT = int(os.getenv("CACHE_REDIS_PORT", 6379))
        CACHE_REDIS_DB = int(os.getenv("CACHE_REDIS_DB", 3))
        CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL")
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")

    # Celery Config
    try:
        CELERY_BROKER_URL = os.environ["CELERY_BROKER_URL"]
        CELERY_RESULT_BACKEND = os.environ["CELERY_RESULT_BACKEND"]
        CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "UTC")
        CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = os.getenv("CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP", "true").lower() == "true"
        
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")

    try:
        # Flask-Mail configuration
        MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
        MAIL_PORT = int(os.getenv('MAIL_PORT', 25))
        MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'False').lower() in ['true', '1', 't']
        MAIL_USERNAME = os.getenv('MAIL_USERNAME')
        MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
        SENDER_MAIL = os.getenv('SENDER_MAIL')
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")
    
    try:
        # Google Chat Webhook URL
        GOOGLE_CHAT_WEBHOOK_URL = os.getenv("GOOGLE_CHAT_WEBHOOK_URL")
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")
    
    try:
        # Frontend URL for CORS
        FRONTEND_URL = os.getenv("FRONTEND_URL")
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")
    
    try:
        # STRIPE Payment Gateway
        STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
        STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    except KeyError as e:
        raise KeyError(f"Missing required environment variable: {e}")
        

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    WTF_CSRF_ENABLED = True  

# Configuration selector based on environment
def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig
