// src/models/vehicle-models.ts

export enum VehicleStatus {
  AVAILABLE = 'Disponível',
  IN_USE = 'Em uso',
  MAINTENANCE = 'Em manutenção',
}

// Representa um Veículo como ele vem do banco de dados (da API)
export interface Vehicle {
  id: number;
  brand: string;
  model: string;
  year: number;
  status: VehicleStatus;
  photo_url?: string | null;
  license_plate?: string | null;
  identifier?: string | null;
  telemetry_device_id?: string | null;
  current_km?: number | null;
  current_engine_hours?: number | null;
  last_latitude?: number | null;
  last_longitude?: number | null;
  next_maintenance_date?: string | null;
  next_maintenance_km?: number | null;
  maintenance_notes?: string | null;
}
// Representa os dados para a CRIAÇÃO de um veículo
// CORREÇÃO DEFINITIVA: Alinhamos os tipos opcionais para aceitar 'null'
export interface VehicleCreate {
  brand: string;
  model: string;
  year: number;
  license_plate?: string | null;
  identifier?: string | null;
  telemetry_device_id?: string | null;
  photo_url?: string | null;
  current_km?: number | null;
  current_engine_hours?: number | null;
  next_maintenance_date?: string | null;
  next_maintenance_km?: number | null;
  maintenance_notes?: string | null;
}

// Representa os dados para a ATUALIZAÇÃO de um veículo
export type VehicleUpdate = Partial<Vehicle>;
