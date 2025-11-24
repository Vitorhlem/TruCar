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
    // --- FUNÇÃO REINTRODUZIDA PARA A PÁGINA DE DETALHES ---
    /**
     * Busca no backend a lista de todos os custos para UM veículo específico.
     * @param vehicleId O ID do veículo cujos custos queremos carregar.
     */
    async fetchCosts(vehicleId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<VehicleCost[]>(`/vehicles/${vehicleId}/costs/`);
        // Esta ação pode sobrescrever os custos gerais, o que é aceitável
        // no contexto da página de detalhes do veículo.
        this.costs = response.data;
      } catch{
        Notify.create({ type: 'negative', message: 'Falha ao carregar a lista de custos do veículo.' });
      } finally {
        this.isLoading = false;
      }
    },
    // --- FIM DA FUNÇÃO REINTRODUZIDA ---

    /**
     * Busca todos os custos da organização, com filtros de data (para a página geral de custos).
     */
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

    /**
     * Adiciona um novo registo de custo para um veículo.
     */
    async addCost(vehicleId: number, payload: VehicleCostCreate): Promise<boolean> {
      try {
        await api.post(`/vehicles/${vehicleId}/costs/`, payload);
        
        // Após adicionar, podemos recarregar os custos do veículo específico ou todos,
        // dependendo do contexto da página. Para ser seguro, vamos chamar fetchAllCosts
        // se a página de custos gerais estiver ativa, ou fetchCosts se a de detalhes estiver.
        // A lógica atual de recarregar na própria página já lida com isso.
        return true;
      } catch  {
        Notify.create({ type: 'negative', message: 'Erro ao adicionar custo.' });
        return false;
      }
    },
  },
});