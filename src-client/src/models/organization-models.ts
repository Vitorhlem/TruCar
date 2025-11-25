// Em: src-client/src/models/organization-models.ts
import type { UserRole, UserSector } from './auth-models';

export interface OrganizationNestedInUser {
  id: number;
  name: string;
  sector: UserSector;
  vehicle_limit: number;
  driver_limit: number;
  freight_order_limit: number;
  maintenance_limit: number;
  part_limit?: number; 
}

export interface UserNestedInOrganization {
  id: number;
  role: UserRole;
}

export interface OrganizationBase {
  name: string;
  sector: UserSector;
  // --- CAMPOS DE CADASTRO (Re-adicionados) ---
  cnpj?: string;
  address?: string;
  contact_phone?: string;
  website?: string;
  // ------------------------------------------
}

export interface Organization extends OrganizationBase {
  id: number;
  users: UserNestedInOrganization[];
  vehicle_limit: number;
  driver_limit: number;
  freight_order_limit: number;
  maintenance_limit: number;
  part_limit?: number; 
}

// --- CORREÇÃO DO ERRO ---
// Criamos um alias exportado para satisfazer a importação de 'OrganizationPublic'
export type OrganizationPublic = Organization;
// ------------------------

export interface OrganizationUpdate {
  name?: string;
  sector?: UserSector;
  vehicle_limit?: number;
  driver_limit?: number;
  freight_order_limit?: number;
  maintenance_limit?: number;
  part_limit?: number;
  // --- CAMPOS DE CADASTRO NO UPDATE ---
  cnpj?: string;
  address?: string;
  contact_phone?: string;
  website?: string;
  // ------------------------------------
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