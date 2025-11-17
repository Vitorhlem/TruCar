import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { VehicleCost, VehicleCostCreate } from 'src/models/vehicle-cost-models';
import { format } from 'date-fns';

interface FetchAllCostsParams {
  startDate?: Date | null;
  endDate?: Date | null;
}

export const useVehicleCostStore = defineStore('vehicleCost', {
  state: () => ({
    costs: [] as VehicleCost[],
    isLoading: false,
  }),

  actions: {


    async fetchCosts(vehicleId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<VehicleCost[]>(`/vehicles/${vehicleId}/costs/`);


        this.costs = response.data;
      } catch{
        Notify.create({ type: 'negative', message: 'Falha ao carregar a lista de custos do veículo.' });
      } finally {
        this.isLoading = false;
      }
    },



    async fetchAllCosts(params: FetchAllCostsParams = {}) {
      this.isLoading = true;
      try {
        const queryParams: Record<string, string> = {};
        if (params.startDate) {
          queryParams.start_date = format(params.startDate, 'yyyy-MM-dd');
        }
        if (params.endDate) {
          queryParams.end_date = format(params.endDate, 'yyyy-MM-dd');
        }
        
        const response = await api.get<VehicleCost[]>('/costs/', { params: queryParams });
        this.costs = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar a lista de custos.' });
      } finally {
        this.isLoading = false;
      }
    },


    async addCost(vehicleId: number, payload: VehicleCostCreate): Promise<boolean> {
      try {
        await api.post(`/vehicles/${vehicleId}/costs/`, payload);
        Notify.create({ type: 'positive', message: 'Custo adicionado com sucesso!' });
        




        return true;
      } catch  {
        Notify.create({ type: 'negative', message: 'Erro ao adicionar custo.' });
        return false;
      }
    },
  },
});