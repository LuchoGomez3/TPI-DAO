from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from database import get_session
from src.models.Cancha import Cancha, TipoCancha
from src.schemas.Cancha import CanchaCreate, CanchaUpdate, CanchaResponse
from typing import List, Optional


class CanchasService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_canchas(self) -> List[CanchaResponse]:
        canchas = self.session.exec(
            select(Cancha).order_by(Cancha.nombre)
        ).all()
        return [CanchaResponse.model_validate(cancha) for cancha in canchas]

    def get_cancha(self, id: int) -> CanchaResponse:
        cancha = self.session.get(Cancha, id)
        if not cancha:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")
        return CanchaResponse.model_validate(cancha)

    def create_cancha(self, cancha: CanchaCreate) -> CanchaResponse:
        tipo_cancha = self.session.get(TipoCancha, cancha.tipo_cancha_id)
        if not tipo_cancha:
            raise HTTPException(status_code=400, detail="El tipo de cancha especificado no existe.")

        try:
            new_cancha = Cancha.model_validate(cancha)
            self.session.add(new_cancha)
            self.session.commit()
            self.session.refresh(new_cancha)
            return CanchaResponse.model_validate(new_cancha)
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear cancha: {e}")

    def update_cancha(self, id: int, cancha_data: CanchaUpdate) -> CanchaResponse:
        cancha_obj = self.session.get(Cancha, id)

        if not cancha_obj:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")

        if cancha_data.tipo_cancha_id is not None:
            tipo_cancha = self.session.get(TipoCancha, cancha_data.tipo_cancha_id)
            if not tipo_cancha:
                raise HTTPException(status_code=400, detail="El tipo de cancha especificado no existe.")

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

        self.session.delete(cancha_obj)
        self.session.commit()
