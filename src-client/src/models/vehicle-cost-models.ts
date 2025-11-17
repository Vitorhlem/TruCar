
export type CostType = 'Manutenção' | 'Combustível' | 'Pedágio' | 'Seguro' | 'Pneu' | 'Outros';


export interface VehicleCost {
  id: number;
  vehicle_id: number;
  description: string;
  amount: number;
  date: string;
  cost_type: CostType;
}


export interface VehicleCostCreate {
  description: string;
  amount: number;
  date: string;
  cost_type: CostType;
}