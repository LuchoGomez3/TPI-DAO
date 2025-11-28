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
            # Aquí se disparan las validaciones del Modelo (Fechas y Nombre único)
            new_torneo = Torneo.model_validate(torneo_data)

            self.session.add(new_torneo)
            self.session.commit()
            self.session.refresh(new_torneo)
            return TorneoResponse.model_validate(new_torneo)

        except ValueError as ve:
            # Capturamos errores de validación (Nombre duplicado o Fechas mal)
            self.session.rollback()
            raise HTTPException(status_code=409, detail=str(ve))
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def update_torneo(self, id: int, torneo_data: TorneoUpdate) -> TorneoResponse:
        torneo = self.session.get(Torneo, id)
        if not torneo:
            raise HTTPException(status_code=404, detail="Torneo no encontrado")

        try:
            data = torneo_data.model_dump(exclude_unset=True)
            for key, value in data.items():
                setattr(torneo, key, value)

            # Al hacer add(), SQLModel validará antes del commit
            self.session.add(torneo)
            self.session.commit()
            self.session.refresh(torneo)
            return TorneoResponse.model_validate(torneo)

        except ValueError as ve:
            self.session.rollback()
            raise HTTPException(status_code=409, detail=str(ve))
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def delete_torneo(self, id: int):
        torneo = self.session.get(Torneo, id)
        if not torneo:
            raise HTTPException(status_code=404, detail="Torneo no encontrado")
        self.session.delete(torneo)
        self.session.commit()

    def agregar_cancha_torneo(self, torneo_id: int, cancha_id: int) -> CanchaResponse:
        # Validamos existencia de ambos
        if not self.session.get(Torneo, torneo_id):
            raise HTTPException(status_code=404, detail="Torneo no encontrado")

        cancha = self.session.get(Cancha, cancha_id)
        if not cancha:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")

        # Evitar duplicados en la relación
        existing_link = self.session.exec(
            select(CanchaTorneoLink).where(
                CanchaTorneoLink.torneo_id == torneo_id,
                CanchaTorneoLink.cancha_id == cancha_id
            )
        ).first()

        if existing_link:
            raise HTTPException(status_code=409, detail="Esta cancha ya está asignada a este torneo.")

        link = CanchaTorneoLink(torneo_id=torneo_id, cancha_id=cancha_id)
        self.session.add(link)
        self.session.commit()

        return CanchaResponse.model_validate(cancha)

    def listar_canchas_torneo(self, torneo_id: int) -> List[CanchaResponse]:
        torneo = self.session.get(Torneo, torneo_id)
        if not torneo:
            raise HTTPException(status_code=404, detail="Torneo no encontrado")
        return [CanchaResponse.model_validate(c) for c in torneo.canchas]