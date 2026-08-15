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

# Auto-detect Render cloud environment hostname
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_host:
    render_host_clean = render_host.strip().lower()
    if render_host_clean not in trusted_hosts:
        trusted_hosts.append(render_host_clean)
    if '*.onrender.com' not in trusted_hosts:
        trusted_hosts.append('*.onrender.com')

# Default fallback list for trusted hosts
if not trusted_hosts:
    if os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID'):
        trusted_hosts = ['*.onrender.com', 'localhost', '127.0.0.1']
    elif not is_production:
        trusted_hosts = ['localhost', '127.0.0.1']
    else:
        # In generic production without TRUSTED_HOSTS specified, default to wildcard to prevent deployment crash
        trusted_hosts = ['*']


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

    # Trusted Hosts validation (supports wildcards, *.onrender.com, custom domains, and localhost)
    TRUSTED_HOSTS = trusted_hosts
