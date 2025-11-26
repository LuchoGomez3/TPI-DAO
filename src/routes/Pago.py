from fastapi import APIRouter, Depends, Body
from src.service.Pago import PagosService
from src.schemas.pago import PagoCreate, PagoResponse
from typing import List, Optional
from datetime import date

pagos_router = APIRouter(prefix="/pagos", tags=["Pagos"])

@pagos_router.get("/", response_model=List[PagoResponse])
def listar_pagos(
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    año: Optional[int] = None,
    service: PagosService = Depends()
):
    return service.get_pagos(fecha_desde, fecha_hasta, año)

@pagos_router.post("/", response_model=PagoResponse)
def registrar_pago(
    pago: PagoCreate,
    estado: str = Body(default="Pagado", embed=True), # Recibimos el string del estado aparte o dentro del objeto
    service: PagosService = Depends()
):
    return service.create_pago(pago, estado)