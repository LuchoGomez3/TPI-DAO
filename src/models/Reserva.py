from sqlmodel import Relationship, Field
from datetime import datetime, time
from typing import Optional
from src.models.BaseModel import BaseModel


class Reserva(BaseModel, table=True):
    cliente_id: int = Field(foreign_key="cliente.id")
    cancha_id: int = Field(foreign_key="cancha.id")
    fecha: datetime
    hora_inicio: time
    hora_fin: time

    cliente: Optional["Cliente"] = Relationship(back_populates="reservas")
    cancha: Optional["Cancha"] = Relationship(back_populates="reservas")
