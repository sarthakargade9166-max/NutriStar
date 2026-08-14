import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'nutristar-secure-default-key')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB limit for request body
    JSON_SORT_KEYS = False
