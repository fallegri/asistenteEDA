import os
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from api.repositories.user_repository import UserRepository
from api.models import User
from fastapi import HTTPException


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.secret_key = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 1440  # 24h

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def register(self, nombre: str, email: str, password: str) -> dict:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=400, detail="Credenciales inválidas")
        
        password_hash = self.hash_password(password)
        user = self.user_repo.create(nombre=nombre, email=email, password_hash=password_hash)
        
        token = self.create_access_token({"sub": user.email})
        return {
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "rol": user.rol,
                "activo": user.activo
            },
            "token": token
        }

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not self.verify_password(password, user.password_hash):
            # Incrementar intentos fallidos
            if user:
                user.intentos_fallidos = (user.intentos_fallidos or 0) + 1
                if user.intentos_fallidos >= 5:
                    user.activo = False
                # En un caso real, guardaríamos con repo
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Reset intentos fallidos
        user.intentos_fallidos = 0
        
        token = self.create_access_token({"sub": user.email})
        return {
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "rol": user.rol,
                "activo": user.activo
            },
            "token": token
        }

    def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if not email:
                raise HTTPException(status_code=401, detail="Credenciales inválidas")
        except JWTError:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        user = self.user_repo.get_by_email(email)
        if not user or not user.activo:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        return user