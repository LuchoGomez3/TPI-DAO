from pydantic import BaseModel, field_validator, model_validator
from datetime import date, time, datetime
from typing import Optional, List


# ================= SCHEMAS ANIDADOS (MINI) =================
# Definimos estos aquí para que la ReservaResponse sepa cómo mostrar
# los datos de los objetos relacionados sin importar todo el archivo de Cliente/Cancha

class ClienteNested(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str

    class Config:
        from_attributes = True


class CanchaNested(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True


class EstadoNested(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True


class PagoNested(BaseModel):
    id: int
    monto: float
    estado_pago_id: int

    class Config:
        from_attributes = True


# ================= SCHEMAS PRINCIPALES =================

class ReservaBase(BaseModel):
    cliente_id: int
    cancha_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    servicios_ids: Optional[List[int]] = []

    @field_validator("fecha")
    @classmethod
    def validar_fecha_futura(cls, v: date):
        if v < date.today():
            raise ValueError("La fecha de reserva no puede ser en el pasado.")
        return v

    @model_validator(mode='after')
    def validar_rango_horario(self):
        # Nota: self es el objeto modelo en mode='after'
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin.")
        return self


class ReservaCreate(ReservaBase):
    pass


class ReservaResponse(BaseModel):
    id: int
    fecha: datetime
    hora_inicio: time
    hora_fin: time

    # --- CAMBIO CLAVE: Usamos los modelos anidados en lugar de 'dict' ---
    cliente: ClienteNested
    cancha: CanchaNested
    estado_reserva: EstadoNested
    pago: Optional[PagoNested] = None

    class Config:
        from_attributes = True