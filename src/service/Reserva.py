from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from database import get_session
from src.models.Reserva import Reserva, EstadoReserva
from src.models.Cancha import Cancha
from src.models.Cliente import Cliente
from src.models.Horario import Horario
from src.models.Busquedas import ReservaServicio
from src.schemas.Reserva import ReservaCreate, ReservaResponse
from typing import List, Optional
from datetime import datetime, date, time
from sqlalchemy import extract


class ReservasService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def check_availability_public(self, cancha_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> bool:
        """
        Verifica disponibilidad sin intentar crear la reserva.
        Ideal para el frontend antes de enviar el formulario.
        """
        # Replicamos la lógica de "lectura" aquí para no instanciar un Modelo pesado
        estados_ocupados = self.session.exec(
            select(EstadoReserva.id).where(EstadoReserva.nombre.in_(["Confirmada", "Pendiente"]))
        ).all()

        # Convertir date a datetime para la query si es necesario, dependiendo de tu DB
        fecha_dt = datetime.combine(fecha, time.min)

        query = select(Reserva).where(
            Reserva.cancha_id == cancha_id,
            Reserva.fecha == fecha_dt,
            Reserva.hora_inicio < hora_fin,
            Reserva.hora_fin > hora_inicio,
            Reserva.estado_reserva_id.in_(estados_ocupados)
        )

        # Si encuentra algo, NO está disponible
        return not self.session.exec(query).first()

    def get_reservas(self, fecha: Optional[date] = None, fecha_desde: Optional[date] = None,
                     fecha_hasta: Optional[date] = None, año: Optional[int] = None,
                     cancha_id: Optional[int] = None, usuario_id: Optional[int] = None) -> List[ReservaResponse]:
        try:
            query = select(Reserva)

            if fecha:
                query = query.where(Reserva.fecha == datetime.combine(fecha, time.min))
            if fecha_desde:
                query = query.where(Reserva.fecha >= datetime.combine(fecha_desde, time.min))
            if fecha_hasta:
                query = query.where(Reserva.fecha <= datetime.combine(fecha_hasta, time.max))
            if año:
                query = query.where(extract('year', Reserva.fecha) == año)
            if cancha_id:
                query = query.where(Reserva.cancha_id == cancha_id)
            if usuario_id:
                query = query.where(Reserva.cliente_id == usuario_id)

            reservas = self.session.exec(query).all()
            return [ReservaResponse.model_validate(r) for r in reservas]
        except Exception as e:
            print(f"❌ ERROR LEYENDO RESERVAS: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def create_reserva(self, reserva_data: ReservaCreate) -> ReservaResponse:
        # 1. Validar existencia de Cliente y Cancha (Para dar 404 en lugar de error genérico)
        if not self.session.get(Cliente, reserva_data.cliente_id):
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        if not self.session.get(Cancha, reserva_data.cancha_id):
            raise HTTPException(status_code=404, detail="Cancha no encontrada")

        try:
            # 2. Buscar el Horario ID correspondiente (Lógica de Negocio)
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

            # 3. Obtener estado inicial
            estado_pendiente = self.session.exec(
                select(EstadoReserva).where(EstadoReserva.nombre == "Pendiente")).first()

            # Preparar datos (convertir date a datetime para el modelo)
            fecha_dt = datetime.combine(reserva_data.fecha, time.min)

            # 4. Instanciar Modelo
            # ¡AQUÍ SE DISPARAN LAS VALIDACIONES DEL MODELO! (Superposición, etc.)
            new_reserva = Reserva(
                cliente_id=reserva_data.cliente_id,
                cancha_id=reserva_data.cancha_id,
                estado_reserva_id=estado_pendiente.id,
                horario_id=horario_obj.id,
                fecha=fecha_dt,
                hora_inicio=reserva_data.hora_inicio,
                hora_fin=reserva_data.hora_fin
            )

            # Si pasa la validación, guardamos
            self.session.add(new_reserva)
            self.session.commit()
            self.session.refresh(new_reserva)

            # 5. Agregar servicios (Relación M:N)
            if reserva_data.servicios_ids:
                for servicio_id in reserva_data.servicios_ids:
                    link = ReservaServicio(reserva_id=new_reserva.id, servicio_id=servicio_id)
                    self.session.add(link)
                self.session.commit()
                self.session.refresh(new_reserva)

            return ReservaResponse.model_validate(new_reserva)

        except ValueError as ve:
            # Capturamos los errores de validación del MODELO (ej: superposición)
            self.session.rollback()
            raise HTTPException(status_code=409, detail=str(ve))

        except Exception as e:
            self.session.rollback()
            print(f"❌ ERROR CREANDO RESERVA: {e}")
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