from fastapi import APIRouter
from app.api.v1.endpoints import login, users, vehicles, leaderboard # Adicione 'leaderboard'


# 1. Adicionamos 'performance' à lista de imports
from app.api.v1.endpoints import (
    users,
    vehicles,
    journeys,
    login,
    reports,
    notifications,
    maintenance,
    gps,
    fuel_logs,
    performance,
    implements,
    report_generator,
    telemetry,
    clients,
    freight_orders
)

api_router = APIRouter()

# Registra todos os roteadores
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])

api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(journeys.router, prefix="/journeys", tags=["Journeys"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(gps.router, prefix="/gps", tags=["GPS"])
api_router.include_router(fuel_logs.router, prefix="/fuel-logs", tags=["Fuel Logs"])

# 2. Adicionamos a nova linha para o roteador de performance
api_router.include_router(performance.router, prefix="/performance", tags=["Performance"])
api_router.include_router(report_generator.router, prefix="/report-generator", tags=["Report Generator"])
api_router.include_router(implements.router, prefix="/implements", tags=["Implements"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(freight_orders.router, prefix="/freight-orders", tags=["Freight Orders"])
