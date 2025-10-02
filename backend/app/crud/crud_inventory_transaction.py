from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List, Optional

from app.models.inventory_transaction_model import InventoryTransaction, TransactionType
from app.models.part_model import Part


async def _create_transaction_no_commit(
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
    Prepara uma nova transação de inventário e atualiza o estoque, mas NÃO faz o commit.
    Retorna o objeto de transação para ser usado em uma transação maior.
    """
    part = await db.get(Part, part_id)
    if not part:
        raise ValueError("Peça não encontrada.")

    if transaction_type != TransactionType.AJUSTE_MANUAL and (part.stock + quantity_change < 0):
        raise ValueError("Estoque insuficiente para esta operação.")

    part.stock += quantity_change

    db_transaction = InventoryTransaction(
        part_id=part_id,
        user_id=user_id,
        transaction_type=transaction_type,
        quantity_change=quantity_change,
        stock_after_transaction=part.stock,
        notes=notes,
        related_vehicle_id=related_vehicle_id,
        related_user_id=related_user_id,
    )

    db.add(part)
    db.add(db_transaction)

    await db.flush()  # Garante que o ID da transação seja gerado e o part.stock seja atualizado na sessão
    
    return db_transaction


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
    Cria uma nova transação de inventário como uma operação atômica e completa.
    """
    db_transaction = await _create_transaction_no_commit(
        db=db,
        part_id=part_id,
        user_id=user_id,
        transaction_type=transaction_type,
        quantity_change=quantity_change,
        notes=notes,
        related_vehicle_id=related_vehicle_id,
        related_user_id=related_user_id,
    )
    
    transaction_id = db_transaction.id
    
    await db.commit()
    
    stmt = (
        select(InventoryTransaction)
        .where(InventoryTransaction.id == transaction_id)
        .options(
            selectinload(InventoryTransaction.user),
            selectinload(InventoryTransaction.part),
            selectinload(InventoryTransaction.related_user),
            selectinload(InventoryTransaction.related_vehicle),
        )
    )
    result = await db.execute(stmt)
    created_transaction = result.scalar_one()
    
    return created_transaction


async def get_transactions_by_part_id(
    db: AsyncSession, *, part_id: int, skip: int = 0, limit: int = 100
) -> List[InventoryTransaction]:
    """Retorna o histórico de transações para uma peça específica."""
    stmt = (
        select(InventoryTransaction)
        .where(InventoryTransaction.part_id == part_id)
        .order_by(InventoryTransaction.timestamp.desc())
        .options(
            selectinload(InventoryTransaction.user),
            selectinload(InventoryTransaction.related_vehicle),
            selectinload(InventoryTransaction.related_user),
            selectinload(InventoryTransaction.part)
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
            selectinload(InventoryTransaction.user),
            selectinload(InventoryTransaction.part),
            selectinload(InventoryTransaction.related_user),
            selectinload(InventoryTransaction.related_vehicle)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
