from fastapi import FastAPI
from database import init_db
from src.routes.Canchas import canchas_router
from src.routes.Clientes import clientes_router
from src.routes.Reservas import reservas_router
from src.routes.Horarios import horarios_router
from src.routes.Torneos import torneos_router
from src.routes.Pago import pagos_router
# 1. Importar el nuevo router de reportes
from src.routes.Reportes import reportes_router
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
app.include_router(torneos_router)
app.include_router(pagos_router)
# 2. Incluir el router en la app
app.include_router(reportes_router)

@app.get("/")
def root():
    return {"message": "Bienvenido al sistema de reservas"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)