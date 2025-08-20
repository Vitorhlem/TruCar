import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { FuelLog, FuelLogCreate } from 'src/models/fuel-log-models';

export const useFuelLogStore = defineStore('fuelLog', () => {
  const fuelLogs = ref<FuelLog[]>([]);
  const isLoading = ref(false);

  async function fetchFuelLogs() {
    isLoading.value = true;
    try {
      const response = await api.get<FuelLog[]>('/fuel-logs/');
      fuelLogs.value = response.data;
    } catch {
      Notify.create({ type: 'negative', message: 'Falha ao carregar registros de abastecimento.' });
    } finally {
      isLoading.value = false;
    }
  }

  async function createFuelLog(payload: FuelLogCreate) {
    isLoading.value = true;
    try {
      const response = await api.post<FuelLog>('/fuel-logs/', payload);
      fuelLogs.value.unshift(response.data);
      Notify.create({ type: 'positive', message: 'Abastecimento registrado com sucesso!' });
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao registrar abastecimento.' });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    fuelLogs,
    isLoading,
    fetchFuelLogs,
    createFuelLog,
  };
});