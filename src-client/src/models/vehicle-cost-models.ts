// Define os tipos de custo que o frontend conhece. Deve ser igual ao Enum do backend.
export type CostType = 'Manutenção' | 'Combustível' | 'Pedágio' | 'Seguro' | 'Pneu' | 'Outros';

// A "forma" de um registo de custo que vem da API
export interface VehicleCost {
  id: number;
  vehicle_id: number;
  description: string;
  amount: number;
  date: string; // Vem como string ISO da API
  cost_type: CostType;
}

// A "forma" dos dados que o formulário envia para criar um novo custo
export interface VehicleCostCreate {
  description: string;
  amount: number;
  date: string;
  cost_type: CostType;
}