// src-client/src/models/maintenance-models.ts

import type { User } from './auth-models';
import type { Vehicle } from './vehicle-models';
import type { InventoryItemStatus } from './inventory-item-models';
import type { VehicleComponent } from './vehicle-component-models';

export enum MaintenanceStatus {
  PENDENTE = 'PENDENTE',
  APROVADA = 'APROVADA',
  REJEITADA = 'REJEITADA',
  EM_ANDAMENTO = 'EM ANDAMENTO',
  CONCLUIDA = 'CONCLUIDA',
}

export enum MaintenanceCategory {
  MECHANICAL = 'Mecânica',
  ELECTRICAL = 'Elétrica',
  BODYWORK = 'Funilaria',
  OTHER = 'Outro',
}

export interface MaintenanceComment {
  id: number;
  comment_text: string;
  file_url: string | null;
  created_at: string;
  user: User | null;
}

export interface ReplaceComponentPayload {
  component_to_remove_id: number;
  new_item_id: number;
  old_item_status: InventoryItemStatus;
  notes?: string | null;
}

export interface InstallComponentPayload {
  new_item_id: number;
  notes?: string | null;
}

export interface MaintenancePartChangePublic {
  id: number;
  timestamp: string;
  user: User;
  notes: string | null;
  component_removed: VehicleComponent | null;
  component_installed: VehicleComponent;
  is_reverted: boolean;
}

export interface ReplaceComponentResponse {
  success: boolean;
  message: string;
  part_change_log: MaintenancePartChangePublic;
  new_comment: MaintenanceComment;
}

export interface InstallComponentResponse {
  success: boolean;
  message: string;
  part_change_log: MaintenancePartChangePublic;
  new_comment: MaintenanceComment;
}

// --- ADICIONADO ---
export interface MaintenanceServiceItem {
  id: number;
  description: string;
  cost: number;
  provider_name?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface MaintenanceServiceItemCreate {
  description: string;
  cost: number;
  provider_name?: string | null;
  notes?: string | null;
}
// --- FIM DA ADIÇÃO ---

export interface MaintenanceRequest {
  id: number;
  problem_description: string;
  status: MaintenanceStatus;
  category: MaintenanceCategory;
  reporter: User | null;
  vehicle: Vehicle;
  approver: User | null;
  manager_notes: string | null;
  created_at: string;
  updated_at: string | null;
  comments: MaintenanceComment[];
  part_changes: MaintenancePartChangePublic[];
  services: MaintenanceServiceItem[]; // <-- Adicionado anteriormente
}

export interface MaintenanceRequestCreate {
  vehicle_id: number;
  problem_description: string;
  category: MaintenanceCategory;
}

export interface MaintenanceRequestUpdate {
  status: MaintenanceStatus;
  manager_notes?: string | null;
}

export interface MaintenanceCommentCreate {
  comment_text: string;
  file_url?: string | null;
}