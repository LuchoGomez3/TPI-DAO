from sqlmodel import Relationship, Field, SQLModel, select, Session
from datetime import datetime, time
from typing import Optional, List, TYPE_CHECKING
from pydantic import model_validator
from src.models.BaseModel import BaseModel

from src.models.Busquedas import Servicio, ReservaServicio

if TYPE_CHECKING:
    from src.models.Cliente import Cliente
    from src.models.Cancha import Cancha
    from src.models.Horario import Horario
    from src.models.Pago import Pago


class EstadoReserva(SQLModel, table=True):
    __tablename__ = "estado_reserva"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
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

    # ================= VALIDACIÓN 1: COHERENCIA HORARIA =================
    @model_validator(mode='after')
    def validar_coherencia_horas(self):
        """Valida que el inicio sea antes que el fin."""
        if self.hora_inicio >= self.hora_fin:
            raise ValueError(
                f"La hora de inicio ({self.hora_inicio}) debe ser anterior a la hora de fin ({self.hora_fin}).")
        return self

    # ================= VALIDACIÓN 2: DISPONIBILIDAD (INFALIBLE) =================
    @model_validator(mode='after')
    def validar_no_superposicion_db(self):
        from database import engine

        with Session(engine) as session:
            # 1. Ignorar reservas canceladas
            estado_cancelada = session.exec(
                select(EstadoReserva).where(EstadoReserva.nombre == "Cancelada")
            ).first()
            id_cancelada = estado_cancelada.id if estado_cancelada else -1

            # 2. Query AMPLIA: Traer TODAS las reservas activas de esta cancha.
            # NO filtramos por fecha en SQL para evitar problemas de formato de SQLite.
            query = select(Reserva).where(
                Reserva.cancha_id == self.cancha_id,
                Reserva.estado_reserva_id != id_cancelada
            )

            # Excluirse a sí mismo si es edición
            if self.id is not None:
                query = query.where(Reserva.id != self.id)

            candidatos = session.exec(query).all()

            # 3. Comparación en Memoria (Python vs Python)
            # Aquí comparamos objetos reales, así que no importa el formato del string en la BD.
            fecha_objetivo = self.fecha.date()

            for res in candidatos:
                # A) Chequear Fecha
                # Nos aseguramos de extraer solo la parte 'date' de la reserva guardada
                res_fecha = res.fecha.date() if isinstance(res.fecha, datetime) else res.fecha

                if res_fecha == fecha_objetivo:
                    # B) Chequear Hora (Superposición)
                    # (StartA < EndB) y (EndA > StartB)
                    if res.hora_inicio < self.hora_fin and res.hora_fin > self.hora_inicio:
                        raise ValueError(
                            f"CONFLICTO: La cancha ya está reservada el {fecha_objetivo} "
                            f"de {res.hora_inicio} a {res.hora_fin}."
                        )

        return self