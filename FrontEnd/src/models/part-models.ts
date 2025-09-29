export type PartCategory = "Peça" | "Fluído" | "Consumível" | "Outro";

export interface Part {
  id: number;
  name: string;
  category: PartCategory; // <-- CAMPO ADICIONADO
  part_number: string | null;
  brand: string | null;
  stock: number;
  min_stock: number;
  location: string | null;
  notes: string | null;
  photo_url: string | null;
}

// Interface para criar uma nova peça (sem o id)
export type PartCreate = Omit<Part, 'id'>;

// Interface para atualizar uma peça (todos os campos são opcionais)
export type PartUpdate = Partial<PartCreate>;