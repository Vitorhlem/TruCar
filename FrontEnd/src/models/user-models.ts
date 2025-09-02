
import type { User } from './auth-models';

// O tipo 'UserRole' é importado implicitamente através do tipo 'User'
type UserRole = User['role'];

// Usado ao criar um novo utilizador
export interface UserCreate {
  full_name: string;
  email: string;
  password?: string;
  role: UserRole;
  avatar_url?: string | null; // Adicionado para consistência
}

// Usado ao atualizar um utilizador existente. Todos os campos são opcionais.
export interface UserUpdate {
  full_name?: string;
  email?: string;
  password?: string;
  role?: UserRole;
  is_active?: boolean;
  // --- CORRIGIDO ---
  // Agora o avatar_url pode ser string ou null, como no objeto User principal.
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