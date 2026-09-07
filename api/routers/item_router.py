from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import get_db
from api.services.item_service import ItemService
from api.services.auth_service import AuthService
from api.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from api.routers.auth_router import get_current_user


router = APIRouter(prefix="/items", tags=["items"])


def get_item_service(db: Session = Depends(get_db)) -> ItemService:
    return ItemService(db)


@router.get("/", response_model=list[ItemResponse])
async def list_items(
    item_service: ItemService = Depends(get_item_service),
    current_user = Depends(get_current_user)
):
    return item_service.list_all()


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    item_service: ItemService = Depends(get_item_service),
    current_user = Depends(get_current_user)
):
    return item_service.create(item_data)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    item_service: ItemService = Depends(get_item_service),
    current_user = Depends(get_current_user)
):
    return item_service.get_by_id(item_id)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    item_service: ItemService = Depends(get_item_service),
    current_user = Depends(get_current_user)
):
    return item_service.update(item_id, item_data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    item_service: ItemService = Depends(get_item_service),
    current_user = Depends(get_current_user)
):
    item_service.delete(item_id)
    return None