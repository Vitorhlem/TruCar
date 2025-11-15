from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, cast, Integer
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.vehicle_component_model import VehicleComponent
from app.models.maintenance_model import MaintenanceRequest, MaintenanceComment
from app.models.vehicle_model import Vehicle
from app.models.inventory_transaction_model import InventoryTransaction
from app.models.user_model import User
from app.models.part_model import Part, InventoryItem # <-- 1. IMPORTAR MODELOS
from app.schemas.maintenance_schema import ( # <-- 2. IMPORTAR NOVOS SCHEMAS
    MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceCommentCreate,
    ReplaceComponentPayload, ReplaceComponentResponse
)
from app.crud import crud_part
# --- CRUD para Solicitações de Manutenção ---

async def create_request(
    db: AsyncSession, *, request_in: MaintenanceRequestCreate, reporter_id: int, organization_id: int
) -> MaintenanceRequest:
    """Cria uma nova solicitação de manutenção e retorna o objeto completo."""
    vehicle = await db.get(Vehicle, request_in.vehicle_id)
    if not vehicle or vehicle.organization_id != organization_id:
        raise ValueError("Veículo não encontrado nesta organização.")

    db_obj = MaintenanceRequest(**request_in.model_dump(), reported_by_id=reporter_id, organization_id=organization_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj, ["reporter", "vehicle", "comments", "approver"])
    return db_obj


async def replace_component_atomic(
    db: AsyncSession, 
    *, 
    request_id: int, 
    payload: ReplaceComponentPayload, 
    user: User
) -> ReplaceComponentResponse:
    """
    Executa a substituição de um componente de forma atômica (sem commit).
    1. Remove o item antigo (muda status).
    2. Instala o item novo (muda status e associa ao veículo).
    3. Adiciona um comentário de log no chamado.
    """
    
    # 1. Validar o chamado e obter o veículo
    request = await get_request(db, request_id=request_id, organization_id=user.organization_id)
    if not request:
        raise ValueError("Chamado de manutenção não encontrado.")
    if not request.vehicle:
        raise ValueError("Chamado não está associado a um veículo.")
        
    vehicle_id = request.vehicle.id
    organization_id = user.organization_id

    # 2. Obter o item antigo (que está saindo)
    old_item = await crud_part.get_item_by_id(db, item_id=payload.old_item_id, organization_id=organization_id)
    if not old_item:
        raise ValueError(f"Item antigo (ID: {payload.old_item_id}) não encontrado.")

    # 3. Obter o item novo (que está entrando)
    new_item = await crud_part.get_item_by_id(db, item_id=payload.new_item_id, organization_id=organization_id)
    if not new_item or new_item.status != "Disponível":
        raise ValueError(f"Item novo (ID: {payload.new_item_id}) não encontrado ou não está 'Disponível'.")
        
    # 4. Obter nomes das peças (para o log)
    old_part_name = old_item.part.name
    old_item_identifier = old_item.item_identifier
    new_part_name = new_item.part.name
    new_item_identifier = new_item.item_identifier

    # 5. Mudar status do ITEM ANTIGO (Remoção)
    # Usamos a função `change_item_status` que já corrigimos (ela não commita, só usa flush)
    await crud_part.change_item_status(
        db=db,
        item=old_item,
        new_status=payload.old_item_status,
        user_id=user.id,
        vehicle_id=vehicle_id, # Passa o ID do veículo para o log de remoção
        notes=f"Removido via Chamado #{request_id}. {payload.notes or ''}".strip()
    )

    # 6. Mudar status do ITEM NOVO (Instalação)
    await crud_part.change_item_status(
        db=db,
        item=new_item,
        new_status="Em Uso",
        user_id=user.id,
        vehicle_id=vehicle_id, # Associa ao veículo
        notes=f"Instalado via Chamado #{request_id}. {payload.notes or ''}".strip()
    )
    
    # 7. Criar o comentário de log
    comment_text = (
        f"Substituição de componente realizada por {user.full_name}:\n"
        f"- [SAIU] {old_part_name} (Cód. {old_item_identifier}) | Status: {payload.old_item_status.value}\n"
        f"- [ENTROU] {new_part_name} (Cód. {new_item_identifier}) | Status: Em Uso"
    )
    
    comment_schema = MaintenanceCommentCreate(comment_text=comment_text)
    
    new_comment = await create_comment(
        db=db,
        comment_in=comment_schema,
        request_id=request_id,
        user_id=user.id,
        organization_id=organization_id
    )

    return ReplaceComponentResponse(
        message="Substituição realizada com sucesso.",
        new_comment=new_comment
    )


