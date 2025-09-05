import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { type IVehicleCost, type ICostCreate } from 'src/models/cost-models';

interface CostsState {
  costs: IVehicleCost[];
  isLoading: boolean;
}

export const useCostsStore = defineStore('costs', {
  state: (): CostsState => ({
    costs: [],
    isLoading: false,
  }),

  actions: {
    // Ação para buscar todos os custos de um veículo específico
    async fetchCostsByVehicle(vehicleId: number) {
      this.isLoading = true;
      try {
        // O backend já tem o endpoint para listar custos de um veículo
        const response = await api.get<IVehicleCost[]>(`/vehicles/${vehicleId}/costs`);
        this.costs = response.data;
      } catch (error) {
        console.error('Falha ao buscar custos do veículo:', error);
        Notify.create({ type: 'negative', message: 'Não foi possível carregar os custos.' });
      } finally {
        this.isLoading = false;
      }
    },

    // Ação para adicionar um novo custo a um veículo
    async addCostToVehicle(vehicleId: number, costData: Omit<ICostCreate, 'vehicle_id'>) {
      try {
        const payload = { ...costData, vehicle_id: vehicleId };
        await api.post('/vehicle_costs/', payload);
        Notify.create({ type: 'positive', message: 'Custo adicionado com sucesso!' });
        
        // Após adicionar, atualizamos a lista para mostrar o novo item
        await this.fetchCostsByVehicle(vehicleId);
      } catch (error) {
        console.error('Erro ao adicionar custo:', error);
        Notify.create({ type: 'negative', message: 'Erro ao salvar o novo custo.' });
        throw error;
      }
    },
  },
});