from src.models.BaseModel import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlmodel import Relationship, SQLModel, Field


class CanchaTorneoLink(SQLModel, table=True):
    cancha_id: int = Field(foreign_key="cancha.id", primary_key=True)
    torneo_id: int = Field(foreign_key="torneo.id", primary_key=True)

class Torneo(BaseModel, table=True):
    nombre: str
    fecha_inicio: datetime
    fecha_fin: datetime
    descripcion: Optional[str] = None

    canchas: List["Cancha"] = Relationship(
        back_populates="torneos",
        link_model=CanchaTorneoLink
    )

