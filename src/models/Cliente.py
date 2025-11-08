from typing import List, Optional
from sqlmodel import Relationship

from src.models.BaseModel import BaseModel
from src.models.Reserva import Reserva


class Cliente(BaseModel, table=True):
    nombre: str
    apellido: str
    telefono: str
    email: str

    reservas: Optional[List["Reserva"]] = Relationship(back_populates="cliente")
