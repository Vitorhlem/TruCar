import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import type { TireLayout, TireInstallPayload, VehicleTireHistory } from 'src/models/tire-models';

export const useTireStore = defineStore('tire', {
  state: () => ({
    tireLayout: null as TireLayout | null,
    removedTiresHistory: [] as VehicleTireHistory[],
    isLoading: false,
  }),

  actions: {
    async fetchTireLayout(vehicleId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<TireLayout>(`/tires/vehicles/${vehicleId}/tires`);
        this.tireLayout = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar a configuração de pneus.' });
      } finally {
        this.isLoading = false;
      }
    },

    async fetchRemovedTiresHistory(vehicleId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<VehicleTireHistory[]>(`/tires/vehicles/${vehicleId}/removed-tires`);
        this.removedTiresHistory = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar o histórico de pneus removidos.' });
      } finally {
        this.isLoading = false;
      }
    },

    async installTire(vehicleId: number, payload: TireInstallPayload): Promise<boolean> {
      this.isLoading = true;
      try {
        await api.post(`/tires/vehicles/${vehicleId}/tires`, payload);
        Notify.create({ type: 'positive', message: 'Pneu instalado com sucesso!' });
        return true;
      } catch (error) {
        const message = isAxiosError(error) ? error.response?.data?.detail : 'Erro ao instalar pneu.';
        Notify.create({ type: 'negative', message: message as string });
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async removeTire(tireId: number, removal_km: number, removal_engine_hours?: number): Promise<boolean> {
      this.isLoading = true;
      try {
        const payload: { removal_km: number, removal_engine_hours?: number } = { removal_km };
        if (removal_engine_hours !== undefined && removal_engine_hours !== null) {
          payload.removal_engine_hours = removal_engine_hours;
        }

        await api.put(`/tires/tires/${tireId}/remove`, payload);

        Notify.create({ type: 'positive', message: 'Pneu removido com sucesso!' });
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