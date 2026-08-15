import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

env_mode = os.environ.get('FLASK_ENV', os.environ.get('ENV', 'development')).lower()
is_production = env_mode in ['production', 'prod']

secret_key = os.environ.get('SECRET_KEY')
if is_production and not secret_key:
    raise RuntimeError(
        "CRITICAL SECURITY ERROR: SECRET_KEY environment variable must be set in production mode. "
        "Please configure a strong, unpredictable SECRET_KEY."
    )


class Config:
    # Environment-backed secret key; uses local development fallback only in non-production mode
    SECRET_KEY = secret_key or 'nutristar-dev-only-secret-key-local-environment'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'nutristar.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = not is_production

    # Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = is_production or os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ['true', '1', 't']
