from sqlmodel import Session, select
from database import engine, init_db
from datetime import date, time, datetime, timedelta

from src.models.Cliente import Cliente
from src.models.Cancha import Cancha, TipoCancha
from src.models.Reserva import Reserva, EstadoReserva
from src.models.Horario import Horario
from src.models.Torneo import Torneo
from src.models.Pago import Pago, EstadoPago
from src.models.Busquedas import Servicio


def seed_data():
    init_db()

    with Session(engine) as session:
        print("🌱 Iniciando población de datos...")

        # 1. ESTADOS Y TIPOS
        estados_reserva = ["Pendiente", "Confirmada", "Cancelada"]
        for nombre in estados_reserva:
            if not session.exec(select(EstadoReserva).where(EstadoReserva.nombre == nombre)).first():
                session.add(EstadoReserva(nombre=nombre))

        estados_pago = ["Pendiente", "Pagado", "Reembolsado"]
        for nombre in estados_pago:
            if not session.exec(select(EstadoPago).where(EstadoPago.nombre == nombre)).first():
                session.add(EstadoPago(nombre=nombre))

        tipos_cancha = [
            {"nombre": "F5", "desc": "Fútbol 5"},
            {"nombre": "F7", "desc": "Fútbol 7"},
            {"nombre": "TENIS", "desc": "Tenis"},
            {"nombre": "PADEL", "desc": "Padel"}
        ]
        for tipo in tipos_cancha:
            if not session.exec(select(TipoCancha).where(TipoCancha.nombre == tipo["nombre"])).first():
                session.add(TipoCancha(nombre=tipo["nombre"], descripcion=tipo["desc"]))

        session.commit()

        tipo_f5 = session.exec(select(TipoCancha).where(TipoCancha.nombre == "F5")).first()
        estado_conf = session.exec(select(EstadoReserva).where(EstadoReserva.nombre == "Confirmada")).first()
        estado_pago_ok = session.exec(select(EstadoPago).where(EstadoPago.nombre == "Pagado")).first()

        # 2. CLIENTES
        if not session.exec(select(Cliente)).first():
            clientes = [
                Cliente(nombre="Lionel", apellido="Messi", email="lio@example.com", telefono="11111111"),
                Cliente(nombre="Emiliano", apellido="Martinez", email="dibu@example.com", telefono="22222222"),
            ]
            session.add_all(clientes)
            session.commit()

        cliente_1 = session.exec(select(Cliente)).first()

        # 3. CANCHAS
        if not session.exec(select(Cancha)).first():
            cancha = Cancha(nombre="Cancha 1", tipo_cancha_id=tipo_f5.id)
            session.add(cancha)
            session.commit()

        cancha_1 = session.exec(select(Cancha)).first()

        # 4. HORARIOS
        if not session.exec(select(Horario)).first():
            horarios = [
                Horario(cancha_id=cancha_1.id, hora_inicio=time(18, 0), hora_fin=time(19, 0), disponible=True),
                Horario(cancha_id=cancha_1.id, hora_inicio=time(19, 0), hora_fin=time(20, 0), disponible=True),
            ]
            session.add_all(horarios)
            session.commit()

        horario_ref = session.exec(select(Horario)).first()

        # 5. RESERVA Y PAGO
        if not session.exec(select(Reserva)).first():
            # Creamos reserva (ya no pide pago_id)
            reserva = Reserva(
                cliente_id=cliente_1.id,
                cancha_id=cancha_1.id,
                estado_reserva_id=estado_conf.id,
                horario_id=horario_ref.id,
                fecha=date.today(),
                hora_inicio=horario_ref.hora_inicio,
                hora_fin=horario_ref.hora_fin
            )
            session.add(reserva)
            session.commit()
            session.refresh(reserva)

            # Creamos pago apuntando a la reserva
            pago = Pago(
                reserva_id=reserva.id,
                estado_pago_id=estado_pago_ok.id,
                monto=15000.0,
                fecha_pago=datetime.now()
            )
            session.add(pago)
            session.commit()

            print("✅ Reservas y Pagos insertados correctamente.")


if __name__ == "__main__":
    seed_data()
    print("\n✨ Base de datos poblada exitosamente.")