import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { VehicleStatus, type Vehicle, type VehicleCreate, type VehicleUpdate } from 'src/models/vehicle-models';
import { useDemoStore } from './demo-store'; // <-- 1. IMPORTAMOS A DEMO STORE
import { useAuthStore } from './auth-store'; // <-- 2. IMPORTAMOS A AUTH STORE

interface FetchParams {
  page?: number;
  rowsPerPage?: number;
  search?: string;
}

interface PaginatedVehiclesResponse {
  vehicles: Vehicle[];
  total_items: number;
}

const initialState = () => ({
  vehicles: [] as Vehicle[],
  isLoading: false,
  totalItems: 0,
});

export const useVehicleStore = defineStore('vehicle', {
  state: initialState,

  getters: {
    availableVehicles: (state) =>
      state.vehicles.filter(v => v.status === VehicleStatus.AVAILABLE),
  },

  actions: {
    async fetchAllVehicles(params: FetchParams = {}) {
      this.isLoading = true;
      try {
        const queryParams = {
          page: params.page || 1,
          rowsPerPage: params.rowsPerPage || 8,
          search: params.search || '',
        };
        const response = await api.get<PaginatedVehiclesResponse>('/vehicles/', { params: queryParams });
        this.vehicles = response.data.vehicles;
        this.totalItems = response.data.total_items;
      } catch (error) {
        console.error('Falha ao buscar veículos:', error);
        Notify.create({ type: 'negative', message: 'Falha ao buscar veículos.' });
      } finally {
        this.isLoading = false;
      }
    },

    async addNewVehicle(vehicleData: VehicleCreate, initialFetchParams: FetchParams) {
      try {
        await api.post('/vehicles/', vehicleData);
        Notify.create({ type: 'positive', message: 'Item adicionado com sucesso!' });
        await this.fetchAllVehicles({ ...initialFetchParams, page: 1 });

        // --- LÓGICA DE ATUALIZAÇÃO ADICIONADA ---
        const authStore = useAuthStore();
        if (authStore.isDemo) {
          const demoStore = useDemoStore();
          await demoStore.fetchDemoStats(true); // O 'true' força a atualização
        }
        // --- FIM DA ADIÇÃO ---

      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao adicionar item.' });
        console.error('Erro ao adicionar:', error);
        throw error;  
      }
    },

    async updateVehicle(id: number, vehicleData: VehicleUpdate, currentFetchParams: FetchParams) {
      try {
        await api.put(`/vehicles/${id}`, vehicleData);
        Notify.create({ type: 'positive', message: 'Item atualizado com sucesso!' });
        await this.fetchAllVehicles(currentFetchParams);
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao atualizar item.' });
        console.error('Erro ao atualizar:', error);
        throw error;
      }
    },
    
    async deleteVehicle(id: number, currentFetchParams: FetchParams) {
      try {
        await api.delete(`/vehicles/${id}`);
        Notify.create({ type: 'positive', message: 'Item excluído com sucesso.' });
        await this.fetchAllVehicles(currentFetchParams);

        // --- LÓGICA DE ATUALIZAÇÃO ADICIONADA ---
        const authStore = useAuthStore();
        if (authStore.isDemo) {
          const demoStore = useDemoStore();
          await demoStore.fetchDemoStats(true); // O 'true' força a atualização
        }
        // --- FIM DA ADIÇÃO ---

      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao excluir o item.' });
        console.error('Erro ao excluir:', error);
      }
    },
  },
});
