import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from api.routes import auth
from api.config import REDIS_URL
from api.database import get_redis  # Usa a conexão correta do Redis
from api.exceptions import ErrorResponse

# Configuração de logs detalhados
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Iniciando a API...")

# Configuração de CORS para segurança
origins = ["https://meuapp.railway.app"]

# Novo sistema de ciclo de vida da aplicação (lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida do aplicativo FastAPI"""
    logger.info("Inicializando recursos da API...")
    
    redis = await get_redis()  # Obtém a conexão corretamente
    await FastAPILimiter.init(redis)
    logger.info("Redis e Rate Limiter inicializados.")

    yield  # Permite que a API funcione

    # Finalização dos recursos
    if redis:
        await redis.close()
        logger.info("Conexão com o Redis fechada.")

# Configuração da aplicação FastAPI
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Middleware para forçar HTTPS
@app.middleware("http")
async def force_https(request: Request, call_next):
    """Garante que a API só seja acessada via HTTPS em produção."""
    if request.url.scheme != "https" and "railway.app" in request.url.hostname:
        return JSONResponse(status_code=403, content={"message": "Use HTTPS para acessar esta API."})
    return await call_next(request)

# Tratamento padronizado de erros HTTP
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Tratamento padronizado de erros HTTP."""
    logger.error(f"Erro HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail, code=exc.status_code).model_dump()  # 🔥 Corrigido `.dict()`
    )

# Tratamento global para exceções inesperadas
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Tratamento global para exceções inesperadas."""
    logger.exception(f"Erro inesperado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Erro interno do servidor", code=500).model_dump()  # 🔥 Corrigido `.dict()`
    )

# Inclui as rotas de autenticação
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])

# Rota raiz para testes
@app.get("/")
def read_root():
    return {"message": "API funcionando na Railway!"}
