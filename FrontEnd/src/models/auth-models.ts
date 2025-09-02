export type UserSector = 'agronegocio' | 'servicos' | 'frete' | 'construcao_civil' | null;

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  // --- CORRIGIDO ---
  // Atualizamos os papéis para refletir a nova lógica de negócio
  role: 'cliente_ativo' | 'cliente_demo' | 'driver';
  // --- FIM DA CORREÇÃO ---
  avatar_url: string | null;
  organization: {
    id: number;
    name: string;
    sector: UserSector;
    // O campo 'plan_status' foi REMOVIDO daqui por ser obsoleto
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
