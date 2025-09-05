from fastapi import APIRouter

# Importamos todos os endpoints de uma só vez para melhor organização
from app.api.v1.endpoints import (
    admin,
    clients,
    dashboard,
    freight_orders,
    fuel_logs,
    gps,
    implements,
    journeys,
    leaderboard,
    login,
    maintenance,
    notifications,
    performance,
    report_generator,
    reports,
    telemetry,
    users,
    vehicles,
    documents,
    vehicle_costs # <-- 1. NOVA IMPORTAÇÃO ADICIONADA
)

api_router = APIRouter()

# Registamos cada router com o seu prefixo e tag
api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Panel"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
# --- 2. NOVA ROTA ADICIONADA ---
# Colocamos a rota de custos logo abaixo da de veículos para manter a organização
api_router.include_router(vehicle_costs.router, prefix="/vehicles/{vehicle_id}/costs", tags=["Vehicle Costs"])
# --- FIM DA ADIÇÃO ---
api_router.include_router(journeys.router, prefix="/journeys", tags=["Journeys"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(gps.router, prefix="/gps", tags=["GPS"])
api_router.include_router(fuel_logs.router, prefix="/fuel-logs", tags=["Fuel Logs"])
api_router.include_router(performance.router, prefix="/performance", tags=["Performance"])
api_router.include_router(report_generator.router, prefix="/report-generator", tags=["Report Generator"])
api_router.include_router(implements.router, prefix="/implements", tags=["Implements"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(freight_orders.router, prefix="/freight-orders", tags=["Freight Orders"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["Telemetry"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])


