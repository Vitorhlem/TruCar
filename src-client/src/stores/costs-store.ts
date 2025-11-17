import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { type IVehicleCost, type ICostCreate } from 'src/models/cost-models';

interface CostsState {
  costs: IVehicleCost[];
  isLoading: boolean;
}


export const useVehicleCostStore = defineStore('vehicleCost', {
  state: (): CostsState => ({
    costs: [],
    isLoading: false,
  }),

  actions: {

    async fetchAllCosts(params?: { startDate?: Date, endDate?: Date }) {
      this.isLoading = true;
      try {
        const response = await api.get<IVehicleCost[]>('/costs/', { params });
        this.costs = response.data;
      } catch (error) {
        console.error('Falha ao buscar todos os custos:', error);
        Notify.create({ type: 'negative', message: 'Não foi possível carregar os custos.' });
      } finally {
        this.isLoading = false;
      }
    },


    async fetchCostsByVehicle(vehicleId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<IVehicleCost[]>(`/vehicles/${vehicleId}/costs`);
        this.costs = response.data;
      } catch (error) {
        console.error('Falha ao buscar custos do veículo:', error);
        Notify.create({ type: 'negative', message: 'Não foi possível carregar os custos do veículo.' });
      } finally {
        this.isLoading = false;
      }
    },


    async addCost(vehicleId: number, costData: Omit<ICostCreate, 'vehicle_id'>) {
      try {
        const payload = { ...costData, vehicle_id: vehicleId };
        await api.post('/vehicle_costs/', payload);
        Notify.create({ type: 'positive', message: 'Custo adicionado com sucesso!' });
        

        await this.fetchCostsByVehicle(vehicleId);
      } catch (error) {
        console.error('Erro ao adicionar custo:', error);
        Notify.create({ type: 'negative', message: 'Erro ao salvar o novo custo.' });
        throw error;
      }
    },
  },
});