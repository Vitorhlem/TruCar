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

/**
 * Define os campos que podem ser enviados ao atualizar uma organização.
 * Todos os campos são opcionais.
 */
export interface OrganizationUpdate {
  name?: string;
  sector?: UserSector;
}
