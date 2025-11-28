from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Relationship, Field, SQLModel, select, Session
from pydantic import field_validator
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

    id: Optional[int] = Field(default=None, primary_key=True, index=True)  # Corregido type hint a Optional[int]
    nombre: str = Field(..., min_length=2, max_length=20, unique=True)
    descripcion: str = Field(..., min_length=2, max_length=250)

    canchas: List["Cancha"] = Relationship(back_populates="tipo_cancha")


class Cancha(BaseModel, table=True):
    __tablename__ = "cancha"

    # Quitamos unique=True de aquí si queremos controlar el mensaje de error nosotros con el validador,
    # aunque dejarlo como respaldo (doble seguridad) es buena práctica.
    nombre: str = Field(..., min_length=2, max_length=20)
    tipo_cancha_id: int = Field(foreign_key="tipo_cancha.id")

    tipo_cancha: "TipoCancha" = Relationship(back_populates="canchas")

    horarios: List["Horario"] = Relationship(back_populates="cancha",
                                             sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    reservas: List["Reserva"] = Relationship(back_populates="cancha",
                                             sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    torneos: List["Torneo"] = Relationship(
        back_populates="canchas",
        link_model=CanchaTorneoLink,
        sa_relationship_kwargs={"cascade": "all"}
    )

    # ================= VALIDACIÓN DE UNICIDAD =================
    @field_validator("nombre")
    @classmethod
    def validar_nombre_unico(cls, v: str):
        nombre_limpio = v.strip().title()

        # 2. Importación DIFERIDA para evitar Circular Import

        from database import engine

        # 3. Consulta a la BD
        with Session(engine) as session:
            # Buscamos si existe alguna cancha con EXACTAMENTE este nombre
            statement = select(cls).where(cls.nombre == nombre_limpio)
            existente = session.exec(statement).first()

            # 4. Si existe, lanzamos error
            if existente:

                raise ValueError(f"Ya existe una cancha llamada '{nombre_limpio}'.")

        return nombre_limpio