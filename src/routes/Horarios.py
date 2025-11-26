from fastapi import APIRouter, Depends
from src.service.Horario import HorariosService
from src.schemas.Horario import HorarioCreate, HorarioUpdate, HorarioResponse
from typing import List

horarios_router = APIRouter(prefix="/horarios", tags=["Horarios"])

@horarios_router.get("/{cancha_id}", response_model=List[HorarioResponse])
def listar_horarios(cancha_id: int, service: HorariosService = Depends()):
    return service.get_horarios(cancha_id)

@horarios_router.post("/{cancha_id}", response_model=HorarioResponse)
def crear_horario_cancha(cancha_id: int, horario: HorarioCreate, service: HorariosService = Depends()):
    return service.create_horario_cancha(cancha_id, horario)

@horarios_router.put("/{cancha_id}/{horario_id}", response_model=HorarioResponse)
def actualizar_horario_cancha(cancha_id: int, horario_id: int, horario: HorarioUpdate, service: HorariosService = Depends()):
    return service.update_horario_cancha(horario_id, horario)

@horarios_router.delete("/{cancha_id}/{horario_id}")
def eliminar_horario_cancha(cancha_id: int, horario_id: int, service: HorariosService = Depends()):
    service.delete_horario_cancha(horario_id)
    return {"ok": True}