from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    rol: Optional[str] = Field(default="user", max_length=50)


class UserUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[str] = Field(default=None, min_length=1, max_length=255)
    rol: Optional[str] = Field(default=None, max_length=50)
    activo: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool
    creado_en: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)