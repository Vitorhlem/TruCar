export interface DriverPerformance {
  user_id: number;
  full_name: string;
  avatar_url: string | null; // <-- Adicionado
  performance_score: number;
  avg_km_per_liter: number;
  total_km_driven: number;
  maintenance_requests_count: number;
}