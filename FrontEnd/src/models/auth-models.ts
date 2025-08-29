// ARQUIVO: src/models/auth-models.ts

// --- CORREÇÃO: Adicionamos TODOS os setores possíveis ao tipo ---
export type UserSector = 'agronegocio' | 'servicos' | 'frete' | 'construcao_civil' | null;

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  role: 'manager' | 'driver';
  avatar_url: string | null;
  organization: {
    id: number;
    name: string;
    sector: UserSector; // Usa o tipo completo
  };
}

// Interfaces para o formulário de login e resposta do token
export interface LoginForm {
  email: string;
  password: string;
}

export interface TokenData {
  access_token: string;
  user: User;
}