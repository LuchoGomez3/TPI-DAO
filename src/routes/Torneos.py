from fastapi import APIRouter, Depends
from src.service.Torneo import TorneosService
from src.schemas.Torneo import TorneoCreate, TorneoUpdate, TorneoResponse
from src.schemas.Cancha import CanchaResponse
from typing import List

torneos_router = APIRouter(prefix="/torneos", tags=["Torneos"])

@torneos_router.get("/", response_model=List[TorneoResponse])
def listar_torneos(service: TorneosService = Depends()):
    return service.get_torneos()

@torneos_router.get("/{id}", response_model=TorneoResponse)
def obtener_torneo(id: int, service: TorneosService = Depends()):
    return service.get_torneo(id)

@torneos_router.post("/", response_model=TorneoResponse)
def crear_torneo(torneo: TorneoCreate, service: TorneosService = Depends()):
    return service.create_torneo(torneo)

@torneos_router.put("/{id}", response_model=TorneoResponse)
def actualizar_torneo(id: int, torneo: TorneoUpdate, service: TorneosService = Depends()):
    return service.update_torneo(id, torneo)

@torneos_router.delete("/{id}")
def eliminar_torneo(id: int, service: TorneosService = Depends()):
    service.delete_torneo(id)
    return {"ok": True}

@torneos_router.post("/{id}/canchas")
def agregar_cancha_torneo(id: int, cancha_id: int, service: TorneosService = Depends()):
    # Nota: El front probablemente envía solo el ID o un objeto, ajustar según necesidad.
    # Aquí asumo que recibimos el ID en el body o query, simplificado a query para este ejemplo:
    return service.agregar_cancha_torneo(id, cancha_id)

@torneos_router.get("/{id}/canchas", response_model=List[CanchaResponse])
def listar_canchas_torneo(id: int, service: TorneosService = Depends()):
    return service.listar_canchas_torneo(id)