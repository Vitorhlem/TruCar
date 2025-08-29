// ARQUIVO: src/stores/vehicle-store.ts

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { VehicleStatus, type Vehicle, type VehicleCreate, type VehicleUpdate } from 'src/models/vehicle-models';

// Interface para os parâmetros da função de busca
interface FetchParams {
  page?: number;
  rowsPerPage?: number;
  search?: string;
}

// --- INÍCIO DA CORREÇÃO #1: Sincronizar a Interface com a API ---
// A interface agora espelha EXATAMENTE o que o backend retorna.
interface PaginatedVehiclesResponse {
  vehicles: Vehicle[];
  total_items: number;
}
// --- FIM DA CORREÇÃO #1 ---

export const useVehicleStore = defineStore('vehicle', () => {
  const vehicles = ref<Vehicle[]>([]);
  const isLoading = ref(false);
  const totalItems = ref(0);

  const availableVehicles = computed(() =>
    vehicles.value.filter(v => v.status === VehicleStatus.AVAILABLE)
  );

  async function fetchAllVehicles(params: FetchParams = {}) {
    isLoading.value = true;
    try {
      // --- INÍCIO DA CORREÇÃO #2: Sincronizar os Parâmetros com a API ---
      // Enviamos os parâmetros que o backend (FastAPI) espera.
      const queryParams = {
        page: params.page || 1,
        rowsPerPage: params.rowsPerPage || 8,
        search: params.search || '',
      };
      // --- FIM DA CORREÇÃO #2 ---

      const response = await api.get<PaginatedVehiclesResponse>('/vehicles/', { params: queryParams });

      // --- INÍCIO DA CORREÇÃO #3: Usar os Nomes de Chave Corretos ---
      // Usamos 'vehicles' e 'total_items' como o backend envia.
      vehicles.value = response.data.vehicles;
      totalItems.value = response.data.total_items;
      // --- FIM DA CORREÇÃO #3 ---

    } catch (error) {
      console.error('Falha ao buscar veículos:', error);
      Notify.create({ type: 'negative', message: 'Falha ao buscar veículos.' });
    } finally {
      isLoading.value = false;
    }
  }

  // --- FUNÇÕES DE CRUD ---

  async function addNewVehicle(vehicleData: VehicleCreate, initialFetchParams: FetchParams) {
    try {
      await api.post('/vehicles/', vehicleData);
      Notify.create({ type: 'positive', message: 'Item adicionado com sucesso!' });
      
      // --- INÍCIO DA CORREÇÃO #4: Recarregar a Lista ---
      // Após adicionar, sempre voltamos para a primeira página da busca atual.
      await fetchAllVehicles({ ...initialFetchParams, page: 1 });
      // --- FIM DA CORREÇÃO #4 ---
      
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao adicionar item.' });
      console.error('Erro ao adicionar:', error);
      throw error;
    }
  }

  async function updateVehicle(id: number, vehicleData: VehicleUpdate, currentFetchParams: FetchParams) {
    try {
      await api.put(`/vehicles/${id}`, vehicleData);
      Notify.create({ type: 'positive', message: 'Item atualizado com sucesso!' });
      // Recarrega a página atual para refletir a mudança
      await fetchAllVehicles(currentFetchParams);
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar item.' });
      console.error('Erro ao atualizar:', error);
      throw error;
    }
  }
  
  async function deleteVehicle(id: number, currentFetchParams: FetchParams) {
    try {
      await api.delete(`/vehicles/${id}`);
      Notify.create({ type: 'positive', message: 'Item excluído com sucesso.' });
      // Recarrega a página atual para refletir a remoção
      await fetchAllVehicles(currentFetchParams);
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao excluir o item.' });
      console.error('Erro ao excluir:', error);
    }
  }
  
  // Esta função não é mais necessária, pois o fetchAllVehicles já cuida da atualização.
  // function updateSingleVehicleInList(...) {}

  return {
    vehicles,
    isLoading,
    totalItems,
    availableVehicles,
    fetchAllVehicles,
    addNewVehicle,
    updateVehicle,
    deleteVehicle,
  };
});