import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def validate_database_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# Configuraciones adicionales para psycopg2
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'pass')
DB_NAME = os.getenv('DB_NAME', 'dbname')

# Construir DATABASE_URL de forma más segura
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

if not validate_database_url(DATABASE_URL):
    raise ValueError(f"DATABASE_URL inválida: {DATABASE_URL}")

MAX_RETRIES = int(os.getenv('DB_MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('DB_RETRY_DELAY', '5'))
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '10'))

# Nuevas configuraciones
SSL_MODE = os.getenv('DB_SSL_MODE', 'prefer')
SSL_CERT_PATH = os.getenv('DB_SSL_CERT_PATH')
CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '30'))

# DNS y timeouts
DB_DNS_CACHE_TTL = int(os.getenv('DB_DNS_CACHE_TTL', '300'))
DB_STATEMENT_TIMEOUT = int(os.getenv('DB_STATEMENT_TIMEOUT', '30000'))
DB_COMMAND_TIMEOUT = int(os.getenv('DB_COMMAND_TIMEOUT', '30'))

# Railway specific settings
PORT = int(os.getenv('PORT', '8000'))
RAILWAY_ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT', 'development')

# Adjust SSL mode for Railway
if RAILWAY_ENVIRONMENT == 'production':
    SSL_MODE = 'require'
    
# Use Railway's DATABASE_URL if available
if os.getenv('RAILWAY_STATIC_URL'):
    DATABASE_URL = os.getenv('DATABASE_URL')
