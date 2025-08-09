export interface LoginForm {
  email: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: 'manager' | 'driver';
  is_active: boolean;
}