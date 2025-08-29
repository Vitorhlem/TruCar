// ARQUIVO: src/models/user-models.ts

export interface UserCreate {
  email: string;
  full_name: string;
  password?: string;
  role: 'manager' | 'driver';
  avatar_url?: string | null;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  password?: string;
  role?: 'manager' | 'driver';
  is_active?: boolean;
  avatar_url?: string | null;
}

// --- INÍCIO DA CORREÇÃO ---

// Renomeado para ser genérico: pode conter KM ou Horas
export interface PerformanceByVehicle {
  vehicle_info: string;
  value: number; // Campo genérico para o valor
}

// Interface de estatísticas atualizada para corresponder ao backend
export interface UserStats {
  total_journeys: number;
  maintenance_requests_count: number;
  
  // Métricas principais que mudam por setor
  primary_metric_label: string;
  primary_metric_value: number;
  primary_metric_unit: string;

  // Lista de performance por veículo, agora genérica
  performance_by_vehicle: PerformanceByVehicle[];

  // KPIs de combustível são opcionais, pois só existem para o setor de serviços
  avg_km_per_liter?: number;
  avg_cost_per_km?: number;
  fleet_avg_km_per_liter?: number;
}
// --- FIM DA CORREÇÃO ---

export interface LeaderboardUser {
  id: number;
  full_name: string;
  avatar_url: string | null;
  primary_metric_value: number;
  total_journeys: number;
}