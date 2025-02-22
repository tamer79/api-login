from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
import logging
import sys
import os
from api.routes import auth
from api.config import REDIS_URL
from api.exceptions import ErrorResponse
import logging

# Configuração de logs detalhados
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Iniciando a API...")


app = FastAPI()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Middleware CORS
origins = ["https://meuapp.railway.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.on_event("startup")
async def startup():
    """Inicializa o Redis e o Rate Limiter."""
    redis = Redis.from_url(REDIS_URL, decode_responses=True)
    await FastAPILimiter.init(redis)
    logger.info("Redis e Rate Limiter inicializados.")

@app.middleware("http")
async def force_https(request: Request, call_next):
    """Garante que a API só seja acessada via HTTPS em produção."""
    if "https" not in request.url.scheme and "railway.app" in request.url.hostname:
        return JSONResponse(status_code=403, content={"message": "Use HTTPS para acessar esta API."})
    return await call_next(request)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Tratamento padronizado de erros HTTP."""
    logger.error(f"Erro HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail, code=exc.status_code).dict()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Tratamento global para exceções inesperadas."""
    logger.exception(f"Erro inesperado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Erro interno do servidor", code=500).dict()
    )

app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])

@app.get("/")
def read_root():
    return {"message": "API funcionando na Railway!"}
