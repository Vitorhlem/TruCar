import { defineStore } from 'pinia';
import { api } from 'boot/axios';
// Importa todos os novos modelos que definimos
import type {
  ManagerDashboardResponse,
  DriverDashboardResponse,
  VehiclePosition,
} from 'src/models/report-models';

// Definição do novo estado da store, mais completo
export interface DashboardState {
  managerDashboard: ManagerDashboardResponse | null;
  driverDashboard: DriverDashboardResponse | null;
  vehiclePositions: VehiclePosition[];
  isLoading: boolean;
}

export const useDashboardStore = defineStore('dashboard', {
  state: (): DashboardState => ({
    managerDashboard: null,
    driverDashboard: null,
    vehiclePositions: [],
    isLoading: false,
  }),

  actions: {
    /**
     * Busca os dados para o dashboard do GESTOR.
     * @param period A string do período para o filtro (ex: 'last_30_days')
     */
    async fetchManagerDashboard(period = 'last_30_days') {
      this.isLoading = true;
      try {
        const response = await api.get<ManagerDashboardResponse>('/dashboard/manager', {
          params: { period },
        });
        this.managerDashboard = response.data;
      } catch (error) {
        console.error('Falha ao buscar dados do dashboard do gestor:', error);
        // Opcional: adicionar notificação de erro para o usuário
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Busca os dados para o dashboard do MOTORISTA.
     */
    async fetchDriverDashboard() {
      this.isLoading = true;
      try {
        const response = await api.get<DriverDashboardResponse>('/dashboard/driver');
        this.driverDashboard = response.data;
      } catch (error) {
        console.error('Falha ao buscar dados do dashboard do motorista:', error);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Busca as posições dos veículos para o MAPA.
     * Esta ação é otimizada para ser chamada repetidamente (polling).
     */
    async fetchVehiclePositions() {
      // Não usamos 'isLoading' aqui para permitir uma atualização silenciosa em segundo plano.
      try {
        const response = await api.get<VehiclePosition[]>('/dashboard/vehicles/positions');
        this.vehiclePositions = response.data;
      } catch (error) {
        console.error('Falha ao buscar posições dos veículos:', error);
      }
    },

    /**
     * Limpa os dados do dashboard, útil ao fazer logout.
     */
    clearDashboardData() {
      this.managerDashboard = null;
      this.driverDashboard = null;
      this.vehiclePositions = [];
      this.isLoading = false;
    },
  },
});
