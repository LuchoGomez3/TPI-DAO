from sqlmodel import Relationship, Field, SQLModel, select, Session
from datetime import datetime, time, date
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

    @model_validator(mode='after')
    def validar_coherencia_horas(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValueError(f"Error Horario: Inicio ({self.hora_inicio}) >= Fin ({self.hora_fin})")
        return self

    # ================= VALIDACIÓN 2: DISPONIBILIDAD (DEBUGGING) =================
    @model_validator(mode='after')
    def validar_no_superposicion_db(self):
        from database import engine

        # Fecha que queremos reservar (sin hora)
        target_date = self.fecha.date() if isinstance(self.fecha, datetime) else self.fecha

        print(f"\n--- VALIDANDO RESERVA ---")
        print(
            f"Intento reservar: Cancha {self.cancha_id} | Fecha {target_date} | Hora {self.hora_inicio} - {self.hora_fin}")

        with Session(engine) as session:
            # 1. Ignorar canceladas
            estado_cancelada = session.exec(
                select(EstadoReserva).where(EstadoReserva.nombre == "Cancelada")
            ).first()
            id_cancelada = estado_cancelada.id if estado_cancelada else -1

            # 2. Traer TODAS las reservas de esa cancha (sin filtrar fecha en SQL para estar seguros)
            query = select(Reserva).where(
                Reserva.cancha_id == self.cancha_id,
                Reserva.estado_reserva_id != id_cancelada
            )
            if self.id is not None:
                    query = query.where(Reserva.id != self.id)
            candidatos = session.exec(query).all()
            print(f"Reservas encontradas en BD para Cancha {self.cancha_id}: {len(candidatos)}")

                # 3. Comparar en Python
            for res in candidatos:
                # Normalizar fecha de la reserva existente
                res_fecha = res.fecha.date() if isinstance(res.fecha, datetime) else res.fecha

                # Solo comparamos si es el mismo día
                if res_fecha == target_date:
                    print(f"  -> Analizando choque con Reserva ID {res.id} ({res.hora_inicio} - {res.hora_fin})")

                    # Lógica de superposición
                    if res.hora_inicio < self.hora_fin and res.hora_fin > self.hora_inicio:
                        print("  -> ¡CHOQUE DETECTADO!")
                        raise ValueError(
                            f"CONFLICTO: La cancha ya está reservada el {target_date} "
                            f"de {res.hora_inicio} a {res.hora_fin}."
                        )
                    else:
                        print("  -> No choca.")

        print("--- VALIDACIÓN EXITOSA (Sin conflictos) ---\n")
        return self