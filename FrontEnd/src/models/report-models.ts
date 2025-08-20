import type { Journey } from './journey-models';

// RE-EXPORTAMOS O TIPO PARA QUE OUTROS ARQUIVOS POSSAM USÁ-LO
export type { Journey };

export interface KPI {
  total_vehicles: number;
  available_vehicles: number;
  in_use_vehicles: number;
  maintenance_vehicles: number;
  total_fuel_cost_current_month: number;
  open_maintenance_requests: number;
}

export interface KmPerDay {
  date: string;
  total_km: number;
}

export interface TopVehicle {
  vehicle_info: string;
  total_km: number;
}

export interface FuelCostPerMonth {
  month: string;
  total_cost: number;
}

export interface UpcomingMaintenance {
  vehicle_info: string;
  due_date: string | null;
  due_km: number | null;
}

export interface DashboardSummary {
  kpis: KPI;
  km_per_day_last_30_days: KmPerDay[];
  top_5_vehicles_by_km: TopVehicle[];
  fuel_cost_last_6_months: FuelCostPerMonth[];
  upcoming_maintenances: UpcomingMaintenance[];
  active_journeys: Journey[];
}