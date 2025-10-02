export interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string; // string no formato ISO
  related_vehicle_id?: number; // --- NOVO CAMPO OPCIONAL ---
}

// --- NOVA INTERFACE ADICIONADA ---
export interface NotificationCreate {
  message: string;
  related_vehicle_id?: number;
}
