from fastapi import FastAPI
from database import init_db
from src.routes.Clientes import clientes_router
from src.routes.Reservas import reservas_router
from src.routes.Canchas import canchas_router
from src.routes.Horarios import horarios_router

from src.models.Cliente import Cliente
from src.models.Cancha import Cancha
from src.models.Reserva import Reserva
from src.models.Horario import Horario
from src.models.Torneo import Torneo

app = FastAPI(title="Sistema de Reservas de Canchas Deportivas")

init_db()

app.include_router(clientes_router)
app.include_router(reservas_router)
app.include_router(canchas_router)
app.include_router(horarios_router)


@app.get("/")
def root():
    return {"message": "Bienvenido al sistema de reservas"}
