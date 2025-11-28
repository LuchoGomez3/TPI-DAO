from datetime import time
from src.models.BaseModel import BaseModel
from sqlmodel import Relationship, Field
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.Cancha import Cancha


class Horario(BaseModel, table=True):
    cancha_id: int = Field(foreign_key="cancha.id", nullable=False)
    disponible: bool = True
    hora_inicio: time
    hora_fin: time

    cancha: "Cancha" = Relationship(back_populates="horarios")
