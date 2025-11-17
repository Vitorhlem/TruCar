import type { User } from './auth-models';
import type { Vehicle } from './vehicle-models';
import type { Part } from './part-models';

import type { InventoryItem } from './inventory-item-models';

export type TransactionType = "Entrada" | "Saída para Uso" | "Fim de Vida" | "Retorno" | "Ajuste Inicial" | "Ajuste Manual";


export interface TransactionCreate {
  transaction_type: TransactionType;
  quantity: number;
  notes?: string;
  related_vehicle_id?: number;
  related_user_id?: number;
}


export interface InventoryTransaction {
  id: number;
  transaction_type: TransactionType;

  quantity_change: number | null;
  stock_after_transaction: number;
  notes: string | null;
  timestamp: string;
  user: User | null;
  related_vehicle: Vehicle | null;
  related_user: User | null;
  part: Part | null;

  item: InventoryItem | null;
}