from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Relationship, Field, SQLModel
from src.models.Torneo import CanchaTorneoLink
from enum import Enum
from src.models.BaseModel import BaseModel

if TYPE_CHECKING:
    from src.models.Horario import Horario
    from src.models.Reserva import Reserva
    from src.models.Busquedas import Servicio
    from src.models.Torneo import Torneo

class TipoDeCancha(Enum):
    FUTBOL = "Futbol"
    TENIS = "Tennis"
    PADEL = "Padel"
    VOLEY = "Voley"

class Cancha(BaseModel, table=True):
    __tablename__ = "cancha"
    
    nombre: str
    tipo_cancha_id: int = Field(foreign_key="tipo_cancha.id")

    horarios: Optional[List["Horario"]] = Relationship(back_populates="cancha")
    reservas: Optional[List["Reserva"]] = Relationship(back_populates="cancha")
    servicios: Optional[List["Servicio"]] = Relationship(back_populates="cancha")
    torneos: Optional[List["Torneo"]] = Relationship(
        back_populates="canchas",
        link_model=CanchaTorneoLink
    ) 

class TipoCancha(SQLModel, table=True):
    __tablename__ = "tipo_cancha"
    
    id: int = Field(default=None, primary_key=True, index=True)
    nombre: TipoDeCancha
    descripcion: str