


import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { FuelLog, FuelLogCreate, FuelLogUpdate } from 'src/models/fuel-log-models';
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



    async updateFuelLog(logId: number, payload: FuelLogUpdate) {
      this.isLoading = true;
      try {
        const response = await api.put<FuelLog>(`/fuel-logs/${logId}`, payload);
        

        const index = this.fuelLogs.findIndex(log => log.id === logId);
        if (index !== -1) {
          this.fuelLogs[index] = response.data;
        }
        
        Notify.create({ type: 'positive', message: 'Registro atualizado com sucesso!' });
        
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Falha ao atualizar o registro.' });
        console.error('Erro ao atualizar:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async createFuelLog(payload: FuelLogCreate) {
      this.isLoading = true;
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


    async syncWithProvider() {
      this.isLoading = true;
      try {
        const response = await api.post<{ message: string }>('/fuel-logs/sync');
        
        Notify.create({
          type: 'positive',
          message: response.data.message || 'Sincronização iniciada.',
          timeout: 4000
        });

        await this.fetchFuelLogs();

      } catch (error) {
        Notify.create({ type: 'negative', message: 'Falha ao sincronizar com o provedor.' });
        console.error('Erro na sincronização:', error);
      } finally {
        this.isLoading = false;
      }
    },



    async deleteFuelLog(logId: number) {
      this.isLoading = true;
      try {

        await api.delete(`/fuel-logs/${logId}`);
        

        this.fuelLogs = this.fuelLogs.filter(log => log.id !== logId);
        
        Notify.create({ type: 'positive', message: 'Registro excluído com sucesso!' });
        
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Falha ao excluir o registro.' });
        console.error('Erro ao excluir:', error);
      } finally {
        this.isLoading = false;
      }
    },
  },
});