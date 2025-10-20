from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from database import get_session
from src.models.Reserva import Reserva

reservas_router = APIRouter(prefix="/reservas", tags=["Reservas"])


@reservas_router.get("/")
def listar_reservas(session: Session = Depends(get_session)) -> List[Reserva]:
    pass
