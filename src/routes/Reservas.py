from fastapi import APIRouter, Depends, Query
from src.service.Reserva import ReservasService
from src.schemas.Reserva import ReservaCreate, ReservaResponse
from typing import List, Optional, Dict
from datetime import date, time

reservas_router = APIRouter(prefix="/reservas", tags=["Reservas"])

@reservas_router.get("/", response_model=List[ReservaResponse])
def listar_reservas(
    fecha: Optional[date] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    año: Optional[int] = None,
    service: ReservasService = Depends()
):
    return service.get_reservas(fecha, fecha_desde, fecha_hasta, año)

@reservas_router.post("/", response_model=ReservaResponse)
def crear_reserva(reserva: ReservaCreate, service: ReservasService = Depends()):
    return service.create_reserva(reserva)

@reservas_router.put("/{id}/cancelar", response_model=ReservaResponse)
def cancelar_reserva(id: int, service: ReservasService = Depends()):
    return service.cancel_reserva(id)

@reservas_router.delete("/{id}")
def eliminar_reserva(id: int, service: ReservasService = Depends()):
    service.delete_reserva(id)
    return {"ok": True}

@reservas_router.get("/disponibilidad")
def verificar_disponibilidad(
    cancha_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    service: ReservasService = Depends()
):
    disponible = service.check_availability_public(cancha_id, fecha, hora_inicio, hora_fin)
    return {"disponible": disponible}