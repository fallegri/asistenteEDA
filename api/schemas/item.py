from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ItemCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    estado: Optional[str] = Field(default="active")


class ItemUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    estado: Optional[str] = None


class ItemResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    estado: str
    eliminado: bool
    creado_en: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)