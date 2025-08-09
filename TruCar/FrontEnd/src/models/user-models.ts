export interface UserCreate {
  email: string;
  full_name: string;
  password?: string; // Senha é opcional na criação via gestor
  role: 'manager' | 'driver';
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  password?: string; // Senha é opcional na atualização
  role?: 'manager' | 'driver';
  is_active?: boolean;
}