from datetime import time
from src.models.BaseModel import BaseModel
from src.models.Cancha import Cancha
from sqlmodel import Relationship, Field
from typing import Optional


class Horario(BaseModel, table=True):
    cancha_id: int = Field(foreign_key="cancha.id")
    hora_inicio: time
    hora_fin: time

    cancha: Optional["Cancha"] = Relationship(back_populates="horarios")
