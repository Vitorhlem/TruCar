import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';

export interface AuditLog {
  id: number;
  action: string;
  resource_type: string;
  resource_id: string;
  user_name: string;
  created_at: string;
  // CORREÇÃO: Substituído 'any' por um tipo seguro para JSON
  details: Record<string, unknown> | null;
}

export const useAuditLogStore = defineStore('audit-log', () => {
  const logs = ref<AuditLog[]>([]);
  const isLoading = ref(false);

  async function fetchLogs() {
    isLoading.value = true;
    try {
      const response = await api.get<AuditLog[]>('/audit-logs/');
      logs.value = response.data;
    } catch (error) {
      console.error('Erro ao buscar logs de auditoria', error);
    } finally {
      isLoading.value = false;
    }
  }

  return { logs, isLoading, fetchLogs };
});