import type { User } from './auth-models';
import type { Vehicle } from './vehicle-models';
import type { Part } from './part-models';
// --- 1. IMPORTAR O MODELO DE ITEM ---
import type { InventoryItem } from './inventory-item-models';

export type TransactionType = "Entrada" | "Saída para Uso" | "Fim de Vida" | "Retorno" | "Ajuste Inicial" | "Ajuste Manual";

// O que enviamos para a API para criar uma transação
export interface TransactionCreate {
  transaction_type: TransactionType;
  quantity: number; // Sempre positivo
  notes?: string;
  related_vehicle_id?: number;
  related_user_id?: number;
}

// O que recebemos da API ao consultar o histórico
export interface InventoryTransaction {
  id: number;
  transaction_type: TransactionType;
  // --- 2. CORRIGIDO: O campo pode ser nulo ---
  quantity_change: number | null; // Pode ser negativo
  stock_after_transaction: number;
  notes: string | null;
  timestamp: string; // Data ISO
  user: User | null;
  related_vehicle: Vehicle | null;
  related_user: User | null;
  part: Part | null; // <-- PROPRIEDADE ADICIONADA
  // --- 3. ADICIONADO: O item de inventário real (para pegar o ID) ---
  item: InventoryItem | null;
}