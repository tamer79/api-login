import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# URL do Banco de Dados na Railway
DATABASE_URL = "postgresql://postgres:ZkwJXjxSeeRbgewdfgilpMmxXKUDpBDD@postgres.railway.internal:5432/lili"

# URL do Redis na Railway
REDIS_URL = os.getenv("REDIS_URL", "redis://default:redispw@redis.railway.internal:6379")

# Credenciais OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "seu-google-client-id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "seu-google-client-secret")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "seu-github-client-id")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "seu-github-client-secret")
