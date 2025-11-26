from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional, List
# Importaciones permitidas
from src.schemas.cliente import ClienteResponse
from src.schemas.Cancha import CanchaResponse
from src.schemas.servicio import ServicioResponse
from src.schemas.pago import PagoResponse  # Esto ahora es seguro


class EstadoReservaResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True


class ReservaBase(BaseModel):
    cliente_id: int
    cancha_id: int
    fecha: datetime
    hora_inicio: time
    hora_fin: time
    servicios_ids: Optional[List[int]] = None


class ReservaCreate(ReservaBase):
    pass


class ReservaUpdate(ReservaBase):
    cliente_id: Optional[int] = None
    cancha_id: Optional[int] = None
    fecha: Optional[datetime] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    servicios_ids: Optional[List[int]] = None


class ReservaResponse(ReservaBase):
    id: int
    estado_reserva_id: int

    fecha_creacion: datetime
    fecha_actualizacion: datetime

    cliente: ClienteResponse
    cancha: CanchaResponse
    estado_reserva: EstadoReservaResponse
    servicios: List[ServicioResponse] = []

    # Aquí usamos el PagoResponse
    pago: Optional[PagoResponse] = None

    class Config:
        from_attributes = True