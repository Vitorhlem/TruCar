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


export type ICostCreate = Omit<IVehicleCost, 'id'>;