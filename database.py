from sqlmodel import SQLModel, create_engine, Session

from src.models.Cliente import Cliente
from src.models.Cancha import Cancha, TipoCancha
from src.models.Reserva import Reserva, EstadoReserva
from src.models.Horario import Horario
from src.models.Torneo import Torneo, CanchaTorneoLink
from src.models.Pago import Pago, EstadoPago
from src.models.Busquedas import Servicio, ReservaServicio


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
