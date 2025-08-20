import type { User } from './auth-models';
import type { Vehicle } from './vehicle-models';

export enum MaintenanceStatus {
  PENDING = 'Pendente',
  APPROVED = 'Aprovada',
  REJECTED = 'Rejeitada',
  IN_PROGRESS = 'Em Andamento',
  COMPLETED = 'Concluída',
}

export enum MaintenanceCategory {
  MECHANICAL = "Mecânica",
  ELECTRICAL = "Elétrica",
  BODYWORK = "Funilaria",
  OTHER = "Outros",
}

export interface MaintenanceRequest {
  id: number;
  problem_description: string;
  status: MaintenanceStatus;
  category: MaintenanceCategory;
  reporter: User;
  vehicle: Vehicle;
  approver: User | null;
  manager_notes: string | null;
  created_at: string;
  updated_at: string | null;
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

// --- TIPOS DE COMENTÁRIO FALTANTES ADICIONADOS AQUI ---
export interface MaintenanceComment {
  id: number;
  comment_text: string;
  file_url: string | null;
  created_at: string;
  user: User;
}

export interface MaintenanceCommentCreate {
  comment_text: string;
  file_url?: string | null;
}