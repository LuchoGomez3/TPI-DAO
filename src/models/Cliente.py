from typing import List, Optional
from sqlmodel import Field, Relationship
from pydantic import EmailStr, field_validator

from src.models.BaseModel import BaseModel
from src.models.Reserva import Reserva

class Cliente(BaseModel, table=True):
    nombre: str = Field(..., min_length=2, max_length=50)
    apellido: str = Field(..., min_length=2, max_length=50)
    telefono: str = Field(..., min_length=8, max_length=15)
    email: str = Field(..., min_length=10, max_length=150, unique=True)

    reservas: List["Reserva"] = Relationship(back_populates="cliente")
    
    @field_validator("nombre")
    @classmethod
    def validar_sin_numeros(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError("El nombre no puede contener números")
        return v
    
    @field_validator("apellido")
    @classmethod
    def validar_sin_numeros_apellido(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError("El apellido no puede contener números")
        return v
    
    @field_validator("email")
    @classmethod
    def validar_email(cls, v):
        if not EmailStr.validate(v):
            raise ValueError("El email no es válido")
        return v
    
    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: str):
        if not v.isdigit() or len(v) < 8 or len(v) > 15:
            raise ValueError("El teléfono debe ser un número entre 8 y 15 dígitos")
        return v
    