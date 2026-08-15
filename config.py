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

trusted_hosts_raw = os.environ.get('TRUSTED_HOSTS', '').strip()
trusted_hosts = [h.strip().lower() for h in trusted_hosts_raw.split(',') if h.strip()]

if is_production and not trusted_hosts:
    raise RuntimeError(
        "CRITICAL SECURITY ERROR: TRUSTED_HOSTS environment variable must be configured in production mode. "
        "Provide a comma-separated list of allowed hostnames (e.g. TRUSTED_HOSTS=nutristar.app,www.nutristar.app)."
    )


class Config:
    # Environment-backed secret key; uses local development fallback only in non-production mode
    SECRET_KEY = secret_key or 'nutristar-dev-only-secret-key-local-environment'
    raw_db = os.environ.get('DATABASE_URL')
    default_sqlite_path = os.path.join(BASE_DIR, 'instance', 'nutristar.db').replace('\\', '/')
    if not raw_db or raw_db in ['sqlite:///instance/nutristar.db', 'sqlite:///nutristar.db']:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{default_sqlite_path}"
    else:
        SQLALCHEMY_DATABASE_URI = raw_db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = not is_production

    # Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = is_production or os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ['true', '1', 't']

    # Trusted Hosts validation (strict in production; defaults to localhost/127.0.0.1 in dev)
    TRUSTED_HOSTS = trusted_hosts if (is_production or trusted_hosts) else ['localhost', '127.0.0.1']
