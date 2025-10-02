export type PartCategory = "Peça" | "Pneu" | "Fluído" | "Consumível" | "Outro";

export interface Part {
  id: number;
  name: string;
  category: PartCategory;
  part_number: string | null;
  serial_number: string | null; 
  brand: string | null;
  stock: number;
  min_stock: number;
  location: string | null;
  notes: string | null;
  photo_url: string | null;
  value: number | null; 
  invoice_url: string | null;
  lifespan_km: number | null; 

}

export type PartCreate = Omit<Part, 'id'>;

export type PartUpdate = Partial<PartCreate>;