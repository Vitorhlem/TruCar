import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import type { DashboardSummary } from 'src/models/report-models';

export const useDashboardStore = defineStore('dashboard', {
  // 1. As variáveis ('refs') agora vivem dentro do 'state'
  state: () => ({
    summary: null as DashboardSummary | null,
    isLoading: false,
  }),

  // 2. As funções agora vivem dentro de 'actions'
  actions: {
    async fetchSummary() {
      this.isLoading = true; // 3. Usamos 'this' em vez de '.value'
      try {
        const response = await api.get<DashboardSummary>('/dashboard/summary');
        this.summary = response.data;
      } catch (error) {
        console.error('Falha ao buscar dados do dashboard:', error);
      } finally {
        this.isLoading = false;
      }
    },
  },
});