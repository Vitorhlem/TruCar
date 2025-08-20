import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import type { DashboardSummary } from 'src/models/report-models';

export const useDashboardStore = defineStore('dashboard', () => {
  const summary = ref<DashboardSummary | null>(null);
  const isLoading = ref(false);

  async function fetchSummary() {
    isLoading.value = true;
    try {
      const response = await api.get<DashboardSummary>('/reports/dashboard-summary');
      summary.value = response.data;
    } catch (error) {
      console.error('Falha ao buscar dados do dashboard:', error);
    } finally {
      isLoading.value = false;
    }
  }
  return { summary, isLoading, fetchSummary };
});