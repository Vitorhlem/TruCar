import type { VehicleCost } from './vehicle-cost-models';
import type { FuelLog } from './fuel-log-models';
import type { MaintenanceRequest } from './maintenance-models';

export interface KPI {
  total_vehicles: number;
  available_vehicles: number;
  in_use_vehicles: number;
  maintenance_vehicles: number;
}
export interface KmPerDay {
  date: string;
  total_km: number;
}
export interface UpcomingMaintenance {
  vehicle_info: string;
  due_date: string | null;
  due_km: number | null;
}
export interface CostByCategory {
  cost_type: string;
  total_amount: number;
}
export interface DashboardPodiumDriver {
  full_name: string;
  avatar_url: string | null;
  primary_metric_value: number;
}

export interface DriverPerformanceEntry {
  driver_id: number;
  driver_name: string;
  total_journeys: number;
  total_distance_km: number;
  total_fuel_liters: number;
  average_consumption: number;
  total_fuel_cost: number;
  cost_per_km: number;
  maintenance_requests: number;
}

export interface DriverPerformanceReport {
  report_period_start: string;
  report_period_end: string;
  generated_at: string;
  drivers_performance: DriverPerformanceEntry[];
}

// ===================================================================
// NOVAS INTERFACES PARA O DASHBOARD AVANÇADO
// (Correspondem a app/schemas/dashboard_schema.py)
// ===================================================================

// --- Interfaces para o Dashboard do Gestor ---

export interface KpiEfficiency {
  cost_per_km: number;
  utilization_rate: number;
}

export interface VehiclePosition {
  id: number;
  license_plate: string | null;
  identifier: string | null;
  latitude: number;
  longitude: number;
  status: string;
}

export interface AlertSummary {
  id: number;
  icon: string;
  color: string;
  title: string;
  subtitle: string;
  time: string;
}

export interface GoalStatus {
  title: string;
  current_value: number;
  target_value: number;
  unit: string;
}

// --- Resposta Principal para o Dashboard do Gestor ---
export interface ManagerDashboardResponse {
  kpis: KPI;
  efficiency_kpis: KpiEfficiency;
  costs_by_category: CostByCategory[] | null;
  km_per_day_last_30_days: KmPerDay[] | null;
  podium_drivers: DashboardPodiumDriver[] | null;
  recent_alerts: AlertSummary[];
  upcoming_maintenances: UpcomingMaintenance[];
  active_goal: GoalStatus | null;
}

// --- Interfaces para o Dashboard do Motorista ---

export interface DriverMetrics {
  distance: number;
  hours: number;
  fuel_efficiency: number;
  alerts: number;
}

export interface DriverRankEntry {
  rank: number;
  name: string;
  metric: number;
  is_current_user: boolean;
}

export interface AchievementStatus {
  title: string;
  icon: string;
  unlocked: boolean;
}

// --- Resposta Principal para o Dashboard do Motorista ---
export interface DriverDashboardResponse {
  metrics: DriverMetrics;
  ranking_context: DriverRankEntry[];
  achievements: AchievementStatus[];
}

export interface VehicleReportPerformanceSummary {
  total_distance_km: number;
  total_fuel_liters: number;
  average_consumption: number;
}

// Corresponde ao schema VehicleReportFinancialSummary do backend
export interface VehicleReportFinancialSummary {
  total_costs: number;
  cost_per_km: number;
  costs_by_category: Record<string, number>;
}

// Corresponde ao schema principal VehicleConsolidatedReport do backend
export interface VehicleConsolidatedReport {
  vehicle_id: number;
  vehicle_identifier: string;
  vehicle_model: string;
  report_period_start: string; // vem como string 'YYYY-MM-DD'
  report_period_end: string;
  generated_at: string; // vem como string ISO

  performance_summary: VehicleReportPerformanceSummary;
  financial_summary: VehicleReportFinancialSummary;
  
  costs_detailed: VehicleCost[];
  fuel_logs_detailed: FuelLog[];
  maintenance_detailed: MaintenanceRequest[];
}