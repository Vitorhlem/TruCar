// ARQUIVO: src/models/client-models.ts

export interface Client {
  id: number;
  name: string;
  contact_person?: string | null;
  phone?: string | null;
  email?: string | null;
}

// Usamos 'Partial' para o Update, pois todos os campos são opcionais
export type ClientUpdate = Partial<Omit<Client, 'id'>>;

// Omitimos 'id' para o Create
export type ClientCreate = Omit<Client, 'id'>;