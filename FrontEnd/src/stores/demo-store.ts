import { defineStore } from 'pinia';
import { api } from 'boot/axios';

export interface DemoStats {
  vehicle_count: number;
  vehicle_limit: number;
  driver_count: number;
  driver_limit: number;
  journey_count: number;
  journey_limit: number;
}

export const useDemoStore = defineStore('demo', {
  state: () => ({
    stats: null as DemoStats | null,
    isLoading: false,
  }),

  actions: {
    // Adicionamos um parâmetro 'force'
    async fetchDemoStats(force = false) {
      // A verificação agora só acontece se 'force' for falso
      if (this.stats && !force) return;

      this.isLoading = true;
      try {
        const response = await api.get<DemoStats>('/dashboard/demo-stats');
        this.stats = response.data;
      } catch (error) {
        console.error('Falha ao buscar as estatísticas da conta demo:', error);
        this.stats = null;
      } finally {
        this.isLoading = false;
      }
    },
  },
});