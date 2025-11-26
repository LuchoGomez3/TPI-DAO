from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from database import get_session
from src.models.Reserva import Reserva, EstadoReserva
from src.models.Cancha import Cancha
from src.models.Cliente import Cliente
from src.models.Horario import Horario
from src.models.Busquedas import Servicio, ReservaServicio
from src.schemas.Reserva import ReservaCreate, ReservaResponse
from typing import List, Optional
from datetime import datetime, date, time
from sqlalchemy import extract


class ReservasService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _check_availability(self, cancha_id: int, fecha: datetime, inicio: time, fin: time,
                            reserva_id: Optional[int] = None):
        estados_ocupados = self.session.exec(
            select(EstadoReserva.id).where(EstadoReserva.nombre.in_(["Confirmada", "Pendiente"]))
        ).all()

        # Lógica de superposición: (StartA < EndB) and (EndA > StartB)
        query = select(Reserva).where(
            Reserva.cancha_id == cancha_id,
            Reserva.fecha == fecha,
            Reserva.hora_inicio < fin,
            Reserva.hora_fin > inicio,
            Reserva.estado_reserva_id.in_(estados_ocupados)
        )
        if reserva_id:
            query = query.where(Reserva.id != reserva_id)

        if self.session.exec(query).first():
            raise HTTPException(status_code=409, detail="Horario no disponible (Ya existe una reserva).")

    def check_availability_public(self, cancha_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> bool:
        try:
            self._check_availability(cancha_id, fecha, hora_inicio, hora_fin)
            return True
        except HTTPException:
            return False

    def get_reservas(self, fecha: Optional[date] = None, fecha_desde: Optional[date] = None,
                     fecha_hasta: Optional[date] = None, año: Optional[int] = None) -> List[ReservaResponse]:
        try:
            query = select(Reserva)

            if fecha:
                query = query.where(Reserva.fecha == fecha)
            if fecha_desde:
                query = query.where(Reserva.fecha >= fecha_desde)
            if fecha_hasta:
                query = query.where(Reserva.fecha <= fecha_hasta)
            if año:
                query = query.where(extract('year', Reserva.fecha) == año)

            reservas = self.session.exec(query).all()
            return [ReservaResponse.model_validate(r) for r in reservas]
        except Exception as e:
            print(f"❌ ERROR LEYENDO RESERVAS: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def create_reserva(self, reserva_data: ReservaCreate) -> ReservaResponse:
        try:
            # 1. Validar Lógica Temporal
            ahora = datetime.now()
            fecha_hora_inicio = datetime.combine(reserva_data.fecha, reserva_data.hora_inicio)
            fecha_hora_fin = datetime.combine(reserva_data.fecha, reserva_data.hora_fin)

            # A) No viajar al pasado
            if fecha_hora_inicio < ahora:
                raise HTTPException(status_code=400, detail="La fecha y hora de inicio deben ser futuras.")

            # B) El fin debe ser después del inicio
            if reserva_data.hora_fin <= reserva_data.hora_inicio:
                raise HTTPException(status_code=400, detail="La hora de fin debe ser posterior a la hora de inicio.")

            # C) Duración mínima (ej: 1 hora)
            duracion = (fecha_hora_fin - fecha_hora_inicio).total_seconds() / 3600
            if duracion < 1:
                raise HTTPException(status_code=400, detail="La reserva debe durar al menos 1 hora.")

            # 2. Validar existencia de Cliente y Cancha
            if not self.session.get(Cliente, reserva_data.cliente_id):
                raise HTTPException(status_code=404, detail="Cliente no encontrado")
            if not self.session.get(Cancha, reserva_data.cancha_id):
                raise HTTPException(status_code=404, detail="Cancha no encontrada")

            # 3. Validar Disponibilidad (Superposición)
            self._check_availability(reserva_data.cancha_id, reserva_data.fecha, reserva_data.hora_inicio,
                                     reserva_data.hora_fin)

            # 4. Buscar el Horario ID correspondiente
            horario_obj = self.session.exec(
                select(Horario).where(
                    Horario.cancha_id == reserva_data.cancha_id,
                    Horario.hora_inicio == reserva_data.hora_inicio,
                    Horario.hora_fin == reserva_data.hora_fin
                )
            ).first()

            # Fallback: Si no hay horario exacto, buscamos uno general
            if not horario_obj:
                horario_obj = self.session.exec(
                    select(Horario).where(Horario.cancha_id == reserva_data.cancha_id)).first()
                if not horario_obj:
                    raise HTTPException(status_code=404, detail="No hay horarios configurados para esta cancha.")

            # 5. Obtener estado inicial
            estado_pendiente = self.session.exec(
                select(EstadoReserva).where(EstadoReserva.nombre == "Pendiente")).first()

            # 6. Crear la reserva
            new_reserva = Reserva(
                **reserva_data.model_dump(exclude={'servicios_ids'}),
                estado_reserva_id=estado_pendiente.id,
                horario_id=horario_obj.id
            )
            self.session.add(new_reserva)
            self.session.commit()
            self.session.refresh(new_reserva)

            # 7. Agregar servicios
            if reserva_data.servicios_ids:
                for servicio_id in reserva_data.servicios_ids:
                    link = ReservaServicio(reserva_id=new_reserva.id, servicio_id=servicio_id)
                    self.session.add(link)
                self.session.commit()
                self.session.refresh(new_reserva)

            return ReservaResponse.model_validate(new_reserva)

        except HTTPException:
            raise
        except Exception as e:
            self.session.rollback()
            print(f"❌ ERROR CREANDO RESERVA: {e}")
            # ESTA LÍNEA ES CRÍTICA PARA QUE EL FRONTEND SEPA QUE FALLÓ:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    def cancel_reserva(self, id: int) -> ReservaResponse:
        reserva = self.session.get(Reserva, id)
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")

        estado = self.session.exec(select(EstadoReserva).where(EstadoReserva.nombre == "Cancelada")).first()
        reserva.estado_reserva_id = estado.id
        self.session.add(reserva)
        self.session.commit()
        self.session.refresh(reserva)
        return ReservaResponse.model_validate(reserva)

    def delete_reserva(self, id: int):
        reserva = self.session.get(Reserva, id)
        if reserva:
            self.session.delete(reserva)
            self.session.commit()