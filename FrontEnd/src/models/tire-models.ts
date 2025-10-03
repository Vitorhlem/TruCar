import type { Part } from './part-models';

// Representa um pneu instalado em uma posição
export interface VehicleTire {
  id: number;
  part_id: number;
  vehicle_id: number;
  position_code: string;
  installation_date: string; // ISO string
  install_km: number;
  is_active: boolean;
  install_engine_hours?: number | null; // --- ADICIONADO ---
  part: Part; // Detalhes da peça (pneu)
}

// Representa a resposta da API com a configuração do veículo
export interface TireLayout {
  vehicle_id: number;
  axle_configuration: string | null;
  tires: VehicleTire[];
}

// Payload para instalar um pneu
export interface TireInstallPayload {
  part_id: number;
  position_code: string;
  install_km: number;
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
    position_code: string; // <-- ADICIONE ESTA LINHA

  install_date: string; // as datas vêm como string do JSON
  removal_date: string | null;
  km_run: number;
}