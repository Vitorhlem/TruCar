import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import type { VehicleComponent, VehicleComponentCreate } from 'src/models/vehicle-component-models';

export const useVehicleComponentStore = defineStore('vehicleComponent', {
  state: () => ({
    components: [] as VehicleComponent[],
    isLoading: false,
    currentVehicleId: null as number | null, // <-- ADICIONE ESTA LINHA
  }),
  actions: {
    async fetchComponents(vehicleId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<VehicleComponent[]>(`/vehicles/${vehicleId}/components`);
        this.components = response.data;
        this.currentVehicleId = vehicleId; // <-- ADICIONE ESTA LINHA
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar componentes do veículo.' });
        this.currentVehicleId = null; // <-- Opcional: limpar em caso de falha
      } finally {
        this.isLoading = false;
      }
    },

    async installComponent(vehicleId: number, payload: VehicleComponentCreate): Promise<boolean> {
      this.isLoading = true;
      try {
        await api.post(`/vehicles/${vehicleId}/components`, payload);
        Notify.create({ type: 'positive', message: 'Componente instalado com sucesso!' });
        await this.fetchComponents(vehicleId); // Recarrega a lista
        return true;
      } catch (error) {
        const message = isAxiosError(error) ? error.response?.data?.detail : 'Erro ao instalar componente.';
        Notify.create({ type: 'negative', message: message as string });
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async discardComponent(componentId: number, vehicleId: number) {
      this.isLoading = true;
      try {
        await api.put(`/vehicle-components/${componentId}/discard`);
        Notify.create({ type: 'positive', message: 'Componente marcado como descartado.' });
        await this.fetchComponents(vehicleId);
        return true; // Recarrega a lista
      } catch {
        Notify.create({ type: 'negative', message: 'Erro ao descartar componente.' });
        return false;
      } finally {
        this.isLoading = false;
      }
    },
  },
});