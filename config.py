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

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:pass@localhost:5432/dbname')
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
