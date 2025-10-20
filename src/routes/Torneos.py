from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from src.models.Torneo import Torneo
from src.models.Cancha import Cancha
from typing import List

torneos_router = APIRouter(prefix="/torneos", tags=["Torneos"])

@torneos_router.get("/")
def listar_torneos(session: Session = Depends(get_session)) -> List[Torneo]:
    pass

@torneos_router.get("/{id}")
def obtener_torneo(id: int, session: Session = Depends(get_session)) -> Torneo:
    pass

@torneos_router.post("/")
def crear_torneo(torneo: Torneo, session: Session = Depends(get_session)) -> Torneo:
    pass

@torneos_router.put("/{id}")
def actualizar_torneo(
    id: int, torneo: Torneo, session: Session = Depends(get_session)
) -> Torneo:
    pass

@torneos_router.post("/{id}/canchas")
def agregar_cancha_torneo(
    id: int, cancha: Cancha, session: Session = Depends(get_session)
) -> Cancha:
    pass

@torneos_router.get("/{id}/canchas")
def listar_canchas_torneo(
    id: int, session: Session = Depends(get_session)
) -> List[Cancha]:
    pass

@torneos_router.delete("/{id}")
def eliminar_torneo(id: int, session: Session = Depends(get_session)) -> None:
    pass
