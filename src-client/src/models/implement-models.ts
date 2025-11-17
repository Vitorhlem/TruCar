



export enum ImplementStatus {
  AVAILABLE = 'available',
  IN_USE = 'in_use',
  MAINTENANCE = 'maintenance'
}


export interface Implement {
  id: number;
  name: string;
  brand: string;
  model: string;
  year: number;
  identifier?: string | null;
  type?: string | null;


  
  status: ImplementStatus; 


  acquisition_date?: string | null;
  acquisition_value?: number | null;
  notes?: string | null;
}



export type ImplementCreate = Omit<Implement, 'id' | 'status'>; 




export type ImplementUpdate = Partial<ImplementCreate & { status: Implement['status'] }>;