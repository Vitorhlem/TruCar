// FrontEnd/src/models/implement-models.ts

// A interface principal para um Implemento
export interface Implement {
  id: number;
  name: string;
  brand: string;
  model: string;
  year: number;
  identifier?: string | null;
}

// O tipo para a CRIAÇÃO de um novo implemento
export type ImplementCreate = Omit<Implement, 'id'>;

// O tipo para a ATUALIZAÇÃO (todos os campos são opcionais)
export type ImplementUpdate = Partial<ImplementCreate>;