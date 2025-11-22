from pydantic import BaseModel
from datetime import time, datetime
from typing import Optional


class HorarioBase(BaseModel):
    disponible: bool = True
    hora_inicio: time
    hora_fin: time


class HorarioCreate(HorarioBase):
    pass


class HorarioUpdate(HorarioBase):
    disponible: Optional[bool] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None


class HorarioResponse(HorarioBase):
    id: int
    cancha_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True
