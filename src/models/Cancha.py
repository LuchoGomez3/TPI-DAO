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


class TipoCancha(SQLModel, table=True):
    __tablename__ = "tipo_cancha"

    id: int = Field(default=None, primary_key=True, index=True)
    nombre: str
    descripcion: str

    canchas: List["Cancha"] = Relationship(back_populates="tipo_cancha")


class Cancha(BaseModel, table=True):
    __tablename__ = "cancha"

    nombre: str
    tipo_cancha_id: int = Field(foreign_key="tipo_cancha.id")

    tipo_cancha: "TipoCancha" = Relationship(back_populates="canchas")

    horarios: List["Horario"] = Relationship(back_populates="cancha", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    reservas: List["Reserva"] = Relationship(back_populates="cancha", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    torneos: List["Torneo"] = Relationship(
        back_populates="canchas",
        link_model=CanchaTorneoLink,
        sa_relationship_kwargs={"cascade": "all"}
    )