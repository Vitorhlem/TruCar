import type { User, UserSector } from './auth-models';

/**
 * Representa o objeto completo de uma Organização, como recebido da API.
 * Inclui a lista de utilizadores para que possamos determinar o status (demo/ativo).
 */
export interface Organization {
  id: number;
  name: string;
  sector: UserSector;
  users?: User[]; // A lista de utilizadores associados
}

export interface OrganizationFuelIntegrationPublic {
  fuel_provider_name: string | null;
  is_api_key_set: boolean;
  is_api_secret_set: boolean;
}

// Usado para enviar os dados do formulário de configuração para o backend
export interface OrganizationFuelIntegrationUpdate {
  fuel_provider_name?: string;
  fuel_provider_api_key?: string;
  fuel_provider_api_secret?: string;
}

/**
 * Define os campos que podem ser enviados ao atualizar uma organização.
 * Todos os campos são opcionais.
 */
export interface OrganizationUpdate {
  name?: string;
  sector?: UserSector;
}
