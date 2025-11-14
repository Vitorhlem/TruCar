export interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string; // string no formato ISO
  related_vehicle_id?: number; // --- NOVO CAMPO OPCIONAL ---
  notification_type: string; // Adiciona o tipo para podermos usar ícones diferentes
  related_entity_type?: string; // Adiciona o tipo de entidade para links (ex: 'maintenance_request')
  related_entity_id?: number; // Adiciona o ID da entidade para construir o link
}

// --- NOVA INTERFACE ADICIONADA ---
export interface NotificationCreate {
  message: string;
  related_vehicle_id?: number;
}
