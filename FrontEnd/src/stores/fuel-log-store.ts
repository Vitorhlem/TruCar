import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { FuelLog, FuelLogCreate } from 'src/models/fuel-log-models';

export const useFuelLogStore = defineStore('fuelLog', {
  state: () => ({
    fuelLogs: [] as FuelLog[],
    isLoading: false,
  }),

  actions: {
    async fetchFuelLogs() {
      this.isLoading = true;
      try {
        const response = await api.get<FuelLog[]>('/fuel-logs/');
        this.fuelLogs = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar registros de abastecimento.' });
      } finally {
        this.isLoading = false;
      }
    },

    async createFuelLog(payload: FuelLogCreate) {
      this.isLoading = true; // Corrigido para this.isLoading
      try {
        const response = await api.post<FuelLog>('/fuel-logs/', payload);
        this.fuelLogs.unshift(response.data);
        Notify.create({ type: 'positive', message: 'Abastecimento registrado com sucesso!' });
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao registrar abastecimento.' });
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});