from pydantic import BaseModel, field_validator
from datetime import datetime
import re
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    email: str
    
class ClienteCreate(ClienteBase):
    @field_validator("email", mode="after")
    @classmethod
    def validate_email(cls, email: str):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Email inválido")
        return email
    

class ClienteUpdate(ClienteBase):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    
    @field_validator("email", mode="after")
    @classmethod
    def validate_email(cls, email: str):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Email inválido")
        return email

class ClienteResponse(ClienteBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime