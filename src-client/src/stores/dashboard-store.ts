import { defineStore } from 'pinia';
import { api } from 'boot/axios';

import type {
  ManagerDashboardResponse,
  DriverDashboardResponse,
  VehiclePosition,
} from 'src/models/report-models';


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

    async fetchManagerDashboard(period = 'last_30_days') {
      this.isLoading = true;
      try {
        const response = await api.get<ManagerDashboardResponse>('/dashboard/manager', {
          params: { period },
        });
        this.managerDashboard = response.data;
      } catch (error) {
        console.error('Falha ao buscar dados do dashboard do gestor:', error);

      } finally {
        this.isLoading = false;
      }
    },


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


    async fetchVehiclePositions() {

      try {
        const response = await api.get<VehiclePosition[]>('/dashboard/vehicles/positions');
        this.vehiclePositions = response.data;
      } catch (error) {
        console.error('Falha ao buscar posições dos veículos:', error);
      }
    },


    clearDashboardData() {
      this.managerDashboard = null;
      this.driverDashboard = null;
      this.vehiclePositions = [];
      this.isLoading = false;
    },
  },
});
