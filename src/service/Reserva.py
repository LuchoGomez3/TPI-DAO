# src/service/Reserva.py
from sqlmodel import Session, select, and_
from fastapi import Depends, HTTPException
from database import get_session
from src.models.Reserva import Reserva, EstadoReserva  # EstadoReserva es clave
from src.models.Cancha import Cancha
from src.models.Cliente import Cliente
from src.models.Busquedas import Servicio, ReservaServicio
from src.schemas.Reserva import ReservaCreate, ReservaUpdate, ReservaResponse
from typing import List
from datetime import datetime


class ReservasService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _check_availability(self, cancha_id: int, fecha: datetime, inicio: datetime.time, fin: datetime.time,
                            reserva_id: Optional[int] = None):
        # 1. Verificar si hay reservas CONFIRMADAS o PENDIENTES que se superpongan

        # Encontrar el ID del estado 'Confirmada' y 'Pendiente' (asumiendo que los nombres se cargaron correctamente)
        estado_confirmada_id = self.session.exec(
            select(EstadoReserva.id).where(EstadoReserva.nombre == 'Confirmada')).first()
        estado_pendiente_id = self.session.exec(
            select(EstadoReserva.id).where(EstadoReserva.nombre == 'Pendiente')).first()

        if not estado_confirmada_id or not estado_pendiente_id:
            raise HTTPException(status_code=500, detail="Error de configuración: Faltan estados de reserva.")

        # Condición de superposición: (hora_inicio_existente < hora_fin_nueva) AND (hora_fin_existente > hora_inicio_nueva)
        query = select(Reserva).where(
            Reserva.cancha_id == cancha_id,
            Reserva.fecha == fecha.date(),  # Comparar solo la fecha
            Reserva.hora_inicio < fin,
            Reserva.hora_fin > inicio,
            Reserva.estado_reserva_id.in_([estado_confirmada_id, estado_pendiente_id])
        )

        if reserva_id:
            query = query.where(Reserva.id != reserva_id)

        overlap_reserva = self.session.exec(query).first()
        if overlap_reserva:
            raise HTTPException(
                status_code=409,
                detail=f"Cancha no disponible. Se superpone con la reserva {overlap_reserva.id}."
            )

    def get_reservas(self) -> List[ReservaResponse]:
        reservas = self.session.exec(select(Reserva)).all()
        return [ReservaResponse.model_validate(r) for r in reservas]

    def create_reserva(self, reserva_data: ReservaCreate) -> ReservaResponse:
        # 0. Validar existencia de FKs
        if not self.session.get(Cliente, reserva_data.cliente_id):
            raise HTTPException(status_code=400, detail="Cliente no existe.")
        if not self.session.get(Cancha, reserva_data.cancha_id):
            raise HTTPException(status_code=400, detail="Cancha no existe.")

        estado_pendiente = self.session.exec(select(EstadoReserva).where(EstadoReserva.nombre == 'Pendiente')).first()
        if not estado_pendiente:
            raise HTTPException(status_code=500, detail="Error de configuración: Estado 'Pendiente' no encontrado.")

        # 1. Validar Disponibilidad (función clave del proyecto)
        self._check_availability(
            reserva_data.cancha_id,
            reserva_data.fecha,
            reserva_data.hora_inicio,
            reserva_data.hora_fin
        )

        try:
            # 2. Crear la reserva con estado inicial PENDIENTE
            new_reserva = Reserva(
                **reserva_data.model_dump(exclude={'servicios_ids'}),
                estado_reserva_id=estado_pendiente.id
            )
            self.session.add(new_reserva)
            self.session.commit()
            self.session.refresh(new_reserva)

            # 3. Manejar Servicios Adicionales (Tabla N:M)
            if reserva_data.servicios_ids:
                for servicio_id in reserva_data.servicios_ids:
                    if not self.session.get(Servicio, servicio_id):
                        raise HTTPException(status_code=400, detail=f"Servicio con ID {servicio_id} no existe.")

                    link = ReservaServicio(reserva_id=new_reserva.id, servicio_id=servicio_id)
                    self.session.add(link)
                self.session.commit()
                self.session.refresh(new_reserva)

            return ReservaResponse.model_validate(new_reserva)

        except HTTPException:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear reserva: {e}")

    # Otras operaciones CRUD (update, delete) irían aquí, incluyendo validación de superposición.