from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ServicioBase(BaseModel):
    nombre: str
    costo: float


class ServicioCreate(ServicioBase):
    pass


class ServicioUpdate(ServicioBase):
    nombre: Optional[str] = None
    costo: Optional[float] = None


class ServicioResponse(ServicioBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True
