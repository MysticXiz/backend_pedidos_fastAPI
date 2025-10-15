from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models.models import User
from core.dependencies import get_session, verify_token
from main import argon2_context as argon2 
from main import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.schemas import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta, timezone
from email_validator import validate_email, EmailNotValidError
import re


auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(user_id: int, token_expire_minutes: int = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    date_expiration = datetime.now(timezone.utc) + token_expire_minutes
    info = {"sub": str(user_id), "exp": date_expiration}
    encoded_jwt = jwt.encode(info, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def user_authentication(email: str, password: str, session: Session = Depends(get_session)):
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return False
    elif not argon2.verify(password, user.password):
        return False
    return user
def is_valid_email(email: str) -> bool:
    try:
        validate_email(email) 
        return True
    except EmailNotValidError:
        return False
def is_valid_password(password: str) -> bool:
    return (
        len(password) >= 8 and
        re.search(r"[A-Za-z]", password) and
        re.search(r"\d", password)
    )

@auth_router.get("/")
async def home():
    return {"message": ""}

@auth_router.post("/signup")
async def signup(user_schema: UserSchema, session: Session = Depends(get_session)):
    email = user_schema.email.strip()
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Formato de e-mail inválido.")
    if not is_valid_password(user_schema.password):
        raise HTTPException(status_code=400, detail="Senha deve ter pelo menos 8 caracteres, uma letra e um número.")

    user = session.query(User).filter_by(email=email).first()
    if user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")

    password_hashed = argon2.hash(user_schema.password)

    new_user = User(
        name=(user_schema.name or "").strip(),
        email=email,
        password=password_hashed,
        active=bool(user_schema.active),
        admin=False  # força não-admin em signup público
    )
    session.add(new_user)
    session.commit()
    return {"message": "Usuário criado com sucesso"}

@auth_router.post("/signin")
async def signin(login_schema: LoginSchema, session: Session = Depends(get_session)):
    user = user_authentication(login_schema.email.strip(), login_schema.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="E-mail ou senha inválidos!")
    access_token = create_token(user.id)
    refresh_token = create_token(user.id, timedelta(days=7))
    return {"access_token": access_token,"refresh_token": refresh_token, "token_type": "Bearer"}

@auth_router.post("/signin-test")
async def signin(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = user_authentication(form_data.username.strip(), form_data.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="E-mail ou senha inválidos!")
    access_token = create_token(user.id)
    return {"access_token": access_token, "token_type": "Bearer"}

@auth_router.post("/refresh")
async def refresh_token(current_user: User = Depends(verify_token)):
    access_token = create_token(current_user.id)
    return {"access_token": access_token, "token_type": "Bearer"}

@auth_router.post("/create-admin")
async def create_admin(user_schema: UserSchema, session: Session = Depends(get_session), current_user: User = Depends(verify_token)):
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="Acesso negado")
    email = user_schema.email.strip()
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Formato de e-mail inválido.")
    user = session.query(User).filter_by(email=email).first()
    if user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")
    if not is_valid_password(user_schema.password):
        raise HTTPException(status_code=400, detail="Senha inválida ou muito curta (mínimo 8 caracteres).")

    password_hashed = argon2.hash(user_schema.password)

    new_user = User(
        name=(user_schema.name or "").strip(),
        email=email,
        password=password_hashed,
        active=bool(user_schema.active),
        admin=True  # define como admin
    )
    session.add(new_user)
    session.commit()
    return {"message": "Usuário admin criado com sucesso"}

