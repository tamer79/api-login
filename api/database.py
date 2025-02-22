from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from api.config import DATABASE_URL, REDIS_URL
import redis.asyncio as redis  # 🚀 Substituí aioredis por redis.asyncio

engine = create_engine(DATABASE_URL, poolclass=QueuePool, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# 🔥 NOVA IMPLEMENTAÇÃO DO REDIS USANDO redis.asyncio
# -------------------------------
redis_client = None  # Variável global para armazenar a conexão Redis

async def init_redis():
    """Inicializa e retorna a conexão com o Redis usando redis.asyncio."""
    return redis.from_url(REDIS_URL, decode_responses=True)

async def get_redis():
    """Obtém a conexão com o Redis, inicializando se necessário."""
    global redis_client
    if redis_client is None:
        redis_client = await init_redis()
    return redis_client
