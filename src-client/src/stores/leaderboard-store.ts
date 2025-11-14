import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { LeaderboardUser } from 'src/models/user-models';

export const useLeaderboardStore = defineStore('leaderboard', {
  state: () => ({
    leaderboard: [] as LeaderboardUser[],
    unit: '',
    isLoading: false,
  }),

  actions: {
    async fetchLeaderboard() {
      this.isLoading = true;
      try {
        const response = await api.get('/leaderboard/');
        this.leaderboard = response.data.leaderboard;
        this.unit = response.data.primary_metric_unit;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar o placar de líderes.' });
      } finally {
        this.isLoading = false;
      }
    },
  },
});