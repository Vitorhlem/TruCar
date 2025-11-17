from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List, Optional

from app.models.inventory_transaction_model import InventoryTransaction, TransactionType
from app.models.part_model import Part, InventoryItem, InventoryItemStatus # <-- Importar
from app.models.user_model import User 


async def create_transaction(
    db: AsyncSession,
    *,
    part_id: int,
    user_id: int,
    transaction_type: TransactionType,
    quantity_change: int,
    notes: Optional[str] = None,
    related_vehicle_id: Optional[int] = None,
    related_user_id: Optional[int] = None,
) -> InventoryTransaction:
    """
    Cria uma nova transação, faz o commit e retorna o objeto completo
    com todas as relações carregadas para garantir uma resposta de API válida.
    """
    
    stmt = (
        select(InventoryTransaction)
        .where(InventoryTransaction.id == transaction_id) # 'transaction_id' viria de algum lugar
        .options(
            selectinload(InventoryTransaction.user).selectinload(User.organization),
            selectinload(InventoryTransaction.related_user).selectinload(User.organization),
            selectinload(InventoryTransaction.related_vehicle),
            selectinload(InventoryTransaction.item),
            
            selectinload(InventoryTransaction.part_template).selectinload(Part.items)
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_transactions_by_part_id(
    db: AsyncSession, *, part_id: int, skip: int = 0, limit: int = 100
) -> List[InventoryTransaction]:
    """Retorna o histórico de transações para todos os itens de um Part (template)."""
    stmt = (
        select(InventoryTransaction)
        .where(InventoryTransaction.part_id == part_id) # Filtra pelo part_id (template)
        .order_by(InventoryTransaction.timestamp.desc())
        .options(
            selectinload(InventoryTransaction.user).selectinload(User.organization),
            selectinload(InventoryTransaction.related_vehicle),
            selectinload(InventoryTransaction.related_user).selectinload(User.organization),
            selectinload(InventoryTransaction.item),
            
            selectinload(InventoryTransaction.part_template).selectinload(Part.items)

        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_transactions_by_vehicle_id(
    db: AsyncSession, *, vehicle_id: int, skip: int = 0, limit: int = 100
) -> List[InventoryTransaction]:
    """Retorna o histórico de transações para um veículo específico."""
    stmt = (
        select(InventoryTransaction)
        .where(InventoryTransaction.related_vehicle_id == vehicle_id)
        .order_by(InventoryTransaction.timestamp.desc())
        .options(
            selectinload(InventoryTransaction.user).selectinload(User.organization),
            selectinload(InventoryTransaction.related_user).selectinload(User.organization),
            selectinload(InventoryTransaction.related_vehicle),
            selectinload(InventoryTransaction.item),
            
            selectinload(InventoryTransaction.part_template).selectinload(Part.items)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()