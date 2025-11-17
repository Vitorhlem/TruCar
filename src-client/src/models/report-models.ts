import type { VehicleCost } from './vehicle-cost-models';
import type { FuelLog } from './fuel-log-models';
import type { MaintenanceRequest } from './maintenance-models';
import type { Fine } from './fine-models';
import type { Journey } from './journey-models';
import type { DocumentPublic } from './document-models';
import type { VehicleTire } from './tire-models';


export interface DashboardSummary {
  total_vehicles: number;
  active_journeys: number;
  total_costs_last_30_days: number;
  maintenance_open_requests: number;
}
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

export interface FleetReportSummary {
  total_cost: number;
  total_distance_km: number;
  overall_cost_per_km: number;
}

export interface VehicleRankingEntry {
  vehicle_id: number;
  vehicle_identifier: string;
  value: number;
  unit: string;
}

export interface FleetManagementReport {
  report_period_start: string;
  report_period_end: string;
  generated_at: string;
  summary: FleetReportSummary;
  costs_by_category: Record<string, number>;
  top_5_most_expensive_vehicles: VehicleRankingEntry[];
  top_5_highest_cost_per_km_vehicles: VehicleRankingEntry[];
  top_5_most_efficient_vehicles: VehicleRankingEntry[];
  top_5_least_efficient_vehicles: VehicleRankingEntry[];
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


export interface DriverDashboardResponse {
  metrics: DriverMetrics;
  ranking_context: DriverRankEntry[];
  achievements: AchievementStatus[];
}

export interface VehicleReportPerformanceSummary {
  total_activity_value: number;
  total_activity_unit: string;
  total_fuel_liters: number;
  average_consumption: number;
}


export interface VehicleReportFinancialSummary {
  total_costs: number;
  cost_per_metric: number;
  metric_unit: string;
  costs_by_category: Record<string, number>;
}



export interface VehicleConsolidatedReport {

  vehicle_id: number;
  vehicle_identifier: string;
  vehicle_model: string;
  report_period_start: string;
  report_period_end: string;
  generated_at: string;


  performance_summary?: VehicleReportPerformanceSummary | null;
  financial_summary?: VehicleReportFinancialSummary | null;


  costs_detailed?: VehicleCost[] | null;
  fuel_logs_detailed?: FuelLog[] | null;
  maintenance_detailed?: MaintenanceRequest[] | null;
  fines_detailed?: Fine[] | null;
  journeys_detailed?: Journey[] | null;
  documents_detailed?: DocumentPublic[] | null;
  tires_detailed?: VehicleTire[] | null;
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
export interface VehicleReportPerformanceSummary {
  vehicle_total_activity: number;
  period_total_activity: number;
  activity_unit: string;
  period_total_fuel: number;
  average_consumption: number;
}

export interface DriverPerformanceReport {
  report_period_start: string;
  report_period_end: string;
  generated_at: string;
  drivers_performance: DriverPerformanceEntry[];
}

export interface FleetReportSummary {
  total_cost: number;
  total_distance_km: number;
  overall_cost_per_km: number;
}

export interface VehicleRankingEntry {
  vehicle_id: number;
  vehicle_identifier: string;
  value: number;
  unit: string;
}

export interface FleetManagementReport {
  report_period_start: string;
  report_period_end: string;
  generated_at: string;
  summary: FleetReportSummary;
  costs_by_category: Record<string, number>;
  top_5_most_expensive_vehicles: VehicleRankingEntry[];
  top_5_highest_cost_per_km_vehicles: VehicleRankingEntry[];
  top_5_most_efficient_vehicles: VehicleRankingEntry[];
  top_5_least_efficient_vehicles: VehicleRankingEntry[];
}