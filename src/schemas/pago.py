from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- IMPORTANTE: ESTE ARCHIVO NO DEBE IMPORTAR NADA DE 'src' ---

class EstadoPagoResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

class PagoBase(BaseModel):
    reserva_id: int
    monto: float
    fecha_pago: datetime

class PagoCreate(PagoBase):
    pass

class PagoUpdate(BaseModel):
    estado_pago_id: Optional[int] = None
    monto: Optional[float] = None
    fecha_pago: Optional[datetime] = None

class PagoResponse(PagoBase):
    id: int
    estado_pago_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    estado_pago: EstadoPagoResponse

    class Config:
        from_attributes = True