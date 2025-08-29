// ARQUIVO: src/models/freight-order-models.ts

import type { Client } from './client-models';
import type { User } from './auth-models';
import type { Vehicle } from './vehicle-models';

export type FreightStatus = "Pendente" | "Em Trânsito" | "Entregue" | "Cancelado";
export type StopPointType = "Coleta" | "Entrega";
export type StopPointStatus = "Pendente" | "Concluído";

export interface StopPoint {
  id: number;
  sequence_order: number;
  type: StopPointType;
  status: StopPointStatus;
  address: string;
  cargo_description?: string | null;
  scheduled_time: string;
  actual_arrival_time?: string | null;
}

// --- CORREÇÃO: Transformado de interface para type para calar o linter ---
export type StopPointCreate = Omit<StopPoint, 'id' | 'status' | 'actual_arrival_time'>;

export interface FreightOrder {
  id: number;
  status: FreightStatus;
  description?: string | null;
  scheduled_start_time?: string | null;
  scheduled_end_time?: string | null;
  client: Client;
  vehicle?: Vehicle | null;
  driver?: User | null;
  stop_points: StopPoint[];
}

export interface FreightOrderCreate {
  client_id: number;
  description?: string | null;
  stop_points: StopPointCreate[];
}

export interface FreightOrderUpdate {
  description?: string | null;
  status?: FreightStatus;
  vehicle_id?: number | null;
  driver_id?: number | null;
}