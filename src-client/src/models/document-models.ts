export interface DocumentPublic {
  id: number;
  document_type: string;
  expiry_date: string;
  notes: string | null;
  file_url: string;
  vehicle_id: number | null;
  driver_id: number | null;
  owner_info: string | null;
}