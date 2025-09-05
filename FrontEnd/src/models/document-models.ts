export interface DocumentPublic {
  id: number;
  document_type: string; // ex: "CNH", "CRLV"
  expiry_date: string; // ex: "2025-12-31"
  notes: string | null;
  file_url: string;
  vehicle_id: number | null;
  driver_id: number | null;
  owner_info: string | null; // ex: "Veículo: ABC-1234" ou "Motorista: João da Silva"
}