from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional

from app.models.part_model import Part
from . import crud_inventory_transaction as crud_transaction
from app.schemas.part_schema import PartCreate, PartUpdate
from app.models.inventory_transaction_model import TransactionType

async def get(db: AsyncSession, *, id: int, organization_id: int) -> Optional[Part]:
    """Busca uma peça pelo ID, garantindo que pertence à organização."""
    stmt = select(Part).where(Part.id == id, Part.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_multi_by_org(
    db: AsyncSession,
    *,
    organization_id: int,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Part]:
    """Retorna uma lista de peças para uma organização, com busca e paginação."""
    stmt = select(Part).where(Part.organization_id == organization_id)
    if search:
        search_term = f"%{search.lower()}%"
        stmt = stmt.where(
            or_(
                Part.name.ilike(search_term),
                Part.brand.ilike(search_term),
                Part.part_number.ilike(search_term)
            )
        )
    stmt = stmt.order_by(Part.name).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create(db: AsyncSession, *, part_in: PartCreate, organization_id: int, user_id: int, photo_url: Optional[str] = None) -> Part:
    """Cria uma nova peça e registra a transação de estoque inicial."""
    db_obj = Part(
        **part_in.model_dump(exclude={"stock"}), # Exclui o estoque para definir manualmente
        stock=0, # Começa com 0 para a transação ajustar
        photo_url=photo_url,
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.flush() # Atribui um ID ao db_obj antes de usá-lo na transação

    # Se houver estoque inicial, cria uma transação
    if part_in.stock > 0:
        # A chamada aqui já estava correta pois importamos diretamente
        await crud_transaction.create_transaction(
            db=db,
            part_id=db_obj.id,
            user_id=user_id,
            transaction_type=TransactionType.AJUSTE_INICIAL,
            quantity_change=part_in.stock,
            notes=f"Carga inicial do item no sistema."
        )
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update(db: AsyncSession, *, db_obj: Part, obj_in: PartUpdate, photo_url: Optional[str]) -> Part:
    """Atualiza uma peça. O estoque é atualizado via transações, não aqui."""
    update_data = obj_in.model_dump(exclude_unset=True, exclude={'stock'})
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db_obj.photo_url = photo_url
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove(db: AsyncSession, *, id: int, organization_id: int) -> Optional[Part]:
    """Remove uma peça do inventário."""
    # Adicionamos organization_id para segurança
    db_obj = await get(db, id=id, organization_id=organization_id)
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    return db_obj

