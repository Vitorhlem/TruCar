export interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string; // string no formato ISO
  related_vehicle_id?: number;
  
  // O uso de (string & {}) permite manter o autocomplete para os tipos conhecidos
  // sem que o ESLint reclame de redundância, pois tecnicamente não é apenas 'string'.
  notification_type: 
    | 'maintenance_due_date'
    | 'maintenance_due_km'
    | 'document_expiring'
    | 'low_stock'
    | 'tire_status_bad'
    | 'abnormal_fuel_consumption'
    | 'cost_exceeded'
    | 'new_fine_registered'
    | 'fine_payment_due'
    | 'freight_assigned'
    | 'freight_updated'
    | 'maintenance_request_new'
    | 'maintenance_request_status_update'
    | 'maintenance_request_new_comment'
    | 'journey_started'
    | 'journey_ended'
    | 'achievement_unlocked'
    | 'leaderboard_top3'
    | (string & {}); 

  related_entity_type?: string; 
  related_entity_id?: number; 
}

export interface NotificationCreate {
  message: string;
  related_vehicle_id?: number;
  notification_type?: string;
}