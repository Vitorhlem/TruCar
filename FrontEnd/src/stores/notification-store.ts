import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import type { Notification } from 'src/models/notification-models';

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [] as Notification[],
    unreadCount: 0,
    isLoading: false,
  }),

  actions: {
    async fetchUnreadCount() {
      try {
        const response = await api.get<number>('/notifications/unread-count');
        this.unreadCount = response.data;
      } catch (error) {
        console.error('Falha ao buscar contagem de notificações:', error);
      }
    },

    async fetchNotifications() {
      this.isLoading = true;
      try {
        const response = await api.get<Notification[]>('/notifications/');
        this.notifications = response.data;
        this.unreadCount = response.data.filter(n => !n.is_read).length;
      } catch (error) {
        console.error('Falha ao buscar notificações:', error);
      } finally {
        this.isLoading = false;
      }
    },

    async markAsRead(notificationId: number) {
      try {
        const response = await api.post<Notification>(`/notifications/${notificationId}/read`);
        const index = this.notifications.findIndex(n => n.id === notificationId);
        if (index !== -1) {
          this.notifications[index] = response.data;
        }
        this.unreadCount = this.notifications.filter(n => !n.is_read).length;
      } catch (error) {
        console.error('Falha ao marcar notificação como lida:', error);
      }
    },
  },
});