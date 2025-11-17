import type { Vehicle } from './vehicle-models';
import type { User } from './user-models';

export type FineStatus = "Pendente" | "Paga" | "Em Recurso" | "Cancelada";

export interface Fine {
  id: number;
  description: string;
  infraction_code: string | null;
  date: string;
  value: number;
  status: FineStatus;
  vehicle_id: number;
  driver_id: number | null;
  vehicle?: Vehicle;
  driver?: User;
}

export interface FineCreate {
  description: string;
  date: string;
  value: number;
  status: FineStatus;
  vehicle_id: number;
  driver_id?: number | null;
  infraction_code?: string | null;
}



export type FineUpdate = Partial<FineCreate>;