from __future__ import annotations
from datetime import time
from src.models.BaseModel import BaseModel
from sqlmodel import Relationship, Field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.Cancha import Cancha

class Horario(BaseModel, table=True):
    cancha_id: int = Field(foreign_key="cancha.id")
    disponible: bool
    hora_inicio: time
    hora_fin: time

    cancha: Optional["Cancha"] = Relationship(back_populates="horarios")
    reservas: List["Reserva"] = Relationship(back_populates="horario")
