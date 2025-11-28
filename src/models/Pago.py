from sqlmodel import SQLModel, Field, Relationship, select, Session
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from pydantic import field_validator, model_validator
from src.models.BaseModel import BaseModel

if TYPE_CHECKING:
    from src.models.Reserva import Reserva


class EstadoPago(SQLModel, table=True):
    __tablename__ = "estado_pago"

    # Corregimos el tipo a Optional[int] para consistencia
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nombre: str = Field(..., min_length=3, max_length=50)

    pagos: List["Pago"] = Relationship(back_populates="estado_pago")


class Pago(BaseModel, table=True):
    __tablename__ = "pago"

    reserva_id: int = Field(foreign_key="reserva.id", unique=True)
    estado_pago_id: int = Field(foreign_key="estado_pago.id")
    monto: float
    fecha_pago: datetime = Field(default_factory=datetime.now)

    reserva: "Reserva" = Relationship(back_populates="pago")
    estado_pago: "EstadoPago" = Relationship(back_populates="pagos")

    # ================= VALIDACIÓN DE MONTO (SIMPLE) =================

    @field_validator("monto")
    @classmethod
    def validar_monto_positivo(cls, v: float):
        if v <= 0:
            raise ValueError("El monto del pago debe ser mayor a 0.")
        return v

    # ================= VALIDACIÓN DE NO DUPLICADOS (CONTRA BD) =================

    @model_validator(mode='after')
    def validar_pago_unico_por_reserva(self):
        """
        Valida que no exista ya un pago registrado para esta reserva.
        Esto evita cobrarle dos veces al cliente por error.
        """
        from database import engine

        with Session(engine) as session:

            query = select(Pago).where(Pago.reserva_id == self.reserva_id)


            if self.id is not None:
                query = query.where(Pago.id != self.id)

            pago_existente = session.exec(query).first()

            if pago_existente:
                raise ValueError(
                    f"La reserva {self.reserva_id} ya tiene un pago registrado (ID Pago: {pago_existente.id}). "
                    "No se puede pagar la misma reserva dos veces."
                )

        return self