export enum VehicleStatus {
  AVAILABLE = 'available',
  IN_USE = 'in_use',
  MAINTENANCE = 'maintenance',
}

export interface Vehicle {
  id: number;
  brand: string;
  model: string;
  license_plate: string;
  year: number;
  status: VehicleStatus;
  photo_url: string | null;
}

export interface VehicleCreate {
  brand: string;
  model: string;
  license_plate: string;
  year: number;
  photo_url?: string | null;
}

export interface VehicleUpdate {
  brand?: string;
  model?: string;
  year?: number;
  photo_url?: string | null;
  status?: VehicleStatus;
}