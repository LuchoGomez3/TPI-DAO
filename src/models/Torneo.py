from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel, select, Session
from datetime import datetime
from pydantic import model_validator, field_validator
from src.models.BaseModel import BaseModel

if TYPE_CHECKING:
    from src.models.Cancha import Cancha


# Tabla intermedia (Link)
class CanchaTorneoLink(SQLModel, table=True):
    cancha_id: int = Field(foreign_key="cancha.id", primary_key=True)
    torneo_id: int = Field(foreign_key="torneo.id", primary_key=True)


class Torneo(BaseModel, table=True):
    __tablename__ = "torneo"

    nombre: str = Field(..., min_length=3, max_length=100)
    fecha_inicio: datetime
    fecha_fin: datetime
    descripcion: Optional[str] = None

    canchas: List["Cancha"] = Relationship(back_populates="torneos", link_model=CanchaTorneoLink)

    # ================= VALIDACIÓN 1: FECHAS COHERENTES =================
    @model_validator(mode='after')
    def validar_fechas_logicas(self):
        if self.fecha_inicio >= self.fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin.")
        return self

    # ================= VALIDACIÓN 2: NOMBRE ÚNICO (CONTRA BD) =================
    @field_validator("nombre")
    @classmethod
    def validar_nombre_unico(cls, v: str):
        nombre_limpio = v.strip().title()

        # Importación diferida
        from database import engine

        with Session(engine) as session:
            # Buscamos si ya existe un torneo con ese nombre exacto
            existente = session.exec(
                select(cls).where(cls.nombre == nombre_limpio)
            ).first()

            if existente:
                raise ValueError(f"Ya existe un torneo llamado '{nombre_limpio}'.")

        return nombre_limpio