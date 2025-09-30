import type { Part } from './part-models';

export interface VehicleComponent {
  id: number;
  installation_date: string; // ISO Date String
  uninstallation_date: string | null;
  is_active: boolean;
  part: Part;
}

export interface VehicleComponentCreate {
  part_id: number;
  quantity: number;
}