from datetime import time
from src.models.BaseModel import BaseModel
from sqlmodel import Relationship, Field
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.Cancha import Cancha


class Horario(BaseModel, table=True):
    cancha_id: int = Field(foreign_key="cancha.id")
    disponible: bool
    hora_inicio: time
    hora_fin: time

    # CORRECCIÓN: Quitamos 'Optional' y las comillas dobles simples
    cancha: "Cancha" = Relationship(back_populates="horarios")

    # Dejamos esto comentado para asegurar que el seed corra sin problemas de ciclo
    # reservas: List["Reserva"] = Relationship(back_populates="horario")