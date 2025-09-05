// --- Interfaces Legadas (Mantidas para compatibilidade e reutilização) ---
// Estas são as interfaces que você já tinha, e que ainda são úteis.
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
