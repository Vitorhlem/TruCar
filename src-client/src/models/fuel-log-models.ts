

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


  verification_status: 'PENDING' | 'VERIFIED' | 'SUSPICIOUS' | 'UNVERIFIED';
  provider_name: string | null;
  gas_station_name: string | null;
  source: 'MANUAL' | 'INTEGRATION';


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



export interface FuelLogUpdate {
  vehicle_id?: number;
  odometer?: number;
  liters?: number;
  total_cost?: number;
  receipt_photo_url?: string | null;
}