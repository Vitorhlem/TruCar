import type { User } from './auth-models';
import type { Vehicle } from './vehicle-models';

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
  quantity_change: number; // Pode ser negativo
  stock_after_transaction: number;
  notes: string | null;
  timestamp: string; // Data ISO
  user: User | null;
  related_vehicle: Vehicle | null;
  related_user: User | null;
}