import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException
from api.schemas import UserLogin
from api.repositories.UserRepository import UserRepository
from api.database import get_db
from sqlalchemy.orm import Session


SECRET_KEY = "tu-secret-key-cambiardesarrollo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthSecurity:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def hash_password(self, password: str) -> str:
        """Hashear password según OWASP A02 - never store plain text"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar password contra hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """Crear token JWT para autenticación segura"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def authenticate_user(self, email: str, password: str, db: Session) -> User | None:
        """Autenticar usuario con verificación de password hasheado"""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if self.verify_password(password, user.password_hash):
            return user
        return None

    def get_current_user(self, token: str, db: Session) -> User:
        """Obtener usuario actual del token JWT (OWASP A01/A02)"""
        credentials_exception = HTTPException(
            status_code=401,
            detail="No se pudo validar la autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = self.user_repo.get_by_email(email)
        if user is None:
            raise credentials_exception
        return user