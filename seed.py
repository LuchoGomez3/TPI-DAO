from datetime import date, time
from sqlmodel import Session, select
from database import engine
from src.models.Cliente import Cliente
from src.models.Cancha import Cancha
from src.models.Reserva import Reserva
from src.models.Horario import Horario
from src.models.Torneo import Torneo

def seed_data():
    with Session(engine) as session:
        # ===============================
        # CLIENTES
        # ===============================
        existing_clients = session.exec(select(Cliente)).all()
        if not existing_clients:
            clientes = [
                Cliente(nombre="Juan", apellido="Pérez", email="juan@example.com", telefono="123456789"),
                Cliente(nombre="María", apellido="Gómez", email="maria@example.com", telefono="987654321"),
            ]
            session.add_all(clientes)
            print("Clientes insertados.")

        # ===============================
        # CANCHAS
        # ===============================
        existing_canchas = session.exec(select(Cancha)).all()
        if not existing_canchas:
            canchas = [
                Cancha(nombre="Cancha 1", tipo="Fútbol 5", capacidad=10),
                Cancha(nombre="Cancha 2", tipo="Fútbol 7", capacidad=14),
            ]
            session.add_all(canchas)
            print("Canchas insertadas.")

        session.commit()

        # ===============================
        # HORARIOS
        # ===============================
        existing_horarios = session.exec(select(Horario)).all()
        cancha = session.exec(select(Cancha)).first()
        if not existing_horarios:
            horarios = [
                Horario(hora_inicio=time(10, 0), hora_fin=time(11, 0), cancha_id=cancha.id),
                Horario(hora_inicio=time(11, 0), hora_fin=time(12, 0), cancha_id=cancha.id),
            ]
            session.add_all(horarios)
            print("Horarios insertados.")
            session.commit()

        # ======= Torneos =======
        existing_torneos = session.exec(select(Torneo)).all()
        if not existing_torneos:
            torneos = [
                Torneo(
                    nombre="Torneo Apertura",
                    fecha_inicio=date(2025, 11, 1),
                    fecha_fin=date(2025, 12, 1),
                    descripcion="Primer torneo de la temporada."
                ),
                Torneo(
                    nombre="Torneo Clausura",
                    fecha_inicio=date(2026, 1, 15),
                    fecha_fin=date(2026, 3, 15),
                    descripcion="Torneo de cierre de temporada."
                ),
            ]
            session.add_all(torneos)
            session.commit()
            print("✅ Torneos insertados.")
        else:
            print("⚠️ Torneos ya existen, no se insertan.")

       # ===============================
        # RESERVAS
        # ===============================
        existing_reservas = session.exec(select(Reserva)).all()
        if not existing_reservas:
            cliente = session.exec(select(Cliente)).first()
            cancha = session.exec(select(Cancha)).first()
            horario = session.exec(select(Horario)).first()
            
            # 🟢 SOLUCIÓN: Usar los atributos de hora del objeto 'horario'
            reservas = [
                Reserva(
                    cliente_id=cliente.id,
                    cancha_id=cancha.id,
                    horario_id=horario.id,
                    fecha=date(2025, 10, 21),
                    # AÑADE ESTAS LÍNEAS:
                    hora_inicio=horario.hora_inicio, # <- Asigna el objeto datetime.time
                    hora_fin=horario.hora_fin       # <- Asigna el objeto datetime.time
                )
            ]
            session.add_all(reservas)
            print("Reservas insertadas.")
            session.commit()

if __name__ == "__main__":
    seed_data()
    print("✅ Base de datos poblada correctamente.")
