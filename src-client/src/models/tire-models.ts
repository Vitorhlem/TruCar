

import type { Part } from './part-models';


export interface VehicleTire {
  id: number;
  part_id: number;
  vehicle_id: number;
  position_code: string;
  installation_date: string;
  install_km: number;
  is_active: boolean;
  install_engine_hours?: number | null;
  part: Part;
}


export interface TireLayout {
  vehicle_id: number;
  axle_configuration: string | null;
  tires: VehicleTire[];
}



export interface TireInstallPayload {
  part_id: number;
  position_code: string;
  install_km: number;
  install_engine_hours?: number;
}

export type TireWithStatus = VehicleTire & {
  status: 'ok' | 'warning' | 'critical';
  wearPercentage: number;
  km_rodados: number;
  horas_de_uso?: number; 
  lifespan_km: number;
}


export interface VehicleTireHistory {
  id: number;
  part: Part;
  install_km: number;
  removal_km: number | null;
  position_code: string;
  installation_date: string;
  removal_date: string | null;
  km_run: number;
}