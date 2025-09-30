import type { Part } from './part-models';
import type { InventoryTransaction } from './inventory-transaction-models';

export interface VehicleComponent {
  id: number;
  installation_date: string; // ISO Date String
  uninstallation_date: string | null;
  is_active: boolean;
  part: Part;
  inventory_transaction?: InventoryTransaction; // Propriedade adicionada
}

export interface VehicleComponentCreate {
  part_id: number;
  quantity: number;
}
