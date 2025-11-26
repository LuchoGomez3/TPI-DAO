from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from src.schemas.Cancha import CanchaResponse # <--- CAMBIO AQUÍ (C mayúscula)

class TorneoBase(BaseModel):
    nombre: str
    fecha_inicio: datetime
    fecha_fin: datetime
    descripcion: Optional[str] = None

class TorneoCreate(TorneoBase):
    pass

class TorneoUpdate(TorneoBase):
    nombre: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    descripcion: Optional[str] = None

class TorneoResponse(TorneoBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    canchas: List[CanchaResponse]

    class Config:
        from_attributes = True