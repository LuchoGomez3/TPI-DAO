from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from src.models.BaseModel import BaseModel

if TYPE_CHECKING:
    from src.models.Reserva import Reserva


class EstadoPago(SQLModel, table=True):
    __tablename__ = "estado_pago"

    id: int = Field(default=None, primary_key=True, index=True)
    nombre: str

    pagos: List["Pago"] = Relationship(back_populates="estado_pago")


class Pago(BaseModel, table=True):
    __tablename__ = "pago"

    reserva_id: int = Field(foreign_key="reserva.id")
    estado_pago_id: int = Field(foreign_key="estado_pago.id")
    monto: float
    fecha_pago: datetime

    reserva: "Reserva" = Relationship(back_populates="pago")
    estado_pago: "EstadoPago" = Relationship(back_populates="pagos")