from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import date  # <-- 1. Importar 'date' para conversão

from app.models.fine_model import Fine, FineStatus
from app.models.vehicle_cost_model import VehicleCost, CostType
from app.schemas.fine_schema import FineCreate, FineUpdate


# (As funções create, get, get_multi_by_org, get_multi_by_driver não precisam de mudança)
# Vamos pular para a função 'update'

async def create(db: AsyncSession, *, fine_in: FineCreate, organization_id: int) -> Fine:
    """Cria uma nova multa e seu custo vinculado de forma simples."""
    
    db_fine = Fine(**fine_in.model_dump(), organization_id=organization_id)
    
    db_cost = VehicleCost(
        description=f"Multa: {db_fine.description}",
        amount=db_fine.value,
        date=db_fine.date,
        cost_type=CostType.MULTA,
        vehicle_id=db_fine.vehicle_id,
        organization_id=organization_id
    )

    db_fine.cost = db_cost 
    
    db.add(db_fine)
    
    return db_fine

async def get(db: AsyncSession, *, fine_id: int, organization_id: int) -> Optional[Fine]:
    """Busca uma multa específica pelo ID, garantindo que pertence à organização e carregando o custo."""
    stmt = select(Fine).where(Fine.id == fine_id, Fine.organization_id == organization_id)
    # 'lazy="selectin"' no modelo fine_model.py já deve cuidar de carregar o custo
    # Mas podemos garantir o 'vehicle' e 'driver' aqui
    stmt = stmt.options(
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

async def get_multi_by_driver(
    db: AsyncSession, *, driver_id: int, organization_id: int, skip: int = 0, limit: int = 100
) -> List[Fine]:
    """Retorna uma lista de multas de um motorista específico dentro de uma organização."""
    stmt = (
        select(Fine)
        .where(Fine.organization_id == organization_id, Fine.driver_id == driver_id)
        .order_by(Fine.date.desc())
        .options(selectinload(Fine.vehicle), selectinload(Fine.driver))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update(
    db: AsyncSession, 
    *, 
    db_fine: Fine, 
    fine_in_dict: Dict[str, Any]
) -> Fine:
    """Atualiza os dados de uma multa e seu custo associado (usando um dict)."""
    
    update_data = fine_in_dict
    
    # --- 2. CORREÇÃO DE TIPO (O PROBLEMA ESTÁ AQUI) ---
    # O JSON nos dá 'date' como a string "2025-11-12".
    # SQLAlchemy espera um objeto datetime.date.
    if 'date' in update_data and isinstance(update_data['date'], str):
        try:
            # Converte a string "YYYY-MM-DD" em um objeto date
            update_data['date'] = date.fromisoformat(update_data['date'])
        except (ValueError, TypeError):
            # Se o formato for inválido ou nulo, remove para não quebrar
            del update_data['date']

    # O JSON nos dá 'status' como a string "Pendente".
    # SQLAlchemy espera o Enum FineStatus.PENDING.
    if 'status' in update_data and isinstance(update_data['status'], str):
        try:
            # Converte a string "Pendente" de volta para o objeto Enum
            update_data['status'] = FineStatus(update_data['status'])
        except ValueError:
            # Se o status enviado ("MeuStatus") não existir no Enum, remove
            del update_data['status']
    # --- FIM DA CORREÇÃO ---

    
    # 1. Atualiza os campos da multa (agora com os tipos corretos)
    for field, value in update_data.items():
        if hasattr(db_fine, field):
            setattr(db_fine, field, value)
        
    # 2. Atualiza os campos do custo vinculado (agora com tipos corretos)
    if db_fine.cost:
        if 'description' in update_data:
            db_fine.cost.description = f"Multa: {update_data['description']}"
        if 'value' in update_data:
            db_fine.cost.amount = update_data['value']
        if 'date' in update_data:
            # update_data['date'] já é um objeto date aqui
            db_fine.cost.date = update_data['date']
        if 'vehicle_id' in update_data:
            db_fine.cost.vehicle_id = update_data['vehicle_id']
        
        db.add(db_fine.cost) # Adiciona o custo atualizado à sessão

    db.add(db_fine) # Adiciona a multa atualizada à sessão
    
    # O endpoint fará o commit e refresh
    return db_fine


async def remove(db: AsyncSession, *, db_fine: Fine) -> Fine:
    """
    Remove uma multa do banco de dados. 
    O custo associado será removido AUTOMATICAMENTE pelo 'cascade'.
    """
    await db.delete(db_fine)
    
    # O endpoint fará o commit
    return db_fine