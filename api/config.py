import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

def get_env_variable(var_name: str, default=None, required=True):
    """Obtém uma variável de ambiente e gera erro se estiver ausente."""
    value = os.getenv(var_name, default)
    if required and value is None:
        raise RuntimeError(f"⚠️ ERRO: Variável de ambiente {var_name} não definida!")
    return value

# 🔒 Segurança
SECRET_KEY = get_env_variable("SECRET_KEY", "uma-chave-secreta")
ALGORITHM = get_env_variable("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(get_env_variable("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# 🔗 Conexões Externas
DATABASE_URL = "postgresql://postgres:e2evfMBeP@34.88.45.48:5432/login"
REDIS_URL = get_env_variable("REDIS_URL", "redis://10.76.177.3:6379")

# 🔑 Credenciais OAuth
GOOGLE_CLIENT_ID = get_env_variable("GOOGLE_CLIENT_ID", "seu-google-client-id")
GOOGLE_CLIENT_SECRET = get_env_variable("GOOGLE_CLIENT_SECRET", "seu-google-client-secret")
GITHUB_CLIENT_ID = get_env_variable("GITHUB_CLIENT_ID", "seu-github-client-id")
GITHUB_CLIENT_SECRET = get_env_variable("GITHUB_CLIENT_SECRET", "seu-github-client-secret")
