from sqlmodel import Session
from src.models.Cliente import Cliente
from src.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from sqlmodel import select
from fastapi import Depends, HTTPException
from database import get_session

class ClientesService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_clientes(self):
        clientes = self.session.exec(select(Cliente)).all()
        return [ClienteResponse.model_validate(cliente) for cliente in clientes]
    
    def get_cliente(self, id: int):
        cliente = self.session.get(Cliente, id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return cliente
    
    def create_cliente(self, cliente: ClienteCreate) -> Cliente:
        try:
            new_cliente = Cliente(
                nombre=cliente.nombre,
                apellido=cliente.apellido,
                telefono=cliente.telefono,
                email=cliente.email
            )
            self.session.add(new_cliente)
            self.session.commit()
            self.session.refresh(new_cliente)
            return ClienteResponse.model_validate(new_cliente)
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_cliente(self, id: int, cliente_data: ClienteUpdate):
        cliente_obj = self.session.exec(select(Cliente).where(Cliente.id == id)).one()
        
        if not cliente_obj:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        for key, value in cliente_data.model_dump().items():
            setattr(cliente_obj, key, value)
        
        self.session.add(cliente_obj)
        self.session.commit()
        self.session.refresh(cliente_obj)
        return ClienteResponse.model_validate(cliente_obj)
    
    def delete_cliente(self, id: int):
        cliente_obj = self.session.exec(select(Cliente).where(Cliente.id == id)).one()
        self.session.delete(cliente_obj)
        self.session.commit()
        
