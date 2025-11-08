from fastapi import FastAPI
from database import init_db
from src.routes.Canchas import canchas_router
from src.routes.Clientes import clientes_router
from src.routes.Reservas import reservas_router
from src.routes.Horarios import horarios_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield



app = FastAPI(title="Sistema de Reservas de Canchas Deportivas", lifespan=lifespan)


app.include_router(clientes_router)
app.include_router(reservas_router)
app.include_router(canchas_router)
app.include_router(horarios_router)


@app.get("/")
def root():
    return {"message": "Bienvenido al sistema de reservas"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)