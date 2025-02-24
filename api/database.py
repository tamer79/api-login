from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis.asyncio as aioredis  # ✅ Usando redis-py em modo assíncrono
import os
import logging

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://login:e2evfMBeP@/login?host=/cloudsql/ultimate-choir-451811-g2:us-central1:login")

# Criar o motor de conexão com PostgreSQL via Cloud SQL Auth Proxy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Criar a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Testar conexão com o banco de dados
def test_db_connection():
    try:
        with engine.connect() as conn:
            logger.info("✅ Conectado ao banco de dados com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")

# Executar teste de conexão
test_db_connection()

# Configuração do Redis
redis_client = None  # Variável global para conexão com Redis

async def get_redis():
    """Obtém uma conexão assíncrona com Redis."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = await aioredis.from_url("redis://10.102.149.123:6379", decode_responses=True)
            logger.info("✅ Conectado ao Redis com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao Redis: {e}")
            redis_client = None  # Se a conexão falhar, impede erro na aplicação

    return redis_client

def get_db():
    """Obtém uma sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
