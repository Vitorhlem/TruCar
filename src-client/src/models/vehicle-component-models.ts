import type { Part } from './part-models';
import type { InventoryTransaction } from './inventory-transaction-models';
// --- 1. IMPORTAR O MODELO DE ITEM ---
import type { InventoryItem } from './inventory-item-models';

export interface VehicleComponent {
  id: number;
  installation_date: string; // ISO Date String
  uninstallation_date: string | null;
  is_active: boolean;
  part: Part;
  inventory_transaction?: InventoryTransaction; // Propriedade adicionada
  // --- 2. ADICIONAR O ITEM (PARA O CÓD. ITEM) ---
  item: InventoryItem | null;
}

export interface VehicleComponentCreate {
  part_id: number;
  quantity: number;
}