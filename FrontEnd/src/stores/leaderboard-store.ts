// ARQUIVO: src/stores/leaderboard-store.ts

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { LeaderboardUser } from 'src/models/user-models'; // Vamos criar este tipo

export const useLeaderboardStore = defineStore('leaderboard', () => {
  const leaderboard = ref<LeaderboardUser[]>([]);
  const unit = ref('');
  const isLoading = ref(false);

  async function fetchLeaderboard() {
    isLoading.value = true;
    try {
      const response = await api.get('/leaderboard/');
      leaderboard.value = response.data.leaderboard;
      unit.value = response.data.primary_metric_unit;
    } catch {
      Notify.create({ type: 'negative', message: 'Falha ao carregar o placar de líderes.' });
    } finally {
      isLoading.value = false;
    }
  }

  return {
    leaderboard,
    unit,
    isLoading,
    fetchLeaderboard,
  };
});