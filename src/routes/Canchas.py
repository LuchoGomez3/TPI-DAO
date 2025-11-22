from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from src.models.Cancha import Cancha
from typing import List

canchas_router = APIRouter(prefix="/canchas", tags=["Canchas"])

@canchas_router.get("/")
def listar_canchas(session: Session = Depends(get_session)) -> List[Cancha]:
    pass

@canchas_router.get("/{id}")
def obtener_cancha(id: int, session: Session = Depends(get_session)) -> Cancha:
    pass

@canchas_router.post("/")
def crear_cancha(cancha: Cancha, session: Session = Depends(get_session)) -> Cancha:
    pass

@canchas_router.put("/{id}")
def actualizar_cancha(
    id: int, cancha: Cancha, session: Session = Depends(get_session)
) -> Cancha:
    pass

@canchas_router.delete("/{id}")
def eliminar_cancha(id: int, session: Session = Depends(get_session)) -> None:
    pass
