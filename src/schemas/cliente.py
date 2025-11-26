from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    email: str


class ClienteCreate(ClienteBase):
    pass
    # Quitamos temporalmente el validador de regex para asegurar que no sea el causante del crash


class ClienteUpdate(ClienteBase):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None


class ClienteResponse(ClienteBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True