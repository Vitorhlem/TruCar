// Em FrontEnd/src/models/auth-models.ts

// A interface para o objeto Organization
export interface Organization {
  id: number;
  name: string;
  sector: 'agronegocio' | 'construcao_civil' | 'servicos';
}

// A interface para o objeto User
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  role: 'manager' | 'driver';
  avatar_url: string | null;
  organization: Organization; // A organização vem aninhada
}

// A interface para o objeto Token
export interface Token {
  access_token: string;
  token_type: string;
}

// A interface para a RESPOSTA COMPLETA do login, que contém o user e o token
export interface TokenData {
  user: User;
  token: Token;
}

// A interface para o FORMULÁRIO de login
export interface LoginForm {
  email: string;
  password: string;
}