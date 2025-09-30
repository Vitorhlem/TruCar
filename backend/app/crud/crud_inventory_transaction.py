import datetime
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
    Se a transação for uma SAIDA_USO para um veículo, também cria o registro do componente.
    """
    part = await db.get(Part, part_id)
    if not part:
        raise ValueError("Peça não encontrada.")

    # Validação de estoque para saídas
    if quantity_change < 0 and part.stock < abs(quantity_change):
        raise ValueError(f"Estoque insuficiente para a peça '{part.name}'. Apenas {part.stock} disponíveis.")

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
    
    # --- LÓGICA DE INTEGRAÇÃO ADICIONADA ---
    # Força o commit para que db_transaction receba um ID
    await db.flush() 

    if transaction_type == TransactionType.SAIDA_USO and related_vehicle_id:
        for _ in range(abs(quantity_change)):
            vehicle_component = VehicleComponent(...)
            db.add(vehicle_component)
        
        # --- LÓGICA PARA CRIAR CUSTO AUTOMÁTICO ---
        if part.value and part.value > 0:
            cost_in = VehicleCostCreate(
                description=f"Instalação do item: {part.name}",
                amount=part.value,
                date=datetime.utcnow().date(),
                cost_type=CostType.MANUTENCAO # Ou outra lógica para definir o tipo
            )
            cost_db_obj = VehicleCost(
                **cost_in.model_dump(),
                vehicle_id=related_vehicle_id,
                organization_id=part.organization_id
            )
            db.add(cost_db_obj)
    # --- FIM DA LÓGICA ---

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