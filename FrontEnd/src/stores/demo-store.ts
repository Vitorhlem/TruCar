import { defineStore } from 'pinia';
import { api } from 'boot/axios';

// A interface é movida para fora para ser usada no 'state'
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
    async fetchDemoStats() {
      // Evita chamadas desnecessárias
      if (this.stats) return;

      this.isLoading = true;
      try {
        const response = await api.get<DemoStats>('/dashboard/demo-stats');
        this.stats = response.data;
      } catch {
        console.error('Falha ao buscar as estatísticas da conta demo:', );
        this.stats = null;
      } finally {
        this.isLoading = false;
      }
    },
  },
});