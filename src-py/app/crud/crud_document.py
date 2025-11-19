from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, timedelta

from app.models.document_model import Document
from app.models.vehicle_model import Vehicle
from app.models.user_model import User
from app.schemas.document_schema import DocumentCreate, DocumentUpdate, DocumentPublic


async def create_with_file_url(db: AsyncSession, *, obj_in: DocumentCreate, organization_id: int, file_url: str) -> Document:
    """
    Cria um novo documento no banco de dados.
    """
    db_obj = Document(
        **obj_in.model_dump(),
        organization_id=organization_id,
        file_url=file_url
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get(db: AsyncSession, *, id: int, organization_id: int) -> Optional[Document]:
    """
    Busca um único documento pelo seu ID, validando a organização.
    """
    stmt = select(Document).where(Document.id == id, Document.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_multi_by_org(
    db: AsyncSession,
    *,
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    expiring_in_days: Optional[int] = None,
    driver_id: Optional[int] = None # <--- NOVO PARÂMETRO DE FILTRO
) -> List[DocumentPublic]:
    """
    Busca uma lista de documentos para uma organização, com paginação e filtros.
    Se 'expiring_in_days' for fornecido, filtra por documentos que vencem nesse período.
    Se 'driver_id' for fornecido, retorna apenas documentos desse motorista.
    """
    stmt = (
        select(Document)
        .where(Document.organization_id == organization_id)
        .options(selectinload(Document.vehicle), selectinload(Document.driver))
        .order_by(Document.expiry_date.asc())
    )

    if expiring_in_days is not None:
        today = date.today()
        future_date = today + timedelta(days=expiring_in_days)
        stmt = stmt.where(Document.expiry_date.between(today, future_date))

    # --- FILTRO DE MOTORISTA ---
    if driver_id is not None:
        stmt = stmt.where(Document.driver_id == driver_id)
    # ---------------------------

    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    documents = result.scalars().all()

    # Monta a lista de resposta no formato DocumentPublic, populando o owner_info
    response_documents = []
    for doc in documents:
        doc_public = DocumentPublic.from_orm(doc)
        if doc.vehicle:
            doc_public.owner_info = f"Veículo: {doc.vehicle.license_plate or doc.vehicle.identifier}"
        elif doc.driver:
            doc_public.owner_info = f"Motorista: {doc.driver.full_name}"
        response_documents.append(doc_public)
        
    return response_documents


async def update(db: AsyncSession, *, db_obj: Document, obj_in: DocumentUpdate) -> Document:
    """
    Atualiza um documento.
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def remove(db: AsyncSession, *, id: int, organization_id: int) -> Optional[Document]:
    """
    Remove um documento do banco de dados.
    """
    db_obj = await get(db, id=id, organization_id=organization_id)
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    return db_obj