export interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string;
  related_vehicle_id?: number;
  notification_type: string;
  related_entity_type?: string;
  related_entity_id?: number;
}


export interface NotificationCreate {
  message: string;
  related_vehicle_id?: number;
}
