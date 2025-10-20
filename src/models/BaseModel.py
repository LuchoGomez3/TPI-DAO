from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    fecha_creacion: datetime = Field(default=datetime.now())
    fecha_actualizacion: datetime = Field(default=datetime.now())
