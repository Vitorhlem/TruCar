import type { Part } from './part-models';
import type { InventoryTransaction } from './inventory-transaction-models';
import type { Vehicle } from './vehicle-models';

// --- ESTA É A CORREÇÃO ---
// Trocamos 'export type' por 'export enum' para que
// ele exista como um objeto JavaScript no runtime.
export enum InventoryItemStatus {
  DISPONIVEL = "Disponível",
  EM_USO = "Em Uso",
  FIM_DE_VIDA = "Fim de Vida",
}
// --- FIM DA CORREÇÃO ---

export interface InventoryItem {
  id: number;
  item_identifier: number;
  status: InventoryItemStatus; // Agora se refere ao enum
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

// Para a nova página (InventoryItemsPage.vue)
export interface InventoryItemRow extends InventoryItem {
  // 'part' já está no InventoryItem, mas aqui forçamos a não ser nulo
  part: Part; 
  // O backend envia um _VehicleInfo, que é um subconjunto de 'Vehicle'
  installed_on_vehicle: Vehicle | null; 
}

export interface InventoryItemPage {
  total: number;
  items: InventoryItemRow[]; // Note que aqui é InventoryItemRow
}