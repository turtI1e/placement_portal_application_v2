import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = (os.environ.get('SECRET_KEY') or 'hard-to-guess-string').strip()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'placement.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT settings
    JWT_SECRET_KEY = '6f8c4b9a2d1e5f7a3c8b0d9e2f4a6c8e1b3d5f7a9c0e2b4d6'
    print("Loaded JWT_SECRET_KEY length:", len(JWT_SECRET_KEY))  # Debug
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Redis & Celery
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # Cache
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300

    # Upload folder
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads', 'resumes')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Email settings (from env)
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@placement.com')

    # Google Chat webhook
    GOOGLE_CHAT_WEBHOOK = os.environ.get('GOOGLE_CHAT_WEBHOOK')
