import type { Part } from './part-models';

// Representa um pneu instalado em uma posição
export interface VehicleTire {
  id: number;
  position_code: string;
  install_date: string;
  install_km: number;
  part: Part; // Detalhes do pneu do inventário
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