from datetime import datetime, timezone # --- ADICIONADO timezone ---
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

# --- IMPORTS ADICIONADOS ---
from app.models.vehicle_component_model import VehicleComponent
from app.models.inventory_transaction_model import InventoryTransaction, TransactionType
from app.models.part_model import Part
from app.models.vehicle_cost_model import VehicleCost, CostType
from app.schemas.vehicle_cost_schema import VehicleCostCreate
from app.schemas.inventory_transaction_schema import TransactionCreate



async def create_transaction(
    db: AsyncSession,
    *,
    part_id: int,
    user_id: int,
    transaction_in: TransactionCreate
) -> InventoryTransaction:
    """
    Cria uma nova transação de inventário, atualiza o estoque da peça e
    cria registros relacionados (componente, custo) se aplicável.
    """
    part = await db.get(Part, part_id)
    if not part:
        raise ValueError("Peça não encontrada.")

    # A quantidade para saídas deve ser negativa
    quantity_change = -transaction_in.quantity if transaction_in.transaction_type in [
        TransactionType.SAIDA_USO, TransactionType.SAIDA_FIM_DE_VIDA
    ] else transaction_in.quantity

    # Validação de estoque para saídas
    if quantity_change < 0 and part.stock < abs(quantity_change):
        raise ValueError(f"Estoque insuficiente para a peça '{part.name}'. Apenas {part.stock} disponíveis.")

    part.stock += quantity_change
    
    db_transaction = InventoryTransaction(
        part_id=part_id,
        user_id=user_id,
        transaction_type=transaction_in.transaction_type,
        quantity_change=quantity_change,
        stock_after_transaction=part.stock,
        notes=transaction_in.notes,
        related_vehicle_id=transaction_in.related_vehicle_id,
        related_user_id=transaction_in.related_user_id
    )
    
    db.add(part)
    db.add(db_transaction)
    
    await db.flush() 

    if transaction_in.transaction_type == TransactionType.SAIDA_USO and transaction_in.related_vehicle_id:
        for _ in range(transaction_in.quantity):
            vehicle_component = VehicleComponent(
                vehicle_id=transaction_in.related_vehicle_id,
                part_id=part_id,
                inventory_transaction_id=db_transaction.id,
                is_active=True
            )
            db.add(vehicle_component)
        
        if part.value and part.value > 0:
            total_cost = part.value * transaction_in.quantity
            cost_in = VehicleCostCreate(
                description=f"Instalação do item: {part.name}",
                amount=total_cost,
                # --- CORREÇÃO APLICADA AQUI ---
                date=datetime.now(timezone.utc).date(),
                cost_type=CostType.MANUTENCAO
            )
            cost_db_obj = VehicleCost(
                **cost_in.model_dump(),
                vehicle_id=transaction_in.related_vehicle_id,
                organization_id=part.organization_id
            )
            db.add(cost_db_obj)

    await db.commit()
    await db.refresh(db_transaction, ["user", "related_vehicle", "related_user", "part"])
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

# --- NOVA FUNÇÃO ADICIONADA E CORRIGIDA ---
async def get_transactions_by_vehicle_id(
    db: AsyncSession, *, vehicle_id: int, skip: int = 0, limit: int = 100
) -> List[InventoryTransaction]:
    """Retorna o histórico de transações de inventário para um veículo específico."""
    stmt = (
        select(InventoryTransaction)
        .where(InventoryTransaction.related_vehicle_id == vehicle_id)
        .order_by(InventoryTransaction.timestamp.desc())
        .options(
            # CORREÇÃO: Adicionados todos os relacionamentos necessários
            selectinload(InventoryTransaction.user),
            selectinload(InventoryTransaction.part),
            selectinload(InventoryTransaction.related_vehicle),
            selectinload(InventoryTransaction.related_user)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()