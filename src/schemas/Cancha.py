from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TipoCanchaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str

    class Config:
        from_attributes = True

class CanchaBase(BaseModel):
    nombre: str
    tipo_cancha_id: int

class CanchaCreate(CanchaBase):
    pass

class CanchaUpdate(CanchaBase):
    nombre: Optional[str] = None
    tipo_cancha_id: Optional[int] = None

class CanchaResponse(CanchaBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    tipo_cancha: TipoCanchaResponse

    class Config:
        from_attributes = True
