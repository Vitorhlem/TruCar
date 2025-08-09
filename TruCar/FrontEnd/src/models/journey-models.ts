import type { User } from './auth-models';
import type { Vehicle } from './vehicle-models';

export interface Journey {
  id: number;
  is_active: boolean;
  start_time: string; // O backend envia como string ISO
  end_time: string | null;
  start_mileage: number;
  end_mileage: number | null;
  trip_type: 'specific_destination' | 'free_roam';
  destination_address: string | null;
  trip_description: string | null;
  driver: User;
  vehicle: Vehicle;
}

// ... (interface Journey já existe) ...
export interface JourneyCreate {
  vehicle_id: number;
  start_mileage: number;
  trip_type: 'specific_destination' | 'free_roam';
  destination_address?: string | null;
  trip_description?: string | null;
}

export interface JourneyUpdate {
  end_mileage: number;
}