import type { Part } from './part-models';
import type { InventoryTransaction } from './inventory-transaction-models';
import type { Vehicle } from './vehicle-models';




export enum InventoryItemStatus {
  DISPONIVEL = "Disponível",
  EM_USO = "Em Uso",
  FIM_DE_VIDA = "Fim de Vida",
}


export interface InventoryItem {
  id: number;
  item_identifier: number;
  status: InventoryItemStatus;
  part_id: number;
  installed_on_vehicle_id: number | null;
  created_at: string;
  installed_at: string | null;
  part: Part | null; 
}

export interface InventoryItemDetails extends InventoryItem {
  part: Part; 
  transactions: InventoryTransaction[];
}


export interface InventoryItemRow extends InventoryItem {

  part: Part; 

  installed_on_vehicle: Vehicle | null; 
}

export interface InventoryItemPage {
  total: number;
  items: InventoryItemRow[];
}