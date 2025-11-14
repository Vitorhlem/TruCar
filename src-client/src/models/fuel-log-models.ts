// ARQUIVO: src/models/fuel-log-models.ts

import type { User } from './auth-models';
import type { Vehicle } from './vehicle-models';

export interface FuelLog {
  id: number;
  odometer: number;
  liters: number;
  total_cost: number;
  vehicle_id: number;
  user_id: number;
  receipt_photo_url: string | null;
  timestamp: string;

  // --- Novos campos para a integração ---
  verification_status: 'PENDING' | 'VERIFIED' | 'SUSPICIOUS' | 'UNVERIFIED';
  provider_name: string | null;
  gas_station_name: string | null;
  source: 'MANUAL' | 'INTEGRATION';

  // --- Relações aninhadas ---
  user: User;
  vehicle: Vehicle;
}

export interface FuelLogCreate {
  vehicle_id: number;
  odometer: number;
  liters: number;
  total_cost: number;
  receipt_photo_url?: string | null;
}

// --- INTERFACE ADICIONADA ---
// Todos os campos são opcionais para a atualização (PUT/PATCH)
export interface FuelLogUpdate {
  vehicle_id?: number;
  odometer?: number;
  liters?: number;
  total_cost?: number;
  receipt_photo_url?: string | null;
}