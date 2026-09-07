from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    rol: Optional[str] = Field(default="user", max_length=50)

    @validator("email")
    def validar_email(cls, v):
        if "@" not in v:
            raise ValueError("Email inválido")
        return v


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool
    creado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)


# Item schemas
class ItemCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(default=None)
    estado: Optional[str] = Field(default="active")


class ItemResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    estado: str
    eliminado: bool
    creado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


# Analysis schemas
class AnalysisRequest(BaseModel):
    file_format: str = Field(..., pattern="^(xlsx|csv)$")
    method: str = Field(..., pattern="^(mediana|media|agrupada|knn)$")


class AnalysisResponse(BaseModel):
    file_reference: str
    initial_metrics: dict
    new_metrics: dict
    download_url: str


# Imputation schemas
class ImputationRequest(BaseModel):
    file_reference: str = Field(..., min_length=1)
    method: str = Field(..., pattern="^(mediana|media|agrupada|knn)$")
    params: dict = Field(default={})


class ImputationResponse(BaseModel):
    file_reference: str
    new_metrics: dict
    download_url: str
    message: str