from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from database import get_session
from src.models.Pago import Pago, EstadoPago
from src.schemas.pago import PagoCreate, PagoResponse
from typing import List, Optional
from datetime import date
from sqlalchemy import extract


class PagosService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_pagos(self, fecha_desde: Optional[date] = None, fecha_hasta: Optional[date] = None,
                  año: Optional[int] = None) -> List[PagoResponse]:
        try:
            query = select(Pago)
            if fecha_desde:
                query = query.where(Pago.fecha_pago >= fecha_desde)
            if fecha_hasta:
                query = query.where(Pago.fecha_pago <= fecha_hasta)
            if año:
                query = query.where(extract('year', Pago.fecha_pago) == año)

            pagos = self.session.exec(query).all()
            return [PagoResponse.model_validate(p) for p in pagos]
        except Exception as e:
            print(f"❌ ERROR LEYENDO PAGOS: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def create_pago(self, pago_data: PagoCreate, estado_nombre: str = "Pagado") -> PagoResponse:
        try:
            estado_obj = self.session.exec(select(EstadoPago).where(EstadoPago.nombre == estado_nombre)).first()
            if not estado_obj:
                # Fallback por si no existe el estado (aunque el seed debería crearlo)
                estado_obj = EstadoPago(nombre=estado_nombre)
                self.session.add(estado_obj)
                self.session.commit()

            new_pago = Pago(
                reserva_id=pago_data.reserva_id,
                monto=pago_data.monto,
                fecha_pago=pago_data.fecha_pago,
                estado_pago_id=estado_obj.id
            )
            self.session.add(new_pago)
            self.session.commit()
            self.session.refresh(new_pago)
            return PagoResponse.model_validate(new_pago)
        except Exception as e:
            self.session.rollback()
            print(f"❌ ERROR CREANDO PAGO: {e}")
            raise HTTPException(status_code=500, detail=str(e))