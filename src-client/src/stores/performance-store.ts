import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import type { DriverPerformance } from 'src/models/performance-models';

export const usePerformanceStore = defineStore('performance', {
  state: () => ({
    leaderboard: [] as DriverPerformance[],
    isLoading: false,
  }),

  actions: {
    async fetchLeaderboard() {
      this.isLoading = true;
      try {
        const response = await api.get<{ leaderboard: DriverPerformance[] }>('/performance/leaderboard');
        this.leaderboard = response.data.leaderboard;
      } catch (error) {
        console.error('Falha ao buscar o placar de líderes:', error);
      } finally {
        this.isLoading = false;
      }
    },
  },
});