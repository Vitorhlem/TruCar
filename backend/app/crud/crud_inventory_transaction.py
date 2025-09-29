from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.inventory_transaction_model import InventoryTransaction, TransactionType
from app.models.part_model import Part

async def create_transaction(
    db: AsyncSession,
    *,
    part_id: int,
    user_id: int,
    transaction_type: TransactionType,
    quantity_change: int,
    notes: Optional[str] = None,
    related_vehicle_id: Optional[int] = None,
    related_user_id: Optional[int] = None
) -> InventoryTransaction:
    """
    Cria uma nova transação de inventário e atualiza o estoque da peça.
    """
    part = await db.get(Part, part_id)
    if not part:
        raise ValueError("Peça não encontrada.")

    # Atualiza o estoque da peça
    part.stock += quantity_change
    
    db_transaction = InventoryTransaction(
        part_id=part_id,
        user_id=user_id,
        transaction_type=transaction_type,
        quantity_change=quantity_change,
        stock_after_transaction=part.stock,
        notes=notes,
        related_vehicle_id=related_vehicle_id,
        related_user_id=related_user_id
    )
    
    db.add(part)
    db.add(db_transaction)
    await db.commit()

    # --- CORREÇÃO APLICADA AQUI ---
    # Após salvar, damos um "refresh" no objeto e pedimos para que o SQLAlchemy
    # carregue (popule) os relacionamentos necessários para a resposta da API.
    await db.refresh(db_transaction, ["user", "related_vehicle", "related_user"])
    # --- FIM DA CORREÇÃO ---

    return db_transaction

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
            selectinload(InventoryTransaction.related_user)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()