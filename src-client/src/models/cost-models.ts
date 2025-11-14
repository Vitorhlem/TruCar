export interface IVehicleCost {
  id: number;
  cost_type: string;
  amount: number;
  date: string;
  notes?: string;
  vehicle_id: number;
}

export interface VehicleCost {
  id: number;
  vehicle_id: number;
  cost_type: string;
  amount: number;
  date: string;
  notes?: string;
}

// Interface para a criação de um novo custo (sem o 'id')
export type ICostCreate = Omit<IVehicleCost, 'id'>;