
// O tipo 'UserRole' é importado implicitamente através do tipo 'User'
type UserRole = User['role'];

// Usado ao criar um novo utilizador
export interface UserCreate {
  full_name: string;
  email: string;
  role: UserRole;
  password?: string;
  is_active?: boolean;
  employee_id?: string;
  avatar_url?: string; // <-- ADICIONADO
}

// Usado ao atualizar um utilizador existente. Todos os campos são opcionais.
export interface UserUpdate {
  full_name?: string;
  email?: string;
  role?: UserRole;
  password?: string;
  is_active?: boolean;
  employee_id?: string;
  avatar_url?: string; // <-- ADICIONADO
}

// --- NOVA INTERFACE ADICIONADA ---
// Define a "forma" dos dados para atualizar as preferências de notificação
export interface UserNotificationPrefsUpdate {
  notify_in_app: boolean;
  notify_by_email: boolean;
}
// --- FIM DA ADIÇÃO ---

// Renomeado para ser genérico: pode conter KM ou Horas
export interface PerformanceByVehicle {
  vehicle_info: string;
  value: number; // Campo genérico para o valor
}

// Interface de estatísticas atualizada para corresponder ao backend
export interface UserStats {
  total_journeys: number;
  maintenance_requests_count: number;
  
  primary_metric_label: string;
  primary_metric_value: number;
  primary_metric_unit: string;

  performance_by_vehicle: PerformanceByVehicle[];

  avg_km_per_liter?: number;
  avg_cost_per_km?: number;
  fleet_avg_km_per_liter?: number;
}

export interface LeaderboardUser {
  id: number;
  full_name: string;
  avatar_url: string | null;
  primary_metric_value: number;
  total_journeys: number;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: 'cliente_ativo' | 'cliente_demo' | 'driver';
  is_active: boolean;
  avatar_url?: string | null;
  organization_id: number;
  employee_id: string;
}