from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuração do banco de dados
DATABASE_URL = "postgresql://postgres:ZkwJXjxSeeRbgewdfgilpMmxXKUDpBDD@postgres.railway.internal:5432/lili"

# Criar o motor de conexão
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Criar a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Testar conexão com o banco de dados
def test_db_connection():
    try:
        with engine.connect() as conn:
            print("✅ Conectado ao banco de dados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")

# Executar teste de conexão
test_db_connection()
