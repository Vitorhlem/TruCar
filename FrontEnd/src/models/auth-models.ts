// Define a estrutura para o objeto Organization que vem dentro do User
export interface Organization {
  id: number;
  name: string;
  sector: 'agronegocio' | 'construcao_civil' | 'servicos';
}

// Define a estrutura para o objeto User
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  role: 'manager' | 'driver';
  avatar_url: string | null;
  organization: Organization;
}

// A interface CORRIGIDA para a RESPOSTA COMPLETA do login
export interface TokenData {
  access_token: string;
  token_type: string;
  user: User;
}

// A interface para o FORMULÁRIO de login
export interface LoginForm {
  email: string;
  password: string;
}