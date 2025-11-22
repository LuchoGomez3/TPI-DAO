# src/service/Horario.py
from sqlmodel import Session, select, and_, or_
from fastapi import Depends, HTTPException
from database import get_session
from src.models.Horario import Horario
from src.schemas.Horario import HorarioCreate, HorarioUpdate, HorarioResponse
from src.models.Cancha import Cancha  # Para validar la FK
from typing import List, Optional
from datetime import time


class HorariosService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    # Lógica de validación de superposición de horarios (clave para el proyecto)
    def _check_overlap(self, cancha_id: int, hora_inicio: time, hora_fin: time, horario_id: Optional[int] = None):
        # La condición busca cualquier horario existente que se superponga con el nuevo.
        # Superposición = (inicio_existente < fin_nuevo) AND (fin_existente > inicio_nuevo)
        query = select(Horario).where(
            Horario.cancha_id == cancha_id,
            Horario.hora_inicio < hora_fin,
            Horario.hora_fin > hora_inicio
        )
        if horario_id:
            # Excluir el horario que se está actualizando
            query = query.where(Horario.id != horario_id)

        overlap_horario = self.session.exec(query).first()
        if overlap_horario:
            raise HTTPException(
                status_code=409,
                detail=f"Horario se superpone con el horario existente {overlap_horario.id} ({overlap_horario.hora_inicio} a {overlap_horario.hora_fin})"
            )

    def get_horarios(self, cancha_id: int) -> List[HorarioResponse]:
        cancha = self.session.get(Cancha, cancha_id)
        if not cancha:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")

        horarios = self.session.exec(
            select(Horario).where(Horario.cancha_id == cancha_id).order_by(Horario.hora_inicio)
        ).all()
        return [HorarioResponse.model_validate(h) for h in horarios]

    def create_horario_cancha(self, cancha_id: int, horario_data: HorarioCreate) -> HorarioResponse:
        cancha = self.session.get(Cancha, cancha_id)
        if not cancha:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")

        # 1. Validar superposición
        self._check_overlap(cancha_id, horario_data.hora_inicio, horario_data.hora_fin)

        try:
            new_horario = Horario.model_validate(horario_data, update={'cancha_id': cancha_id})
            self.session.add(new_horario)
            self.session.commit()
            self.session.refresh(new_horario)
            return HorarioResponse.model_validate(new_horario)
        except HTTPException:
            raise
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear horario: {e}")

    def update_horario_cancha(self, horario_id: int, horario_data: HorarioUpdate) -> HorarioResponse:
        horario_obj = self.session.get(Horario, horario_id)

        if not horario_obj:
            raise HTTPException(status_code=404, detail="Horario no encontrado")

        # Aplicar datos de actualización para validar superposición con los valores correctos
        update_data = horario_data.model_dump(exclude_unset=True)
        hora_inicio = update_data.get('hora_inicio', horario_obj.hora_inicio)
        hora_fin = update_data.get('hora_fin', horario_obj.hora_fin)

        # 1. Validar superposición (excluyendo el propio horario)
        self._check_overlap(horario_obj.cancha_id, hora_inicio, hora_fin, horario_id)

        for key, value in update_data.items():
            setattr(horario_obj, key, value)

        self.session.add(horario_obj)
        self.session.commit()
        self.session.refresh(horario_obj)
        return HorarioResponse.model_validate(horario_obj)

    def delete_horario_cancha(self, horario_id: int) -> None:
        horario_obj = self.session.get(Horario, horario_id)
        if not horario_obj:
            raise HTTPException(status_code=404, detail="Horario no encontrado")

        # Opcional: Agregar lógica para verificar que no haya reservas futuras asociadas.

        self.session.delete(horario_obj)
        self.session.commit()