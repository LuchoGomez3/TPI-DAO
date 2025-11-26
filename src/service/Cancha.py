from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from database import get_session
from src.models.Cancha import Cancha, TipoCancha
from src.models.Horario import Horario  # <--- Importamos Horario
from src.schemas.Cancha import CanchaCreate, CanchaUpdate, CanchaResponse
from typing import List, Optional
from datetime import time


class CanchasService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_canchas(self) -> List[CanchaResponse]:
        canchas = self.session.exec(select(Cancha).order_by(Cancha.nombre)).all()
        return [CanchaResponse.model_validate(cancha) for cancha in canchas]

    def get_cancha(self, id: int) -> CanchaResponse:
        cancha = self.session.get(Cancha, id)
        if not cancha:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")
        return CanchaResponse.model_validate(cancha)

    def create_cancha(self, cancha_data: CanchaCreate) -> CanchaResponse:
        # 1. Validar tipo
        tipo_cancha = self.session.get(TipoCancha, cancha_data.tipo_cancha_id)
        if not tipo_cancha:
            raise HTTPException(status_code=400, detail="El tipo de cancha especificado no existe.")

        try:
            # 2. Crear la Cancha
            new_cancha = Cancha.model_validate(cancha_data)
            self.session.add(new_cancha)
            self.session.commit()
            self.session.refresh(new_cancha)

            # 3. --- MAGIA: GENERAR HORARIOS AUTOMÁTICOS ---
            # Creamos slots de 1 hora desde las 14:00 hasta las 23:00
            horarios_nuevos = []
            for hora in range(14, 23):
                slot = Horario(
                    cancha_id=new_cancha.id,
                    hora_inicio=time(hora, 0),
                    hora_fin=time(hora + 1, 0),
                    disponible=True
                )
                horarios_nuevos.append(slot)

            self.session.add_all(horarios_nuevos)
            self.session.commit()
            # -----------------------------------------------

            return CanchaResponse.model_validate(new_cancha)
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error creando cancha: {e}")
            raise HTTPException(status_code=500, detail=f"Error al crear cancha: {e}")

    def update_cancha(self, id: int, cancha_data: CanchaUpdate) -> CanchaResponse:
        cancha_obj = self.session.get(Cancha, id)
        if not cancha_obj:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")

        update_data = cancha_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(cancha_obj, key, value)

        self.session.add(cancha_obj)
        self.session.commit()
        self.session.refresh(cancha_obj)
        return CanchaResponse.model_validate(cancha_obj)

    def delete_cancha(self, id: int) -> None:
        cancha_obj = self.session.get(Cancha, id)
        if not cancha_obj:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")

        # Nota: Si intentas borrar una cancha con reservas, SQL podría quejarse por FK.
        # Idealmente deberías borrar sus horarios y reservas antes, o usar cascade en la DB.
        self.session.delete(cancha_obj)
        self.session.commit()