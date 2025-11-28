from datetime import time
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Relationship, Field, select, Session, and_
from pydantic import model_validator
from src.models.BaseModel import BaseModel

if TYPE_CHECKING:
    from src.models.Cancha import Cancha


class Horario(BaseModel, table=True):
    cancha_id: int = Field(foreign_key="cancha.id", nullable=False)
    disponible: bool = True
    hora_inicio: time
    hora_fin: time

    cancha: "Cancha" = Relationship(back_populates="horarios")

    # ================= VALIDACIÓN DE CONSISTENCIA TEMPORAL =================

    @model_validator(mode='after')
    def validar_horas_logicas(self):

        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin.")
        return self

    # ================= VALIDACIÓN DE SUPERPOSICIÓN (CONTRA BD) =================

    @model_validator(mode='after')
    def validar_no_superposicion(self):
        """Valida que este horario no choque con otro existente en la misma cancha."""

        # Importación diferida
        from database import engine

        with Session(engine) as session:
            # Lógica de superposición: (StartA < EndB) and (EndA > StartB)
            # Buscamos si existe algun horario QUE NO SEA ESTE MISMO (para updates)
            # que se solape en la misma cancha.
            query = select(Horario).where(
                Horario.cancha_id == self.cancha_id,
                Horario.hora_inicio < self.hora_fin,
                Horario.hora_fin > self.hora_inicio
            )

            # Si estamos editando un horario existente (tiene ID), lo excluimos de la búsqueda
            # para que no choque consigo mismo.
            if self.id is not None:
                query = query.where(Horario.id != self.id)

            horario_chocante = session.exec(query).first()

            if horario_chocante:
                raise ValueError(
                    f"El horario {self.hora_inicio}-{self.hora_fin} se superpone con uno existente "
                    f"({horario_chocante.hora_inicio}-{horario_chocante.hora_fin}) en esta cancha."
                )

        return self