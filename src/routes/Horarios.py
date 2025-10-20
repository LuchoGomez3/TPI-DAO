from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from src.models.Horario import Horario
from typing import List

horarios_router = APIRouter(prefix="/horarios", tags=["Horarios"])


@horarios_router.get("/{cancha_id}")
def listar_horarios(
    cancha_id: int, session: Session = Depends(get_session)
) -> List[Horario]:
    pass


@horarios_router.post("/{cancha_id}")
def crear_horario_cancha(
    cancha_id: int, horario: Horario, session: Session = Depends(get_session)
) -> Horario:
    pass


@horarios_router.put("/{cancha_id}/{horario_id}")
def actualizar_horario_cancha(
    cancha_id: int,
    horario_id: int,
    horario: Horario,
    session: Session = Depends(get_session),
) -> Horario:
    pass


@horarios_router.delete("/{cancha_id}/{horario_id}")
def eliminar_horario_cancha(
    cancha_id: int, horario_id: int, session: Session = Depends(get_session)
) -> None:
    pass
