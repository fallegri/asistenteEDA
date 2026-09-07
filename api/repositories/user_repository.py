from sqlalchemy.orm import Session
from api.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, nombre: str, email: str, password_hash: str, rol: str = "user") -> User:
        db_user = User(nombre=nombre, email=email, password_hash=password_hash, rol=rol)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).filter(User.activo == True).offset(skip).limit(limit).all()

    def soft_delete(self, user_id: int) -> User | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.activo = False
            self.db.commit()
            self.db.refresh(user)
        return user