

export interface Client {
  id: number;
  name: string;
  contact_person?: string | null;
  phone?: string | null;
  email?: string | null;

  cep?: string | null;
  address_street?: string | null;
  address_number?: string | null;
  address_neighborhood?: string | null;
  address_city?: string | null;
  address_state?: string | null;
}


export type ClientUpdate = Partial<Omit<Client, 'id'>>;


export type ClientCreate = Omit<Client, 'id'>;
