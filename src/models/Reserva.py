from sqlmodel import Relationship, Field, SQLModel
from datetime import datetime, time
from typing import Optional, List, TYPE_CHECKING
from src.models.BaseModel import BaseModel
from enum import Enum

from src.models.Busquedas import Servicio, ReservaServicio

if TYPE_CHECKING:
    from src.models.Cliente import Cliente
    from src.models.Cancha import Cancha
    from src.models.Horario import Horario
    from src.models.Pago import Pago


class EstadoReserva(SQLModel, table=True):
    __tablename__ = "estado_reserva"

    id: int = Field(default=None, primary_key=True, index=True)
    nombre: str

    reservas: List["Reserva"] = Relationship(back_populates="estado_reserva")


class Reserva(BaseModel, table=True):
    __tablename__ = "reserva"

    cliente_id: int = Field(foreign_key="cliente.id")
    cancha_id: int = Field(foreign_key="cancha.id")
    estado_reserva_id: int = Field(foreign_key="estado_reserva.id")
    horario_id: int = Field(foreign_key="horario.id")
    fecha: datetime
    hora_inicio: time
    hora_fin: time

    cliente: "Cliente" = Relationship(back_populates="reservas")
    cancha: "Cancha" = Relationship(back_populates="reservas")
    estado_reserva: "EstadoReserva" = Relationship(back_populates="reservas")

    horario: "Horario" = Relationship()

    servicios: List["Servicio"] = Relationship(back_populates="reservas", link_model=ReservaServicio)

    pago: Optional["Pago"] = Relationship(back_populates="reserva")