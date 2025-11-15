// FrontEnd/src/models/implement-models.ts

// --- 1. ADICIONE O ENUM AQUI ---
// (Isso espelha o seu modelo do backend em implement_model.py)
export enum ImplementStatus {
  AVAILABLE = 'available',
  IN_USE = 'in_use',
  MAINTENANCE = 'maintenance'
}

// A interface principal para um Implemento
export interface Implement {
  id: number;
  name: string;
  brand: string;
  model: string;
  year: number;
  identifier?: string | null;
  type?: string | null; // Ex: "Arado", "Plantadeira"
  
  // --- 2. USE O ENUM AQUI ---
  // (Isso torna o tipo mais forte e consistente)
  status: ImplementStatus; 

  // Campos de aquisição que adicionamos
  acquisition_date?: string | null;
  acquisition_value?: number | null;
  notes?: string | null;
}

// O tipo para a CRIAÇÃO de um novo implemento
// (O 'Omit' já remove 'status', o que está correto)
export type ImplementCreate = Omit<Implement, 'id' | 'status'>; 


// O tipo para a ATUALIZAÇÃO (todos os campos são opcionais)
// (O '& { status: ... }' está correto)
export type ImplementUpdate = Partial<ImplementCreate & { status: Implement['status'] }>;