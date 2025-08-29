# ARQUIVO: backend/app/crud/crud_freight_order.py

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime

# Importações limpas e organizadas
from app.models.freight_order_model import FreightOrder, FreightStatus
from app.models.journey_model import Journey, JourneyType
from app.models.stop_point_model import StopPoint, StopPointStatus
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.models.user_model import User
from app.schemas.freight_order_schema import FreightOrderCreate, FreightOrderUpdate

class CRUDFreightOrder:
    
    async def create_with_stops(self, db: AsyncSession, *, obj_in: FreightOrderCreate, organization_id: int) -> FreightOrder:
        freight_order_data = obj_in.model_dump(exclude={"stop_points"})
        db_freight_order = FreightOrder(**freight_order_data, organization_id=organization_id, status=FreightStatus.OPEN)
        
        for stop_point_data in obj_in.stop_points:
            db_stop_point = StopPoint(**stop_point_data.model_dump())
            db_freight_order.stop_points.append(db_stop_point)
            
        db.add(db_freight_order)
        await db.commit()
        
        # --- CORREÇÃO: Força o carregamento dos relacionamentos para a resposta da API ---
        await db.refresh(db_freight_order, attribute_names=["client", "stop_points"])
        
        return db_freight_order


    async def get(self, db: AsyncSession, *, id: int, organization_id: int) -> FreightOrder | None:
        """Busca uma Ordem de Frete pelo ID, com todos os seus relacionamentos."""
        stmt = (
            select(FreightOrder)
            .where(FreightOrder.id == id, FreightOrder.organization_id == organization_id)
            .options(
                selectinload(FreightOrder.client),
                selectinload(FreightOrder.vehicle),
                selectinload(FreightOrder.driver),
                selectinload(FreightOrder.stop_points),
                selectinload(FreightOrder.journeys)
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi_by_org(self, db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[FreightOrder]:
        """Busca uma lista de Ordens de Frete com seus relacionamentos principais."""
        stmt = (
            select(FreightOrder)
            .where(FreightOrder.organization_id == organization_id)
            .options(
                selectinload(FreightOrder.client),
                selectinload(FreightOrder.vehicle),
                selectinload(FreightOrder.driver),
                # --- INÍCIO DA CORREÇÃO ---
                # Garante que as paradas sejam carregadas junto com a lista
                selectinload(FreightOrder.stop_points)
                # --- FIM DA CORREÇÃO ---
            )
            .order_by(FreightOrder.id.desc())
            .offset(skip).limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    # --- FUNÇÃO QUE FALTAVA ---
    async def get_multi_by_status(self, db: AsyncSession, *, organization_id: int, status: FreightStatus) -> List[FreightOrder]:
        """Busca todas as ordens de frete de uma organização com um status específico."""
        stmt = (
            select(FreightOrder)
            .where(
                FreightOrder.organization_id == organization_id,
                FreightOrder.status == status
            )
            .options(
                selectinload(FreightOrder.client),
                selectinload(FreightOrder.stop_points) # Para o mural, precisamos saber o cliente e as paradas
            )
            .order_by(FreightOrder.scheduled_start_time.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_pending_by_driver(self, db: AsyncSession, *, driver_id: int, organization_id: int) -> List[FreightOrder]:
        """Busca os fretes ATRIBUÍDOS (CLAIMED) ou EM TRÂNSITO de um motorista."""
        stmt = (
            select(FreightOrder)
            .where(
                FreightOrder.driver_id == driver_id,
                FreightOrder.organization_id == organization_id,
                FreightOrder.status.in_([FreightStatus.CLAIMED, FreightStatus.IN_TRANSIT])
            )
            .options(
                selectinload(FreightOrder.client),
                selectinload(FreightOrder.vehicle),
                selectinload(FreightOrder.stop_points)
            )
            .order_by(FreightOrder.scheduled_start_time)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(self, db: AsyncSession, *, db_obj: FreightOrder, obj_in: FreightOrderUpdate) -> FreightOrder:
        """Atualiza uma Ordem de Frete (ex: alocação manual de gestor)."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
        
    async def claim_order(self, db: AsyncSession, *, order: FreightOrder, driver: User, vehicle: Vehicle) -> FreightOrder:
        """Atribui uma ordem de frete a um motorista e veículo."""
        if order.status != FreightStatus.OPEN:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este frete não está mais aberto para atribuição.")
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O veículo selecionado não está disponível.")

        order.driver_id = driver.id
        order.vehicle_id = vehicle.id
        order.status = FreightStatus.CLAIMED
        db.add(order)
        
        vehicle.status = VehicleStatus.IN_USE
        db.add(vehicle)
        
        await db.commit()
        await db.refresh(order, attribute_names=["client", "vehicle", "driver", "stop_points"])
        return order

    async def start_journey_for_stop(self, db: AsyncSession, *, order: FreightOrder, stop: StopPoint, vehicle: Vehicle) -> Journey:
        """Inicia uma nova Journey (trecho) para uma parada de um frete."""
        if order.status == FreightStatus.CLAIMED:
            order.status = FreightStatus.IN_TRANSIT
            db.add(order)
            
        new_journey = Journey(
            vehicle_id=vehicle.id, driver_id=order.driver_id, organization_id=order.organization_id,
            freight_order_id=order.id, start_mileage=vehicle.current_km,
            start_engine_hours=vehicle.current_engine_hours, start_time=datetime.utcnow(),
            is_active=True, trip_type=JourneyType.FREE_ROAM
        )
        db.add(new_journey)
        await db.commit()
        await db.refresh(new_journey)
        return new_journey

    async def complete_stop_point(self, db: AsyncSession, *, order: FreightOrder, stop: StopPoint, journey: Journey, end_mileage: int) -> StopPoint:
        """Marca uma parada como concluída e finaliza o trecho (Journey)."""
        stop.status = StopPointStatus.COMPLETED
        stop.actual_arrival_time = datetime.utcnow()
        db.add(stop)
        
        journey.is_active = False
        journey.end_time = datetime.utcnow()
        if end_mileage is not None:
             journey.end_mileage = end_mileage
        db.add(journey)
        
        if order.vehicle and end_mileage is not None:
            order.vehicle.current_km = end_mileage
            db.add(order.vehicle)

        all_stops_completed = all(s.status == StopPointStatus.COMPLETED for s in order.stop_points)
        if all_stops_completed:
            order.status = FreightStatus.DELIVERED
            # Também libera o veículo
            if order.vehicle:
                order.vehicle.status = VehicleStatus.AVAILABLE
                db.add(order.vehicle)
            db.add(order)
            
        await db.commit()
        await db.refresh(stop)
        return stop

# Instância única que será usada em toda a aplicação
freight_order = CRUDFreightOrder()