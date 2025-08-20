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