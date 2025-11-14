// --- 1. IMPORTAR O NOVO MODELO DE ITEM ---
import type { InventoryItem } from './inventory-item-models';

export type PartCategory = "Peça" | "Pneu" | "Fluído" | "Consumível" | "Outro";

export interface Part {
  id: number;
  name: string;
  category: PartCategory;
  part_number: string | null;
  serial_number: string | null; 
  brand: string | null;
  stock: number; // Este agora é calculado e vem do PartPublic
  minimum_stock: number;
  location: string | null;
  notes: string | null;
  photo_url: string | null;
  value: number | null; 
  invoice_url: string | null;
  lifespan_km: number | null; 
  items: InventoryItem[]; // <-- 2. ADICIONADO
}

// 3. REMOVIDO 'stock'
export interface PartCreate extends Omit<Part, 'id' | 'stock' | 'items'> {
  initial_quantity?: number; // <-- Adicionado para o formulário
}

export type PartUpdate = Partial<Omit<PartCreate, 'initial_quantity'>>;