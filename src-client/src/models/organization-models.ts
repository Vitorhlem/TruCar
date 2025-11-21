// Em: src/models/organization-models.ts
import type { UserRole, UserSector } from './auth-models';

// --- ESTA INTERFACE PRECISA SER ATUALIZADA ---
export interface OrganizationNestedInUser {
  id: number;
  name: string;
  sector: UserSector;
  // --- CAMPOS ADICIONADOS ---
  vehicle_limit: number;
  driver_limit: number;
  freight_order_limit: number;
  maintenance_limit: number;
  // --- FIM DA ADIÇÃO ---
}
// --- FIM DA ATUALIZAÇÃO ---

export interface UserNestedInOrganization {
  id: number;
  role: UserRole;
}

export interface OrganizationBase {
  name: string;
  sector: UserSector;
}

export interface Organization extends OrganizationBase {
  id: number;
  users: UserNestedInOrganization[];
  // --- CAMPOS ADICIONADOS ---
  vehicle_limit: number;
  driver_limit: number;
  freight_order_limit: number;
  maintenance_limit: number;
  part_limit?: number; // <--- Este corrige o erro da PartsPage
  // --- FIM DA ADIÇÃO ---
}

export interface OrganizationUpdate {
  name?: string;
  sector?: UserSector;
  // --- CAMPOS ADICIONADOS ---
  vehicle_limit?: number;
  driver_limit?: number;
  freight_order_limit?: number;
  maintenance_limit?: number;
  // --- FIM DA ADIÇÃO ---
}

export interface OrganizationFuelIntegrationPublic {
  fuel_provider_name: string | null;
  is_api_key_set: boolean;
  is_api_secret_set: boolean;
}

export interface OrganizationFuelIntegrationUpdate {
  fuel_provider_name?: string;
  fuel_provider_api_key?: string;
  fuel_provider_api_secret?: string;
}