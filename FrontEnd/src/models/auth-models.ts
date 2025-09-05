export type UserSector = 'agronegocio' | 'servicos' | 'frete' | 'construcao_civil' | null;

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  role: 'cliente_ativo' | 'cliente_demo' | 'driver';
  avatar_url: string | null;
  is_superuser: boolean;
  notify_in_app: boolean;
  notify_by_email: boolean;
  notification_email: string | null; // <-- CAMPO ADICIONADO
  organization: {
    id: number;
    name: string;
    sector: UserSector;
  };
}

export interface UserRegister {
  full_name: string;
  email: string;
  password: string;
  organization_name: string;
  sector: UserSector;
}

export interface LoginForm {
  email: string;
  password: string;
}

export interface TokenData {
  access_token: string;
  user: User;
}