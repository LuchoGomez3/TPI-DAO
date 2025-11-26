from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from database import get_session
from src.models.Torneo import Torneo, CanchaTorneoLink
from src.models.Cancha import Cancha
from src.schemas.Torneo import TorneoCreate, TorneoUpdate, TorneoResponse
from src.schemas.Cancha import CanchaResponse
from typing import List


class TorneosService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_torneos(self) -> List[TorneoResponse]:
        torneos = self.session.exec(select(Torneo)).all()
        return [TorneoResponse.model_validate(t) for t in torneos]

    def get_torneo(self, id: int) -> TorneoResponse:
        torneo = self.session.get(Torneo, id)
        if not torneo:
            raise HTTPException(status_code=404, detail="Torneo no encontrado")
        return TorneoResponse.model_validate(torneo)

    def create_torneo(self, torneo_data: TorneoCreate) -> TorneoResponse:
        try:
            new_torneo = Torneo.model_validate(torneo_data)
            self.session.add(new_torneo)
            self.session.commit()
            self.session.refresh(new_torneo)
            return TorneoResponse.model_validate(new_torneo)
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def update_torneo(self, id: int, torneo_data: TorneoUpdate) -> TorneoResponse:
        torneo = self.session.get(Torneo, id)
        if not torneo:
            raise HTTPException(status_code=404, detail="Torneo no encontrado")

        data = torneo_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(torneo, key, value)

        self.session.add(torneo)
        self.session.commit()
        self.session.refresh(torneo)
        return TorneoResponse.model_validate(torneo)

    def delete_torneo(self, id: int):
        torneo = self.session.get(Torneo, id)
        if not torneo:
            raise HTTPException(status_code=404, detail="Torneo no encontrado")
        self.session.delete(torneo)
        self.session.commit()

    def agregar_cancha_torneo(self, torneo_id: int, cancha_id: int) -> CanchaResponse:
        # (Tu lógica existente estaba bien, solo asegúrate de devolver CanchaResponse)
        # ... lógica de link ...
        link = CanchaTorneoLink(torneo_id=torneo_id, cancha_id=cancha_id)
        self.session.add(link)
        self.session.commit()

        cancha = self.session.get(Cancha, cancha_id)
        return CanchaResponse.model_validate(cancha)

    def listar_canchas_torneo(self, torneo_id: int) -> List[CanchaResponse]:
        torneo = self.session.get(Torneo, torneo_id)
        if not torneo:
            raise HTTPException(status_code=404, detail="Torneo no encontrado")
        return [CanchaResponse.model_validate(c) for c in torneo.canchas]