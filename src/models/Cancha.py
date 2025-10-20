from typing import Optional, List
from sqlmodel import Relationship
from src.models.Torneo import CanchaTorneoLink

from src.models.BaseModel import BaseModel


class Cancha(BaseModel, table=True):
    nombre: str
    tipo: str
    iluminacion: bool = False
    servicios_adicionales: Optional[str] = None

    horarios: List["Horario"] = Relationship(back_populates="cancha")
    reservas: List["Reserva"] = Relationship(back_populates="cancha")

    torneos: List["Torneo"] = Relationship(
        back_populates="canchas",
        link_model=CanchaTorneoLink
    )
