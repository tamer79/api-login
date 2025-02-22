import os
import sys
import logging
import aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from api.routes import auth
from api.config import REDIS_URL
from api.exceptions import ErrorResponse

# Configuração da aplicação FastAPI
app = FastAPI()

# Configuração de logs detalhados
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Iniciando a API...")

# Configuração de CORS para segurança
origins = ["https://meuapp.railway.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Inicializa o Redis e o Rate Limiter
@app.on_event("startup")
async def startup():
    """Inicializa a conexão com o Redis e configura o Rate Limiter."""
    global redis
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)  # Conexão assíncrona
    await FastAPILimiter.init(redis)  # Inicializa o FastAPILimiter com Redis assíncrono
    logger.info("Redis e Rate Limiter inicializados.")

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
        content=ErrorResponse(detail=exc.detail, code=exc.status_code).dict()
    )

# Tratamento global para exceções inesperadas
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Tratamento global para exceções inesperadas."""
    logger.exception(f"Erro inesperado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Erro interno do servidor", code=500).dict()
    )

# Inclui as rotas de autenticação
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])

# Rota raiz para testes
@app.get("/")
def read_root():
    return {"message": "API funcionando na Railway!"}
