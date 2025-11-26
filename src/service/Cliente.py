from sqlmodel import Session, select
from src.models.Cliente import Cliente
from src.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from fastapi import Depends, HTTPException
from database import get_session
from typing import List


class ClientesService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_clientes(self) -> List[ClienteResponse]:
        try:
            clientes = self.session.exec(select(Cliente)).all()
            return [ClienteResponse.model_validate(cliente) for cliente in clientes]
        except Exception as e:
            print(f"❌ ERROR EN CLIENTES: {e}")  # Esto aparecerá en tu terminal negra
            raise HTTPException(status_code=500, detail=str(e))

    def get_cliente(self, id: int) -> ClienteResponse:
        cliente = self.session.get(Cliente, id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return ClienteResponse.model_validate(cliente)

    def create_cliente(self, cliente_data: ClienteCreate) -> ClienteResponse:
        try:
            new_cliente = Cliente.model_validate(cliente_data)
            self.session.add(new_cliente)
            self.session.commit()
            self.session.refresh(new_cliente)
            return ClienteResponse.model_validate(new_cliente)
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def update_cliente(self, id: int, cliente_data: ClienteUpdate) -> ClienteResponse:
        cliente_obj = self.session.get(Cliente, id)

        if not cliente_obj:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        data = cliente_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(cliente_obj, key, value)

        self.session.add(cliente_obj)
        self.session.commit()
        self.session.refresh(cliente_obj)
        return ClienteResponse.model_validate(cliente_obj)

    def delete_cliente(self, id: int):
        cliente_obj = self.session.get(Cliente, id)
        if not cliente_obj:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        self.session.delete(cliente_obj)
        self.session.commit()