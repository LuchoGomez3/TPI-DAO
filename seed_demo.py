import random
from datetime import timedelta, date, time, datetime
from sqlmodel import Session, select
from database import engine, init_db
from src.models.Cliente import Cliente
from src.models.Cancha import Cancha, TipoCancha
from src.models.Reserva import Reserva, EstadoReserva
from src.models.Horario import Horario
from src.models.Pago import Pago, EstadoPago

# Configuración
CANTIDAD_RESERVAS = 150
DIAS_ATRAS = 90  # Generar historia de los últimos 3 meses


def seed_heavy():
    init_db()
    with Session(engine) as session:
        print("🌱 Iniciando población MASIVA de datos...")

        # --- 1. Asegurar Estados y Tipos ---
        estados_reserva = ["Pendiente", "Confirmada", "Cancelada"]
        for nombre in estados_reserva:
            if not session.exec(select(EstadoReserva).where(EstadoReserva.nombre == nombre)).first():
                session.add(EstadoReserva(nombre=nombre))

        estados_pago = ["Pendiente", "Pagado", "Reembolsado"]
        for nombre in estados_pago:
            if not session.exec(select(EstadoPago).where(EstadoPago.nombre == nombre)).first():
                session.add(EstadoPago(nombre=nombre))

        tipos_data = [
            ("F5", "Fútbol 5"), ("F7", "Fútbol 7"),
            ("TENIS", "Tenis"), ("PADEL", "Padel"),
            ("BASQUET", "Basquet")
        ]
        for nombre, desc in tipos_data:
            if not session.exec(select(TipoCancha).where(TipoCancha.nombre == nombre)).first():
                session.add(TipoCancha(nombre=nombre, descripcion=desc))

        session.commit()

        # Recuperar objetos base
        estado_conf = session.exec(select(EstadoReserva).where(EstadoReserva.nombre == "Confirmada")).first()
        estado_pagado = session.exec(select(EstadoPago).where(EstadoPago.nombre == "Pagado")).first()

        # --- 2. Crear Clientes Famosos ---
        nombres = [
            ("Lionel", "Messi"), ("Cristiano", "Ronaldo"), ("Neymar", "Junior"),
            ("Kylian", "Mbappe"), ("Luka", "Modric"), ("Erling", "Haaland"),
            ("Vinicius", "Junior"), ("Kevin", "De Bruyne"), ("Harry", "Kane"),
            ("Sergio", "Ramos")
        ]

        clientes_db = []
        for nom, ape in nombres:
            cli = session.exec(select(Cliente).where(Cliente.nombre == nom)).first()
            if not cli:
                cli = Cliente(nombre=nom, apellido=ape, email=f"{nom.lower()}@goal.com", telefono="555-0000")
                session.add(cli)
                session.commit()
                session.refresh(cli)
            clientes_db.append(cli)

        # --- 3. Crear Varias Canchas ---
        canchas_data = [
            ("Estadio Lusail", "F5"), ("Camp Nou", "F7"),
            ("Roland Garros", "TENIS"), ("Wimbledon", "TENIS"),
            ("Padel Center", "PADEL")
        ]

        canchas_db = []
        for nom_cancha, tipo_nombre in canchas_data:
            cancha = session.exec(select(Cancha).where(Cancha.nombre == nom_cancha)).first()
            tipo = session.exec(select(TipoCancha).where(TipoCancha.nombre == tipo_nombre)).first()

            if not cancha:
                cancha = Cancha(nombre=nom_cancha, tipo_cancha_id=tipo.id)
                session.add(cancha)
                session.commit()
                session.refresh(cancha)

                # Crear Horarios para la cancha (14hs a 23hs)
                for h in range(14, 23):
                    session.add(Horario(
                        cancha_id=cancha.id,
                        hora_inicio=time(h, 0),
                        hora_fin=time(h + 1, 0),
                        disponible=True
                    ))
                session.commit()

            canchas_db.append(cancha)

        # --- 4. Generar Reservas Aleatorias ---
        print(f"🎲 Generando {CANTIDAD_RESERVAS} reservas aleatorias...")

        count = 0
        errores = 0

        # Rango de fechas: desde hace 3 meses hasta hoy
        fecha_inicio_historia = date.today() - timedelta(days=DIAS_ATRAS)

        while count < CANTIDAD_RESERVAS:
            # Randomizar datos
            cliente = random.choice(clientes_db)
            cancha = random.choice(canchas_db)
            dias_random = random.randint(0, DIAS_ATRAS)
            fecha_reserva = fecha_inicio_historia + timedelta(days=dias_random)

            # Hora random entre 14 y 22
            hora_int = random.randint(14, 22)
            hora_inicio = time(hora_int, 0)
            hora_fin = time(hora_int + 1, 0)

            # Buscar horario ID correspondiente
            horario = session.exec(select(Horario).where(
                Horario.cancha_id == cancha.id,
                Horario.hora_inicio == hora_inicio
            )).first()

            if not horario: continue  # Si no hay horario configurado, saltar

            # Validar que no exista ya (superposición simple)
            existe = session.exec(select(Reserva).where(
                Reserva.cancha_id == cancha.id,
                Reserva.fecha == fecha_reserva,
                Reserva.hora_inicio == hora_inicio
            )).first()

            if not existe:
                # Crear Reserva
                nueva_reserva = Reserva(
                    cliente_id=cliente.id,
                    cancha_id=cancha.id,
                    estado_reserva_id=estado_conf.id,
                    horario_id=horario.id,
                    fecha=fecha_reserva,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin
                )
                session.add(nueva_reserva)
                session.commit()
                session.refresh(nueva_reserva)

                # Crear Pago (simulando ingresos)
                pago = Pago(
                    reserva_id=nueva_reserva.id,
                    estado_pago_id=estado_pagado.id,
                    monto=random.choice([15000.0, 20000.0, 12000.0]),
                    fecha_pago=datetime.combine(fecha_reserva, hora_inicio)
                )
                session.add(pago)
                session.commit()

                count += 1
                if count % 20 == 0:
                    print(f"   ... {count} reservas creadas")
            else:
                errores += 1
                # Si hay muchas colisiones, simplemente intentamos de nuevo en el loop

    print(f"✅ ¡Terminado! {count} reservas históricas generadas.")


if __name__ == "__main__":
    seed_heavy()