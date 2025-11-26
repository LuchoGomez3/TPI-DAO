from fastapi import APIRouter, Depends
from src.service.Cancha import CanchasService
from src.schemas.Cancha import CanchaCreate, CanchaUpdate, CanchaResponse
from typing import List

canchas_router = APIRouter(prefix="/canchas", tags=["Canchas"])

@canchas_router.get("/", response_model=List[CanchaResponse])
def listar_canchas(service: CanchasService = Depends()):
    return service.get_canchas()

@canchas_router.get("/{id}", response_model=CanchaResponse)
def obtener_cancha(id: int, service: CanchasService = Depends()):
    return service.get_cancha(id)

@canchas_router.post("/", response_model=CanchaResponse)
def crear_cancha(cancha: CanchaCreate, service: CanchasService = Depends()):
    return service.create_cancha(cancha)

@canchas_router.put("/{id}", response_model=CanchaResponse)
def actualizar_cancha(id: int, cancha: CanchaUpdate, service: CanchasService = Depends()):
    return service.update_cancha(id, cancha)

@canchas_router.delete("/{id}")
def eliminar_cancha(id: int, service: CanchasService = Depends()):
    service.delete_cancha(id)
    return {"ok": True}