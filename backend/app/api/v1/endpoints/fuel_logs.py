from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import random
from datetime import datetime, timedelta

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.schemas.fuel_log_schema import FuelLogPublic, FuelLogCreate, FuelLogUpdate, FuelProviderTransaction

router = APIRouter()

# --- ROTAS PARA GERENCIAMENTO MANUAL DE ABASTECIMENTOS (Seu código original) ---

@router.post("/", response_model=FuelLogPublic, status_code=status.HTTP_201_CREATED)
async def create_fuel_log(
    *,
    db: AsyncSession = Depends(deps.get_db),
    log_in: FuelLogCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Registra um novo abastecimento para o utilizador logado."""
    return await crud.fuel_log.create_fuel_log(
        db=db, log_in=log_in, user_id=current_user.id, organization_id=current_user.organization_id
    )

@router.get("/", response_model=List[FuelLogPublic])
async def read_fuel_logs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retorna o histórico de abastecimentos com paginação.
    - Gestores veem todos os registos da organização.
    - Motoristas veem apenas os seus próprios registos.
    """
    # NOTA: O seu código original tinha UserRole.MANAGER, mas nos outros arquivos você usa
    # CLIENTE_ATIVO e CLIENTE_DEMO. Estou a assumir que estes são os papéis de gestor.
    if current_user.role in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
        return await crud.fuel_log.get_multi_by_org(
            db=db, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
    else: # DRIVER
        return await crud.fuel_log.get_multi_by_user(
            db=db, user_id=current_user.id, organization_id=current_user.organization_id, skip=skip, limit=limit
        )

@router.get("/{log_id}", response_model=FuelLogPublic)
async def read_fuel_log_by_id(
    log_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Busca um registo de abastecimento específico pelo ID (apenas gestores)."""
    log = await crud.fuel_log.get_fuel_log(db, log_id=log_id, organization_id=current_user.organization_id)
    if not log:
        raise HTTPException(status_code=404, detail="Registo de abastecimento não encontrado.")
    return log

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fuel_log(
    log_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Exclui um registo de abastecimento (apenas gestores)."""
    log_to_delete = await crud.fuel_log.get_fuel_log(db, log_id=log_id, organization_id=current_user.organization_id)
    if not log_to_delete:
        raise HTTPException(status_code=404, detail="Registo de abastecimento não encontrado.")
    
    await crud.fuel_log.remove_fuel_log(db, db_obj=log_to_delete)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- NOVAS ROTAS PARA INTEGRAÇÃO COM CARTÃO DE COMBUSTÍVEL ---

async def _simulate_fuel_provider_transactions(
    db: AsyncSession, current_user: User
) -> List[FuelProviderTransaction]:
    """
    [SIMULADOR INTERNO] Gera uma lista de transações de abastecimento falsas.
    Não é exposto como um endpoint, apenas usado internamente pela rota de sync.
    """
    vehicles = await crud.vehicle.get_multi_by_org(db, organization_id=current_user.organization_id, limit=10)
    drivers = await crud.user.get_multi_by_org(db, organization_id=current_user.organization_id, limit=10)

    if not vehicles or not drivers:
        return []

    transactions = []
    for _ in range(random.randint(2, 5)):
        vehicle = random.choice(vehicles)
        driver = random.choice(drivers)
        timestamp = datetime.utcnow() - timedelta(days=random.uniform(0, 2))
        liters = round(random.uniform(20.0, 80.0), 2)
        price_per_liter = 5.50
        station_lat = (vehicle.last_latitude or -21.1) + random.uniform(-0.005, 0.005)
        station_lon = (vehicle.last_longitude or -48.2) + random.uniform(-0.005, 0.005)

        tx = FuelProviderTransaction(
            transaction_id=f"TX-{random.randint(100000, 999999)}",
            vehicle_license_plate=vehicle.license_plate,
            driver_cpf=getattr(driver, 'cpf', f"000000000{driver.id:02d}"),
            timestamp=timestamp,
            liters=liters,
            total_cost=round(liters * price_per_liter, 2),
            gas_station_name=f"Posto Simulado {random.choice(['A', 'B', 'C'])}",
            gas_station_latitude=station_lat,
            gas_station_longitude=station_lon,
        )
        transactions.append(tx)
        
    return transactions


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_fuel_transactions(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager), # Apenas gestores podem sincronizar
):
    """
    Inicia a sincronização de transações de combustível a partir do provedor.
    """
    # 1. Busca as transações (do nosso simulador)
    transactions = await _simulate_fuel_provider_transactions(db=db, current_user=current_user)

    if not transactions:
        return {"message": "Nenhuma nova transação encontrada."}

    # 2. Processa as transações usando a função do nosso CRUD
    result = await crud.fuel_log.process_provider_transactions(
        db=db,
        transactions=transactions,
        organization_id=current_user.organization_id
    )
    
    return {"message": f"Sincronização concluída. {result.get('new_logs_processed', 0)} novos registos processados."}
