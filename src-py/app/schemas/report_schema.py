from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date, datetime

from .vehicle_cost_schema import VehicleCostPublic
from .fuel_log_schema import FuelLogPublic
from .maintenance_schema import MaintenanceRequestPublic
from .fine_schema import FinePublic
from .journey_schema import JourneyPublic
from .document_schema import DocumentPublic
from .tire_schema import VehicleTirePublic as TirePublic

class DashboardSummary(BaseModel):
    total_vehicles: int
    active_journeys: int
    total_costs_last_30_days: float
    maintenance_open_requests: int


class VehicleReportSections(BaseModel):
    """Define quais seções devem ser incluídas no relatório."""
    performance_summary: bool = True
    financial_summary: bool = True
    costs_detailed: bool = True
    fuel_logs_detailed: bool = True
    maintenance_detailed: bool = False
    fines_detailed: bool = False
    journeys_detailed: bool = False
    documents_detailed: bool = False
    tires_detailed: bool = False

class VehicleReportRequest(BaseModel):
    """Schema para o corpo (body) do pedido do relatório consolidado."""
    vehicle_id: int
    start_date: date
    end_date: date
    sections: VehicleReportSections


class VehicleReportPerformanceSummary(BaseModel):
    """Resumo de performance para o relatório."""
    vehicle_total_activity: float = 0.0   # <-- CAMPO ADICIONADO
    
    period_total_activity: float = 0.0  # Renomeado de total_activity_value
    activity_unit: str = "km"           # Renomeado de total_activity_unit
    period_total_fuel: float = 0.0      # Renomeado de total_fuel_liters
    average_consumption: float = 0.0

class VehicleReportFinancialSummary(BaseModel):
    """Resumo financeiro para o relatório."""
    total_costs: float = 0.0
    cost_per_metric: float = 0.0       # Renomeado de cost_per_km
    cost_per_metric_unit: str = "km"   # Novo campo
    costs_by_category: Dict[str, float] = {}

class VehicleConsolidatedReport(BaseModel):
    """Schema principal para o Relatório Consolidado de Veículo."""
    vehicle_id: int
    vehicle_identifier: str 
    vehicle_model: str
    report_period_start: date
    report_period_end: date
    generated_at: datetime

    performance_summary: Optional[VehicleReportPerformanceSummary] = None
    financial_summary: Optional[VehicleReportFinancialSummary] = None
    
    costs_detailed: Optional[List[VehicleCostPublic]] = None
    fuel_logs_detailed: Optional[List[FuelLogPublic]] = None
    maintenance_detailed: Optional[List[MaintenanceRequestPublic]] = None
    fines_detailed: Optional[List[FinePublic]] = None
    journeys_detailed: Optional[List[JourneyPublic]] = None
    documents_detailed: Optional[List[DocumentPublic]] = None
    tires_detailed: Optional[List[TirePublic]] = None
    
    class Config:
        from_attributes = True


class DriverPerformanceEntry(BaseModel):
    """Representa a linha de dados para um único motorista no relatório."""
    driver_id: int
    driver_name: str
    total_journeys: int = 0
    total_distance_km: float = 0.0
    total_fuel_liters: float = 0.0
    average_consumption: float = 0.0
    total_fuel_cost: float = 0.0
    cost_per_km: float = 0.0
    maintenance_requests: int = 0

class DriverPerformanceReport(BaseModel):
    """Schema principal para o Relatório de Desempenho de Motoristas."""
    report_period_start: date
    report_period_end: date
    generated_at: datetime
    drivers_performance: List[DriverPerformanceEntry]

    class Config:
        from_attributes = True

class FleetReportSummary(BaseModel):
    """Resumo geral da frota no período."""
    total_cost: float = 0.0
    total_distance_km: float = 0.0
    overall_cost_per_km: float = 0.0
    
class VehicleRankingEntry(BaseModel):
    """Entrada para os rankings de veículos."""
    vehicle_id: int
    vehicle_identifier: str
    value: float
    unit: str

class FleetManagementReport(BaseModel):
    """Schema principal para o Relatório Gerencial da Frota."""
    report_period_start: date
    report_period_end: date
    generated_at: datetime
    
    summary: FleetReportSummary
    costs_by_category: Dict[str, float] = {}
    
    top_5_most_expensive_vehicles: List[VehicleRankingEntry]
    top_5_highest_cost_per_km_vehicles: List[VehicleRankingEntry]
    top_5_most_efficient_vehicles: List[VehicleRankingEntry]
    top_5_least_efficient_vehicles: List[VehicleRankingEntry]

    class Config:
        from_attributes = True