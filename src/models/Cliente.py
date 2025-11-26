from typing import List, Optional
from sqlmodel import Relationship

from src.models.BaseModel import BaseModel
# Nota: Si da error de importación circular, usa TYPE_CHECKING como en Cancha.py,
# pero por ahora probemos manteniendo tu estructura simple.
from src.models.Reserva import Reserva

class Cliente(BaseModel, table=True):
    nombre: str
    apellido: str
    telefono: str
    email: str

    # CORRECCIÓN: Eliminamos Optional[]
    reservas: List["Reserva"] = Relationship(back_populates="cliente")