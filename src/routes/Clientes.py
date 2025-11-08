from fastapi import APIRouter, Depends
from src.service.Cliente import ClientesService
from src.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from typing import List

clientes_router = APIRouter(prefix="/clientes", tags=["Clientes"])

@clientes_router.get("/")
def listar_clientes(clientes_service: ClientesService = Depends(ClientesService)) -> List[ClienteResponse]:
    return clientes_service.get_clientes()


@clientes_router.get("/{id}")
def obtener_cliente(id: int, clientes_service: ClientesService = Depends(ClientesService)) -> ClienteResponse:
    return clientes_service.get_cliente(id)


@clientes_router.post("/")
def crear_cliente(cliente: ClienteCreate, clientes_service: ClientesService = Depends(ClientesService)) -> ClienteResponse:
    return clientes_service.create_cliente(cliente)


@clientes_router.put("/{id}")
def actualizar_cliente(
    id: int, cliente: ClienteUpdate, clientes_service: ClientesService = Depends(ClientesService)
) -> ClienteResponse:
    return clientes_service.update_cliente(id, cliente)


@clientes_router.delete("/{id}")
def eliminar_cliente(id: int, clientes_service: ClientesService = Depends(ClientesService)) -> None:
    return clientes_service.delete_cliente(id)
