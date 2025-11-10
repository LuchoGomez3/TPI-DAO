from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from database import get_session
from src.models.Torneo import Torneo, CanchaTorneoLink
from src.models.Cancha import Cancha
from src.schemas.Torneo import TorneoCreate, TorneoUpdate, TorneoResponse
from typing import List


class TorneosService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_torneos(self) -> List[TorneoResponse]:
        torneos = self.session.exec(select(Torneo)).all()
        return [TorneoResponse.model_validate(t) for t in torneos]

    def create_torneo(self, torneo_data: TorneoCreate) -> TorneoResponse:
        try:
            new_torneo = Torneo.model_validate(torneo_data)
            self.session.add(new_torneo)
            self.session.commit()
            self.session.refresh(new_torneo)
            return TorneoResponse.model_validate(new_torneo)
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear torneo: {e}")

    def agregar_cancha_torneo(self, torneo_id: int, cancha_id: int) -> Cancha:
        torneo = self.session.get(Torneo, torneo_id)
        cancha = self.session.get(Cancha, cancha_id)

        if not torneo or not cancha:
            raise HTTPException(status_code=404, detail="Torneo o Cancha no encontrado.")

        link = CanchaTorneoLink(torneo_id=torneo_id, cancha_id=cancha_id)

        existing_link = self.session.get(CanchaTorneoLink, primary_key=(cancha_id, torneo_id))
        if existing_link:
            raise HTTPException(status_code=409, detail="La cancha ya está asociada a este torneo.")

        try:
            self.session.add(link)
            self.session.commit()
            return cancha
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Error al agregar cancha al torneo: {e}")
