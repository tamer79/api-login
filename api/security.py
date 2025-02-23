import uuid
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from api.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from api.database import get_redis
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # Define o esquema OAuth2

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Cria um token de acesso JWT com expiração."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "exp": expire,
        "jti": str(uuid.uuid4()),  # Gera um identificador único para o token
        **data
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    """Cria um token de atualização JWT com expiração."""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    token_data = {
        "exp": expire,
        "jti": str(uuid.uuid4()),  # Gera um identificador único para o token
        **data
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

async def verify_token(token: str = Depends(oauth2_scheme)):
    """Verifica a validade de um token JWT e se está revogado."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_jti = payload.get("jti")  # Obtém o identificador do token

        if not token_jti:
            logger.warning("Token recebido sem JTI.")
            raise HTTPException(status_code=401, detail="Token inválido")

        # Obtém uma conexão segura com o Redis
        try:
            redis = await get_redis()
            if redis and await redis.exists(f"blacklist:{token_jti}"):
                logger.warning("Tentativa de uso de token revogado.")
                raise HTTPException(status_code=401, detail="Token revogado")
        except Exception as e:
            logger.error(f"Erro ao acessar Redis: {e}")
            # Se o Redis falhar, apenas logamos, mas não bloqueamos o usuário

        return payload  # Retorna o payload do token se válido

    except JWTError:
        logger.warning("Token inválido ou expirado recebido.")
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
