from sqlalchemy.orm import Session
from api.repositories.item_repository import ItemRepository
from api.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from api.models import Item
from fastapi import HTTPException


class ItemService:
    def __init__(self, db: Session):
        self.repo = ItemRepository(db)

    def create(self, data: ItemCreate) -> ItemResponse:
        if not data.nombre or not data.nombre.strip():
            raise ValueError("El nombre es obligatorio")
        
        item = self.repo.create(
            nombre=data.nombre.strip(),
            descripcion=data.descripcion,
            estado=data.estado or "active"
        )
        return ItemResponse.model_validate(item)

    def get_by_id(self, item_id: int) -> ItemResponse | None:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item no encontrado")
        return ItemResponse.model_validate(item)

    def list_all(self) -> list[ItemResponse]:
        return [ItemResponse.model_validate(item) for item in self.repo.list_all()]

    def update(self, item_id: int, data: ItemUpdate) -> ItemResponse | None:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item no encontrado")
        
        update_data = data.model_dump(exclude_unset=True)
        if "nombre" in update_data and not update_data["nombre"].strip():
            raise ValueError("El nombre no puede estar vacío")
        
        updated_item = self.repo.update(item, **update_data)
        return ItemResponse.model_validate(updated_item)

    def delete(self, item_id: int) -> bool:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item no encontrado")
        self.repo.soft_delete(item)
        return True