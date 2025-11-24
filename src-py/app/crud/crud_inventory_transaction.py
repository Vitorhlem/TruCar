from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List, Optional

from app.models.inventory_transaction_model import InventoryTransaction, TransactionType
from app.models.part_model import Part, InventoryItem
from app.models.user_model import User 

# --- FUNÇÕES DE CRIAÇÃO ---

async def _create_transaction_no_commit(
    db: AsyncSession,
    *,
    part_id: int,
    user_id: int,
    transaction_type: TransactionType,
    item_id: int,
    quantity_change: int = 0,
    notes: Optional[str] = None,
    related_vehicle_id: Optional[int] = None,
) -> InventoryTransaction:
    """
    Cria o objeto da transação.
    """
    db_obj = InventoryTransaction(
        part_id=part_id,
        user_id=user_id,
        transaction_type=transaction_type,
        notes=notes,
        related_vehicle_id=related_vehicle_id,
        item_id=item_id
    )
    db.add(db_obj)
    return db_obj

async def create_transaction(
    db: AsyncSession,
    *,
    part_id: int,
    user_id: int,
    transaction_type: TransactionType,
    item_id: int,
    quantity_change: int = 0,
    notes: Optional[str] = None,
    related_vehicle_id: Optional[int] = None,
    related_user_id: Optional[int] = None,
) -> InventoryTransaction:
    """
    Cria uma nova transação e faz o commit.
    """
    db_obj = await _create_transaction_no_commit(
        db=db,
        part_id=part_id,
        user_id=user_id,
        transaction_type=transaction_type,
        quantity_change=quantity_change,
        notes=notes,
        related_vehicle_id=related_vehicle_id,
        item_id=item_id
    )
    
    if related_user_id:
        db_obj.related_user_id = related_user_id

    # CORREÇÃO AQUI:
    # 1. Fazemos flush para garantir que o ID seja gerado pelo banco
    await db.flush()
    
    # 2. Capturamos o ID em uma variável local ANTES do commit
    transaction_id = db_obj.id

    # 3. Fazemos o commit (que expira o objeto db_obj)
    await db.commit()
    
    # 4. Usamos a variável transaction_id na query, em vez de db_obj.id
    stmt = (
        select(InventoryTransaction)
        .where(InventoryTransaction.id == transaction_id)
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


# --- FUNÇÕES DE LEITURA (Mantidas iguais) ---

async def get_transactions_by_part_id(
    db: AsyncSession, *, part_id: int, skip: int = 0, limit: int = 100
) -> List[InventoryTransaction]:
    stmt = (
        select(InventoryTransaction)
        .where(InventoryTransaction.part_id == part_id)
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