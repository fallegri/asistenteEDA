from api.repositories.UserRepository import UserRepository
from api.repositories.ItemRepository import ItemRepository
from api.schemas import UserCreate, UserLogin, UserResponse, ItemCreate, ItemResponse
from api.models import User, Item
from fastapi import HTTPException
from sqlalchemy.orm import Session


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register(self, user_data: UserCreate) -> User:
        # Verificar si el email ya existe
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        
        # Crear usuario con password hasheado
        import bcrypt
        password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = self.user_repo.create(
            nombre=user_data.nombre,
            email=user_data.email,
            password_hash=password_hash,
            rol=user_data.rol
        )
        return user

    def authenticate(self, login_data: UserLogin) -> User | None:
        user = self.user_repo.get_by_email(login_data.email)
        if not user:
            return None
        
        import bcrypt
        if bcrypt.checkpw(login_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return user
        return None


class ItemService:
    def __init__(self, db: Session):
        self.item_repo = ItemRepository(db)
        self.user_repo = UserRepository(db)

    def create_item(self, item_data: ItemCreate, usuario_id: int) -> Item:
        # Verificar que el usuario existe
        user = self.user_repo.get_by_id(usuario_id)
        if not user or not user.activo:
            raise HTTPException(status_code=404, detail="Usuario no encontrado o inactivo")
        
        return self.item_repo.create(
            nombre=item_data.nombre,
            descripcion=item_data.descripcion,
            estado=item_data.estado,
            propietario_id=usuario_id
        )

    def get_user_items(self, usuario_id: int, skip: int = 0, limit: int = 100, 
                       solo_activos: bool = True) -> list[Item]:
        user = self.user_repo.get_by_id(usuario_id)
        if not user or not user.activo:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return self.item_repo.get_all(skip=skip, limit=limit, eliminado=not solo_activos)