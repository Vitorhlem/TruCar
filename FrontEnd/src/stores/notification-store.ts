import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import type { Notification } from 'src/models/notification-models';

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([]);
  const unreadCount = ref(0);
  const isLoading = ref(false);

  async function fetchUnreadCount() {
    try {
      const response = await api.get<number>('/notifications/unread-count');
      unreadCount.value = response.data;
    } catch (error) {
      console.error('Falha ao buscar contagem de notificações:', error);
    }
  }

  async function fetchNotifications() {
    isLoading.value = true;
    try {
      const response = await api.get<Notification[]>('/notifications/');
      notifications.value = response.data;
      // Sincroniza a contagem de não lidos com a lista completa
      unreadCount.value = response.data.filter(n => !n.is_read).length;
    } catch (error) {
      console.error('Falha ao buscar notificações:', error);
    } finally {
      isLoading.value = false;
    }
  }

  async function markAsRead(notificationId: number) {
    try {
      const response = await api.post<Notification>(`/notifications/${notificationId}/read`);
      const index = notifications.value.findIndex(n => n.id === notificationId);
      if (index !== -1) {
        notifications.value[index] = response.data;
      }
      // Recalcula a contagem de não lidos
      unreadCount.value = notifications.value.filter(n => !n.is_read).length;
    } catch (error) {
      console.error('Falha ao marcar notificação como lida:', error);
    }
  }

  return {
    notifications,
    unreadCount,
    isLoading,
    fetchUnreadCount,
    fetchNotifications,
    markAsRead,
  };
});