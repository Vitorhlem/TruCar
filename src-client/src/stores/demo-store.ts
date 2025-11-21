import { defineStore } from 'pinia';
import { api } from 'boot/axios';

export interface DemoStats {
  vehicle_count: number;
  vehicle_limit: number;
  driver_count: number;
  driver_limit: number;
  journey_count: number;
  maintenance_count: number;
  maintenance_limit: number;
  part_count: number;
  part_limit: number;
  journey_limit: number;
  cost_count: number;
  cost_limit: number;
}

// Interface auxiliar que espelha a resposta do backend
interface ApiDemoStatsResponse {
  vehicles: { current: number; limit: number };
  users: { current: number; limit: number };
  freight_orders: { current: number; limit: number };
  journeys: { current: number; limit: number }; // Novo campo adicionado no backend
  parts: { current: number; limit: number }; // O Backend já manda isso
  vehicle_costs: { current: number; limit: number };
  maintenance_requests: { current: number; limit: number }; // Campo chave
}

export const useDemoStore = defineStore('demo', {
  state: () => ({
    stats: null as DemoStats | null,
    isLoading: false,
  }),

  actions: {
    async fetchDemoStats(force = false) {
      if (this.stats && !force) return;

      this.isLoading = true;
      try {
        const response = await api.get<ApiDemoStatsResponse>('/dashboard/demo-stats');
        const data = response.data;

        this.stats = {
            vehicle_count: data.vehicles.current,
            vehicle_limit: data.vehicles.limit,
            
            driver_count: data.users.current, 
            driver_limit: data.users.limit,
            maintenance_count: data.maintenance_requests?.current ?? 0,
            maintenance_limit: data.maintenance_requests?.limit ?? 5,
            // CORREÇÃO: Agora mapeamos 'journey_count' para o campo correto 'journeys'
            // e não mais para 'freight_orders'
            journey_count: data.journeys?.current ?? 0,
            journey_limit: data.journeys?.limit ?? 10,
            part_count: data.parts?.current ?? 0,
            part_limit: data.parts?.limit ?? 50,
            cost_count: data.vehicle_costs?.current ?? 0,
            cost_limit: data.vehicle_costs?.limit ?? 15
        };
        
      } catch (error) {
        console.error('Falha ao buscar as estatísticas da conta demo:', error);
        this.stats = null;
      } finally {
        this.isLoading = false;
      }
    },
  },
});