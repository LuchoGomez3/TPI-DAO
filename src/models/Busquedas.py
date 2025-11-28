from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.Reserva import Reserva


class ReservaServicio(SQLModel, table=True):
    __tablename__ = "reserva_servicio"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    reserva_id: int = Field(foreign_key="reserva.id")
    servicio_id: int = Field(foreign_key="servicio.id")


class Servicio(SQLModel, table=True):
    __tablename__ = "servicio"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nombre: str
    costo: float

    reservas: List["Reserva"] = Relationship(back_populates="servicios", link_model=ReservaServicio)