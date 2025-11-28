from pydantic import BaseModel, field_validator
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

    # --- VALIDACIÓN PARA CREACIÓN (POST) ---
    @field_validator("monto")
    @classmethod
    def validar_monto_positivo(cls, v: float):
        if v <= 0:
            raise ValueError("El monto del pago debe ser mayor a 0.")
        return v

class PagoCreate(PagoBase):
    pass

class PagoUpdate(BaseModel):
    estado_pago_id: Optional[int] = None
    monto: Optional[float] = None
    fecha_pago: Optional[datetime] = None

    # --- VALIDACIÓN PARA ACTUALIZACIÓN (PUT) ---
    @field_validator("monto")
    @classmethod
    def validar_monto_positivo_update(cls, v: Optional[float]):
        # Si envían un monto, verificamos que sea positivo
        if v is not None and v <= 0:
            raise ValueError("El monto del pago debe ser mayor a 0.")
        return v

class PagoResponse(PagoBase):
    id: int
    estado_pago_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    estado_pago: EstadoPagoResponse

    class Config:
        from_attributes = True