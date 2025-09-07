import random
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

# Para uma integração real, você usaria uma biblioteca de requisições HTTP
# import httpx

from app import crud
from app.schemas.fuel_log_schema import FuelProviderTransaction
from app.models.user_model import UserRole

async def _get_simulated_transactions(db: AsyncSession, organization_id: int) -> List[FuelProviderTransaction]:
    """
    SIMULADOR: Esta função gera dados falsos e deve ser usada apenas para
    desenvolvimento e demonstração.
    """
    vehicles = await crud.vehicle.get_multi_by_org(db, organization_id=organization_id, limit=5)
    drivers = await crud.user.get_users_by_role(db, organization_id=organization_id, role=UserRole.DRIVER, limit=5)

    if not vehicles or not drivers:
        return []

    mock_transactions = []
    for _ in range(random.randint(0, 2)): # Pode não haver novas transações
        vehicle = random.choice(vehicles)
        driver = random.choice(drivers)
        
        if not driver.employee_id:
            continue

        is_suspicious = random.choice([True, False, False])
        if is_suspicious:
            station_lat, station_lon = -23.5505, -46.6333 # São Paulo
        else:
            station_lat, station_lon = vehicle.last_latitude or -21.1767, vehicle.last_longitude or -47.8208

        mock_transactions.append(
            FuelProviderTransaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                vehicle_license_plate=vehicle.license_plate,
                driver_employee_id=driver.employee_id,
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 12)),
                liters=round(random.uniform(20.0, 50.0), 2),
                total_cost=round(random.uniform(100.0, 300.0), 2),
                gas_station_name=random.choice(["Posto Ipiranga", "Shell", "Petrobras"]),
                gas_station_latitude=station_lat + random.uniform(-0.05, 0.05),
                gas_station_longitude=station_lon + random.uniform(-0.05, 0.05),
            )
        )
    return mock_transactions


async def _fetch_transactions_from_provider(db: AsyncSession, organization_id: int) -> List[FuelProviderTransaction]:
    """
    TEMPLATE PARA INTEGRAÇÃO REAL: Esta função conecta-se à API de um provedor
    de cartão de combustível e retorna as transações.
    """
    # --- PASSO 1: Buscar as credenciais da API da organização ---
    # No mundo real, você teria um local para armazenar as API keys do cliente.
    # Ex: org_settings = await crud.organization.get_settings(db, id=organization_id)
    # api_key = org_settings.fuel_provider_api_key
    # api_secret = org_settings.fuel_provider_api_secret
    
    # Se não houver credenciais, a integração não está ativa para esta empresa.
    # if not api_key:
    #     return []

    # --- PASSO 2: Fazer a chamada à API real ---
    # O código abaixo é um exemplo de como seria. A documentação do provedor
    # (Ticket Log, Alelo, etc.) teria os detalhes exatos.
    
    # async with httpx.AsyncClient() as client:
    #     try:
    #         response = await client.get(
    #             "https://api.ticketlog.com.br/v1/transactions",
    #             headers={"Authorization": f"Bearer {api_key}"},
    #             params={"since": "2024-01-01T00:00:00Z"} # Exemplo de parâmetro
    #         )
    #         response.raise_for_status() # Lança um erro se a resposta for 4xx ou 5xx
    #         raw_transactions = response.json()
    #     except httpx.HTTPStatusError as e:
    #         print(f"Erro ao buscar transações para a organização {organization_id}: {e}")
    #         return []

    # --- PASSO 3: Converter a resposta da API para o nosso schema ---
    # Cada provedor tem um formato de resposta diferente. Aqui, você converteria
    # o `raw_transactions` para uma lista de `FuelProviderTransaction`.
    
    # processed_transactions = []
    # for tx in raw_transactions:
    #     processed_transactions.append(
    #         FuelProviderTransaction(
    #             transaction_id=tx.get("idTransacao"),
    #             vehicle_license_plate=tx.get("placa"),
    #             driver_employee_id=tx.get("codigoMotorista"),
    #             ... # e assim por diante
    #         )
    #     )
    # return processed_transactions

    # --- ATENÇÃO: Enquanto a integração real não for implementada, usamos o simulador ---
    print("AVISO: Usando o simulador de transações de combustível.")
    return await _get_simulated_transactions(db, organization_id=organization_id)


async def sync_all_organizations_fuel_logs(db: AsyncSession):
    """
    Esta é a tarefa principal a ser agendada. Ela itera sobre todas as
    organizações ativas e processa seus abastecimentos.
    """
    print("Iniciando tarefa de sincronização de abastecimentos...")
    organizations = await crud.organization.get_multi(db, status='active')
    
    total_processed = 0
    for org in organizations:
        print(f"Buscando transações para a organização: {org.name}")
        # 1. Busca as transações (do nosso template ou da API real)
        transactions = await _fetch_transactions_from_provider(db, organization_id=org.id)
        
        if not transactions:
            print(f"Nenhuma nova transação para {org.name}.")
            continue
            
        # 2. Processa as transações encontradas usando a função CRUD existente
        result = await crud.fuel_log.process_provider_transactions(
            db=db, transactions=transactions, organization_id=org.id
        )
        processed_count = result.get("new_logs_processed", 0)
        if processed_count > 0:
            print(f"{processed_count} novos abastecimentos importados para {org.name}.")
            total_processed += processed_count

    print(f"Tarefa de sincronização concluída. Total de {total_processed} novos abastecimentos importados.")

