from fastapi import FastAPI
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

argon2_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/signin-test")

from routes.orders import orders_router
from routes.auth import auth_router


routes = [auth_router, orders_router]

for route in routes:
    app.include_router(route)
