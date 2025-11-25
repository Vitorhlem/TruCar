// --- Conteúdo Existente ---
export interface LoginForm {
  email: string;
  password: string;
}

export type UserRole = 'cliente_ativo' | 'cliente_demo' | 'driver' | 'admin';
export type UserSector = 'agronegocio' | 'frete' | 'servicos' | 'construcao_civil' | null;

export interface Organization {
  id: number;
  name: string;
  sector: UserSector;
  part_limit?: number; // <--- ADICIONE ESTA LINHA AQUI
}

export interface OrganizationNestedInUser {
  id: number;
  name: string;
  sector: UserSector;
  // --- CAMPOS DE LIMITE ADICIONADOS ---
  vehicle_limit: number;
  driver_limit: number;
  freight_order_limit: number;
  maintenance_limit: number;
  part_limit?: number; // <--- ADICIONE ESTA LINHA AQUI
  // --- FIM DA ADIÇÃO ---
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  employee_id: string;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  avatar_url: string | null;
  notify_in_app: boolean;
  phone: string | null;
  notify_by_email: boolean;
  notification_email: string | null;
  organization: OrganizationNestedInUser | null; // <-- Esta linha usa a interface que acabamos de corrigir
}

export interface TokenData {
  access_token: string;
  token_type: string;
  user: User;
}

export interface PasswordRecoveryRequest {
  email: string;
}

export interface PasswordResetRequest {
  token: string;
  new_password: string;
}

export interface UserRegister {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
  sector: UserSector;
}