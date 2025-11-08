from sqlmodel import SQLModel, Field, Relationship
from typing import List
from src.models.Reserva import Reserva


class Servicio(SQLModel, table=True):
    __tablename__ = "servicio"
    
    id: int = Field(default=None, primary_key=True, index=True)
    nombre: str
    costo: float
    
    reservas: List["Reserva"] = Relationship(back_populates="servicios")
    
class ReservaServicio(SQLModel, table=True):
    __tablename__ = "reserva_servicio"
    
    id: int = Field(default=None, primary_key=True, index=True)
    reserva_id: int = Field(foreign_key="reserva.id")
    servicio_id: int = Field(foreign_key="servicio.id")
    
    reserva: "Reserva" = Relationship(back_populates="reserva_servicios")
    servicio: "Servicio" = Relationship(back_populates="reserva_servicios")
    