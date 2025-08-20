// src/models/journey-models.ts
import type { User } from './auth-models';
import type { Vehicle } from './vehicle-models';

export enum JourneyType {
  SPECIFIC_DESTINATION = 'specific_destination',
  FREE_ROAM = 'free_roam',
}

export interface Journey {
  id: number;
  start_time: string;
  end_time: string | null;
  start_mileage: number;
  end_mileage: number | null;
  is_active: boolean;
  trip_type: JourneyType;
  destination_address?: string | null;
  trip_description?: string | null;
  vehicle: Vehicle;
  driver: User;
  organization_id: number;
}

export interface JourneyCreate {
  // CORRIGIDO: Permite null para o reset do formulário
  vehicle_id: number | null;
  start_mileage: number;
  trip_type: JourneyType;
  destination_address?: string;
  trip_description?: string;
}

export interface JourneyUpdate {
  end_mileage: number;
}