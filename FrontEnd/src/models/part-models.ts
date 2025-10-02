export type PartCategory = "Peça" | "Pneu" | "Fluído" | "Consumível" | "Outro";

export interface Part {
  id: number;
  name: string;
  category: PartCategory;
  part_number: string | null;
  serial_number: string | null; // Adicionado
  brand: string | null;
  stock: number;
  min_stock: number;
  location: string | null;
  notes: string | null;
  photo_url: string | null;
  value: number | null; // Já estava correto
  invoice_url: string | null; // --- ADICIONADO ---
}

// Interface para criar uma nova peça (sem o id)
export type PartCreate = Omit<Part, 'id'>;

// Interface para atualizar uma peça (todos os campos são opcionais)
export type PartUpdate = Partial<PartCreate>;