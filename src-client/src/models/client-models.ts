// ARQUIVO: src/models/client-models.ts

export interface Client {
  id: number;
  name: string;
  contact_person?: string | null;
  phone?: string | null;
  email?: string | null;
  // --- CAMPOS DE ENDEREÇO ADICIONADOS ---
  cep?: string | null;
  address_street?: string | null;
  address_number?: string | null;
  address_neighborhood?: string | null;
  address_city?: string | null;
  address_state?: string | null;
}

// Usamos 'Partial' para o Update, pois todos os campos são opcionais
export type ClientUpdate = Partial<Omit<Client, 'id'>>;

// Omitimos 'id' para o Create
export type ClientCreate = Omit<Client, 'id'>;
