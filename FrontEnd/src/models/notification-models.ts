export interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string; // string no formato ISO
}