async def get_request(
    db: AsyncSession, *, request_id: int, organization_id: int
) -> MaintenanceRequest | None:
    """Busca uma solicitação de manutenção específica, carregando todas as relações."""
    stmt = select(MaintenanceRequest).where(
        MaintenanceRequest.id == request_id, MaintenanceRequest.organization_id == organization_id
    ).options(
        # Carrega os usuários e seus relacionamentos
        selectinload(MaintenanceRequest.reporter).options(
            selectinload(User.organization)
        ),
        selectinload(MaintenanceRequest.approver).options(
            selectinload(User.organization)
        ),
        
        # Carrega o veículo
        selectinload(MaintenanceRequest.vehicle),
        
        # Carrega os comentários E o usuário de cada comentário E 
        # a organização de cada usuário.
        selectinload(MaintenanceRequest.comments).options(
            selectinload(MaintenanceComment.user).options(
                selectinload(User.organization)
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_maintenance_request_for_api(
    db: AsyncSession, *, request_id: int
) -> Optional[MaintenanceRequest]:
    """
    Recarrega uma solicitação de manutenção com todas as
    relações necessárias para o schema 'MaintenanceRequestPublic'.
    """
    stmt = (
        select(MaintenanceRequest)
        .where(MaintenanceRequest.id == request_id)
        .options(
            # Carrega o veículo
            selectinload(MaintenanceRequest.vehicle),
            
            # Carrega o usuário que criou a solicitação
            selectinload(MaintenanceRequest.user).options(
                selectinload(User.organization) # <-- Carrega a organização do usuário
            ),
            
            # Carrega a peça (template) relacionada
            selectinload(MaintenanceRequest.part),
            
            # Carrega o componente que será substituído (e seus detalhes)
            selectinload(MaintenanceRequest.component_to_replace).options(
                selectinload(VehicleComponent.part),
                selectinload(VehicleComponent.inventory_transaction).options(
                    selectinload(InventoryTransaction.item)
                )
            ),
            
            # --- AQUI ESTÁ A CORREÇÃO PRINCIPAL ---
            # Carrega os comentários E o usuário de cada comentário E 
            # a organização de cada usuário de cada comentário.
            selectinload(MaintenanceRequest.comments).options(
                selectinload(MaintenanceComment.user).options(
                    selectinload(User.organization)
                )
            )
            # --- FIM DA CORREÇÃO ---
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_all_requests(
    db: AsyncSession, *, organization_id: int, search: str | None = None, skip: int = 0, limit: int = 100
) -> List[MaintenanceRequest]:
    """Busca todas as solicitações, carregando TODAS as relações necessárias."""
    stmt = select(MaintenanceRequest).where(MaintenanceRequest.organization_id == organization_id)
    
    if search:
        search_term_text = f"%{search}%"
        
        # --- LÓGICA DE BUSCA ATUALIZADA ---
        search_filters = [
            MaintenanceRequest.problem_description.ilike(search_term_text),
            Vehicle.brand.ilike(search_term_text),
            Vehicle.model.ilike(search_term_text)
        ]
        
        try:
            # Tenta converter o 'search' para um número
            search_id = int(search)
            # Se conseguir, adiciona a busca pelo ID do chamado
            search_filters.append(MaintenanceRequest.id == search_id)
        except ValueError:
            pass # Não é um número, continua a busca por texto

        stmt = stmt.join(MaintenanceRequest.vehicle).where(
            or_(*search_filters)
        )
        # --- FIM DA LÓGICA ATUALIZADA ---

    stmt = stmt.order_by(MaintenanceRequest.created_at.desc()).offset(skip).limit(limit).options(
        selectinload(MaintenanceRequest.reporter),
        selectinload(MaintenanceRequest.approver),
        selectinload(MaintenanceRequest.vehicle),
        selectinload(MaintenanceRequest.comments).selectinload(MaintenanceComment.user)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_request_status(
    db: AsyncSession, *, db_obj: MaintenanceRequest, update_data: MaintenanceRequestUpdate, manager_id: int
) -> MaintenanceRequest:
    """Atualiza o status de uma solicitação e retorna o objeto completo."""
    db_obj.status = update_data.status
    db_obj.manager_notes = update_data.manager_notes
    db_obj.approver_id = manager_id
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj, ["reporter", "vehicle", "comments", "approver"])
    return db_obj

# --- CRUD PARA COMENTÁRIOS DE MANUTENÇÃO (ADICIONADO AQUI) ---

async def create_comment(
    db: AsyncSession, *, comment_in: MaintenanceCommentCreate, request_id: int, user_id: int, organization_id: int
) -> MaintenanceComment:
    """Cria um novo comentário, garantindo que a solicitação pertence à organização."""
    # A verificação de segurança agora funciona, pois 'get_request' está no mesmo ficheiro
    request_obj = await get_request(db, request_id=request_id, organization_id=organization_id)
    if not request_obj:
        raise ValueError("Solicitação de manutenção não encontrada.")

    db_obj = MaintenanceComment(
        **comment_in.model_dump(),
        request_id=request_id,
        user_id=user_id,
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.flush()
    await db.refresh(db_obj, ["user"])
    return db_obj

async def get_comments_for_request(
    db: AsyncSession, *, request_id: int, organization_id: int
) -> List[MaintenanceComment]:
    """Busca os comentários de uma solicitação, garantindo que a solicitação pertence à organização."""
    request_obj = await get_request(db, request_id=request_id, organization_id=organization_id)
    if not request_obj:
        return []
    
    stmt = select(MaintenanceComment).where(MaintenanceComment.request_id == request_id).order_by(MaintenanceComment.created_at.asc()).options(selectinload(MaintenanceComment.user))
    result = await db.execute(stmt)
    return result.scalars().all()