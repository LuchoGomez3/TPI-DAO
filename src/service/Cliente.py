from sqlmodel import Session
from src.models.Cliente import Cliente
from sqlmodel import select
from fastapi import Depends
from database import get_session

class ClientesService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_clientes(self):
        return self.session.exec(select(Cliente)).all()
    
    def get_cliente(self, id: int):
        return self.session.exec(select(Cliente).where(Cliente.id == id)).one()
    
    def create_cliente(self, cliente: Cliente):
        self.session.add(cliente)
        self.session.commit()
        return cliente
    
    def update_cliente(self, id: int, cliente: Cliente):
        cliente = self.session.exec(select(Cliente).where(Cliente.id == id)).one()
        cliente.nombre = cliente.nombre
        cliente.apellido = cliente.apellido
        cliente.telefono = cliente.telefono
        cliente.email = cliente.email
        self.session.commit()
        return cliente
    
    def delete_cliente(self, id: int):
        cliente = self.session.exec(select(Cliente).where(Cliente.id == id)).one()
        self.session.delete(cliente)
        self.session.commit()
        
