export interface UserCreate {
  email: string;
  full_name: string;
  password?: string;
  role: 'manager' | 'driver';
  avatar_url?: string | null; // <-- Adicionado
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  password?: string;
  role?: 'manager' | 'driver';
  is_active?: boolean;
  avatar_url?: string | null; // <-- Adicionado
}

export interface JourneysByVehicle {
  vehicle_info: string;
  km_driven_in_vehicle: number;
}

// --- INTERFACE COMPLETA DE ESTATÍSTICAS ---
export interface UserStats {
  total_journeys: number;
  total_km_driven: number;
  journeys_by_vehicle: JourneysByVehicle[];
  maintenance_requests_count: number;
  avg_km_per_liter: number;
  avg_cost_per_km: number;
  fleet_avg_km_per_liter: number;
}