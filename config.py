import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # Authentication
    APP_PASSWORD = os.getenv('APP_PASSWORD', 'caregiver123')

    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/caregivers.db')

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # Application Settings
    MAX_SEARCH_RADIUS_MILES = 15
    MAX_OVERTIME_HOURS = 10
