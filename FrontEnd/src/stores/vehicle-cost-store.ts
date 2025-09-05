import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { VehicleCost, VehicleCostCreate } from 'src/models/vehicle-cost-models';

export const useVehicleCostStore = defineStore('vehicleCost', {
  state: () => ({
    costs: [] as VehicleCost[],
    isLoading: false,
  }),

  actions: {
    /**
     * Busca no backend a lista de todos os custos para um veículo específico.
     * @param vehicleId O ID do veículo cujos custos queremos carregar.
     */
    async fetchCosts(vehicleId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<VehicleCost[]>(`/vehicles/${vehicleId}/costs/`);
        this.costs = response.data;
      } catch{
        Notify.create({ type: 'negative', message: 'Falha ao carregar a lista de custos.' });
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Adiciona um novo registo de custo para um veículo.
     * @param vehicleId O ID do veículo ao qual o custo pertence.
     * @param payload Os dados do novo custo a ser criado.
     */
    async addCost(vehicleId: number, payload: VehicleCostCreate) {
      try {
        await api.post(`/vehicles/${vehicleId}/costs/`, payload);
        Notify.create({ type: 'positive', message: 'Custo adicionado com sucesso!' });
        // Recarrega a lista de custos para mostrar o novo item
        await this.fetchCosts(vehicleId);
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao adicionar custo.' });
        throw error;
      }
    },
  },
});