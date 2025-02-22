from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from api.database import get_db
from api.oauth import oauth
from api.models import User
from api.security import create_access_token, verify_password
from api.exceptions import ErrorResponse
import logging

router = APIRouter()

# Configuração do Logger
logger = logging.getLogger(__name__)

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """Processa login e retorna token de acesso."""
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    logger.info(f"Tentativa de login para {email}")

    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"Falha de login para {email}")
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    logger.info(f"Login bem-sucedido para {email}")
    
    return {"access_token": access_token}

@router.get("/login/google")
async def login_google(request: Request):
    """Redireciona o usuário para a página de login do Google."""
    try:
        redirect_uri = request.url_for("auth_google_callback")
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Erro ao redirecionar para Google OAuth: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar autenticação com Google")

@router.get("/login/google/callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    """Processa o callback do Google e autentica o usuário."""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = await oauth.google.parse_id_token(request, token)
        
        if not user_info:
            logger.warning("Falha ao obter informações do Google.")
            raise HTTPException(status_code=400, detail="Falha na autenticação com o Google")
        
        email = user_info["email"]
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            user = User(email=email, hashed_password="oauth_user")
            db.add(user)
            db.commit()
            logger.info(f"Novo usuário criado via Google OAuth: {email}")

        access_token = create_access_token(data={"sub": email})
        logger.info(f"Login via Google bem-sucedido para {email}")

        return {"access_token": access_token}

    except Exception as e:
        logger.error(f"Erro ao autenticar com Google: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar login com Google")

@router.get("/login/github")
async def login_github(request: Request):
    """Redireciona o usuário para a página de login do GitHub."""
    try:
        redirect_uri = request.url_for("auth_github_callback")
        return await oauth.github.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Erro ao redirecionar para GitHub OAuth: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar autenticação com GitHub")

@router.get("/login/github/callback")
async def auth_github_callback(request: Request, db: Session = Depends(get_db)):
    """Processa o callback do GitHub e autentica o usuário."""
    try:
        token = await oauth.github.authorize_access_token(request)
        user_info = await oauth.github.get("user", token=token)
        
        if not user_info:
            logger.warning("Falha ao obter informações do GitHub.")
            raise HTTPException(status_code=400, detail="Falha na autenticação com o GitHub")

        email = user_info.json().get("email")
        if not email:
            logger.warning("O GitHub não retornou um email válido.")
            raise HTTPException(status_code=400, detail="O GitHub não retornou um email válido")

        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            user = User(email=email, hashed_password="oauth_user")
            db.add(user)
            db.commit()
            logger.info(f"Novo usuário criado via GitHub OAuth: {email}")

        access_token = create_access_token(data={"sub": email})
        logger.info(f"Login via GitHub bem-sucedido para {email}")

        return {"access_token": access_token}

    except Exception as e:
        logger.error(f"Erro ao autenticar com GitHub: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar login com GitHub")
