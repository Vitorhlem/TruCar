from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date, datetime

from .vehicle_cost_schema import VehicleCostPublic
from .fuel_log_schema import FuelLogPublic
from .maintenance_schema import MaintenanceRequestPublic

# Mantém o schema do dashboard existente
class DashboardSummary(BaseModel):
    total_vehicles: int
    active_journeys: int
    total_costs_last_30_days: float
    maintenance_open_requests: int

# --- NOVOS SCHEMAS PARA O RELATÓRIO CONSOLIDADO DE VEÍCULO ---

class VehicleReportPerformanceSummary(BaseModel):
    """Resumo de performance para o relatório."""
    total_distance_km: float = 0.0
    total_fuel_liters: float = 0.0
    average_consumption: float = 0.0 # KM/L ou L/Hora, dependendo do setor

class VehicleReportFinancialSummary(BaseModel):
    """Resumo financeiro para o relatório."""
    total_costs: float = 0.0
    cost_per_km: float = 0.0
    costs_by_category: Dict[str, float] = {}

class VehicleConsolidatedReport(BaseModel):
    """Schema principal para o Relatório Consolidado de Veículo."""
    # --- Dados de Cabeçalho ---
    vehicle_id: int
    vehicle_identifier: str # Placa ou Identificador
    vehicle_model: str
    report_period_start: date
    report_period_end: date
    generated_at: datetime

    # --- Seções de Dados ---
    performance_summary: VehicleReportPerformanceSummary
    financial_summary: VehicleReportFinancialSummary
    
    # --- Dados Detalhados ---
    costs_detailed: List[VehicleCostPublic]
    fuel_logs_detailed: List[FuelLogPublic]
    maintenance_detailed: List[MaintenanceRequestPublic]
    
    class Config:
        from_attributes = True