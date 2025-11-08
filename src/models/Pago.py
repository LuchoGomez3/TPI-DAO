from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from src.models.Reserva import Reserva
from enum import Enum

class EstadoPago(Enum):
    PENDIENTE = "Pendiente"
    COBRADO = "Cobrado"

class Pago(SQLModel, table=True):
    __tablename__ = "pago"
    
    id: int = Field(default=None, primary_key=True, index=True)
    reserva_id: int = Field(foreign_key="reserva.id")
    estado_pago_id: int = Field(foreign_key="estado_pago.id")
    monto: float
    fecha_pago: datetime
    
    reserva: "Reserva" = Relationship(back_populates="pagos")
    estado_pago: "EstadoPago" = Relationship(back_populates="pagos")
    
class EstadoPago(SQLModel, table=True):
    __tablename__ = "estado_pago"
    
    id: int = Field(default=None, primary_key=True, index=True)
    nombre: EstadoPago
    