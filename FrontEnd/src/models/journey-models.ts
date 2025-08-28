import type { User } from './auth-models';
import { ImplementCreate } from './implement-models';
import type { Vehicle } from './vehicle-models';

export enum JourneyType {
  SPECIFIC_DESTINATION = 'specific_destination',
  FREE_ROAM = 'free_roam',
}

// A interface principal para uma Viagem/Operação
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
  
  // OS CAMPOS QUE ESTAVAM EM FALTA:
  start_engine_hours: number | null;
  end_engine_hours: number | null;
  implement?: ImplementCreate;


  // Relações
  vehicle: Vehicle;
  driver: User;
  organization_id: number;
}

// A interface para o formulário de CRIAÇÃO
export interface JourneyCreate {
  vehicle_id: number | null;
  trip_type: JourneyType;
  destination_address?: string;
  trip_description?: string;
  implement_id?: number | null;

  
  // OS CAMPOS QUE ESTAVAM EM FALTA:
  start_mileage?: number;
  start_engine_hours?: number;
}

// A interface para o formulário de ATUALIZAÇÃO (Finalização)
export interface JourneyUpdate {
  // OS CAMPOS QUE ESTAVAM EM FALTA:
  end_mileage?: number;
  end_engine_hours?: number;
}