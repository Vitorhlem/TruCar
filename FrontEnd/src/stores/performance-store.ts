import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import type { DriverPerformance } from 'src/models/performance-models';

export const usePerformanceStore = defineStore('performance', () => {
  const leaderboard = ref<DriverPerformance[]>([]);
  const isLoading = ref(false);

  async function fetchLeaderboard() {
    isLoading.value = true;
    try {
      const response = await api.get<{ leaderboard: DriverPerformance[] }>('/performance/leaderboard');
      leaderboard.value = response.data.leaderboard;
    } catch (error) {
      console.error('Falha ao buscar o placar de líderes:', error);
    } finally {
      isLoading.value = false;
    }
  }
  return { leaderboard, isLoading, fetchLeaderboard };
});