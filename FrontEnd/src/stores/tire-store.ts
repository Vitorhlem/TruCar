import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import type { TireLayout, TireInstallPayload } from 'src/models/tire-models';

export const useTireStore = defineStore('tire', {
  state: () => ({
    tireLayout: null as TireLayout | null,
    isLoading: false,
  }),

  actions: {
    async fetchTireLayout(vehicleId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<TireLayout>(`/tires/vehicles/${vehicleId}/tires`);
        this.tireLayout = response.data;
      } catch { // --- CORREÇÃO APLICADA AQUI --- (variável 'error' removida)
        Notify.create({ type: 'negative', message: 'Falha ao carregar a configuração de pneus.' });
      } finally {
        this.isLoading = false;
      }
    },

    async installTire(vehicleId: number, payload: TireInstallPayload): Promise<boolean> {
      this.isLoading = true;
      try {
        await api.post(`/tires/vehicles/${vehicleId}/tires`, payload);
        Notify.create({ type: 'positive', message: 'Pneu instalado com sucesso!' });
        await this.fetchTireLayout(vehicleId);
        return true;
      } catch (error) {
        const message = isAxiosError(error) ? error.response?.data?.detail : 'Erro ao instalar pneu.';
        Notify.create({ type: 'negative', message: message as string });
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async removeTire(tireId: number, removalKm: number, vehicleId: number): Promise<boolean> {
      this.isLoading = true;
      try {
        await api.put(`/tires/tires/${tireId}/remove?removal_km=${removalKm}`);
        Notify.create({ type: 'positive', message: 'Pneu removido e descartado com sucesso!' });
        await this.fetchTireLayout(vehicleId);
        return true;
      } catch (error) {
        const message = isAxiosError(error) ? error.response?.data?.detail : 'Erro ao remover pneu.';
        Notify.create({ type: 'negative', message: message as string });
        return false;
      } finally {
        this.isLoading = false;
      }
    },
  },
});