# Em backend/app/crud/crud_fine.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.fine_model import Fine, FineStatus
from app.schemas.fine_schema import FineCreate, FineUpdate
from app.schemas.vehicle_cost_schema import VehicleCostCreate # <-- 1. IMPORTAR
from app.models.vehicle_cost_model import CostType           # <-- 2. IMPORTAR
from . import crud_vehicle_cost        


async def create(db: AsyncSession, *, fine_in: FineCreate, organization_id: int) -> Fine:
    """Cria uma nova multa e, simultaneamente, cria um lançamento de custo correspondente."""
    db_fine = Fine(**fine_in.model_dump(), organization_id=organization_id)
    db.add(db_fine)
    
    # Cria o custo provisionado no momento em que a multa é registrada
    cost_payload = VehicleCostCreate(
        description=f"Multa: {db_fine.description}",
        amount=db_fine.value,
        date=db_fine.date,
        cost_type=CostType.MULTA
    )
    # Chama o CRUD de custos, mas não faz o commit final aqui
    await crud_vehicle_cost.create_cost(
        db=db,
        obj_in=cost_payload,
        vehicle_id=db_fine.vehicle_id,
        organization_id=organization_id,
        commit=False 
    )
    
    await db.commit() # O commit salva tanto a multa quanto o custo
    await db.refresh(db_fine, ["vehicle", "driver"])
    
    return db_fine

async def get(db: AsyncSession, *, fine_id: int, organization_id: int) -> Optional[Fine]:
    """Busca uma multa específica pelo ID, garantindo que pertence à organização."""
    stmt = select(Fine).where(Fine.id == fine_id, Fine.organization_id == organization_id).options(
        selectinload(Fine.vehicle),
        selectinload(Fine.driver)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_multi_by_org(
    db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100
) -> List[Fine]:
    """Retorna uma lista de todas as multas de uma organização."""
    stmt = (
        select(Fine)
        .where(Fine.organization_id == organization_id)
        .order_by(Fine.date.desc())
        .options(selectinload(Fine.vehicle), selectinload(Fine.driver))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update(db: AsyncSession, *, db_fine: Fine, fine_in: FineUpdate) -> Fine:
    """Atualiza os dados de uma multa."""
    # A lógica de ATUALIZAR o custo associado é mais complexa e
    # exigiria uma coluna de ligação (ex: fine.cost_id).
    # Por agora, a criação do custo no registro já resolve a principal necessidade.
    update_data = fine_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_fine, field, value)
    db.add(db_fine)
    await db.commit()
    await db.refresh(db_fine, ["vehicle", "driver"])
    return db_fine

async def remove(db: AsyncSession, *, db_fine: Fine) -> Fine:
    """Remove uma multa do banco de dados."""
    await db.delete(db_fine)
    await db.commit()
    return db_fine