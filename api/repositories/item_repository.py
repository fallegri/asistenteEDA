from sqlalchemy.orm import Session
from api.models import Item
from typing import Optional, List


class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Item:
        db_item = Item(**kwargs)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def get_by_id(self, item_id: int) -> Optional[Item]:
        return self.db.query(Item).filter(Item.id == item_id, Item.eliminado == False).first()

    def list_all(self) -> List[Item]:
        return self.db.query(Item).filter(Item.eliminado == False).all()

    def update(self, item: Item, **kwargs) -> Item:
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def soft_delete(self, item: Item) -> Item:
        item.eliminado = True
        self.db.commit()
        self.db.refresh(item)
        return item