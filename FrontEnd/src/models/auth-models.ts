// --- Conteúdo Existente ---
export interface LoginForm {
  email: string;
  password: string;
}

export type UserRole = 'cliente_ativo' | 'cliente_demo' | 'driver';
export type UserSector = 'agronegocio' | 'frete' | 'servicos' | 'construcao_civil' | null;

export interface Organization {
  id: number;
  name: string;
  sector: UserSector;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  employee_id: string;
  role: UserRole;
  is_active: boolean;
  avatar_url: string | null;
  notify_in_app: boolean;
  notify_by_email: boolean;
  notification_email: string | null;
  organization: Organization;
  is_superuser?: boolean;
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