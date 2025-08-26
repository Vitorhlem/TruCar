// src/stores/vehicle-store.ts

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { VehicleStatus, type Vehicle, type VehicleCreate, type VehicleUpdate } from 'src/models/vehicle-models';

interface FetchParams {
  page?: number;
  rowsPerPage?: number;
  search?: string;
}

interface PaginatedVehiclesResponse {
  total: number;
  items: Vehicle[];
}

export const useVehicleStore = defineStore('vehicle', () => {
  // ESTA LINHA É A MAIS IMPORTANTE DE TODAS
  // Ela garante que 'vehicles' começa como um array vazio, e nunca como 'undefined'.
  const vehicles = ref<Vehicle[]>([]);
  
  const isLoading = ref(false);
  const totalItems = ref(0);

  const availableVehicles = computed(() =>
    vehicles.value.filter(v => v.status === VehicleStatus.AVAILABLE)
  );

   async function fetchAllVehicles(params: FetchParams = {}) {
    isLoading.value = true;
    try {
      // Usamos um limite alto para garantir que todos os veículos sejam carregados para os seletores
      const queryParams = {
        skip: params.page ? (params.page - 1) * (params.rowsPerPage || 100) : 0,
        limit: params.rowsPerPage || 100,
        search: params.search || '',
      };

      const response = await api.get<PaginatedVehiclesResponse>('/vehicles/', { params: queryParams });
      vehicles.value = response.data.items;
      totalItems.value = response.data.total;
    } catch (error) {
      console.error('Falha ao buscar veículos:', error);
      Notify.create({ type: 'negative', message: 'Falha ao buscar veículos.' });
    } finally {
      isLoading.value = false;
    }
  }

  function updateSingleVehicleInList(updatedVehicle: Vehicle) {
    const index = vehicles.value.findIndex(v => v.id === updatedVehicle.id);
    if (index !== -1) {
      vehicles.value[index] = updatedVehicle;
    }
  }

  // --- FUNÇÕES DE CRUD IMPLEMENTADAS ---

  async function addNewVehicle(vehicleData: VehicleCreate) {
    try {
      await api.post('/vehicles/', vehicleData);
      Notify.create({ type: 'positive', message: 'Item adicionado com sucesso!' });
      await fetchAllVehicles(); // Atualiza a lista
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao adicionar item.' });
      console.error('Erro ao adicionar:', error);
      throw error; // Propaga o erro para o componente saber que falhou
    }
  }

  async function updateVehicle(id: number, vehicleData: VehicleUpdate) {
    try {
      await api.put(`/vehicles/${id}`, vehicleData);
      Notify.create({ type: 'positive', message: 'Item atualizado com sucesso!' });
      await fetchAllVehicles(); // Atualiza a lista
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
      await fetchAllVehicles(currentFetchParams); // Recarrega a página atual
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao excluir o item.' });
      console.error('Erro ao excluir:', error);
    }
  }

  return {
    vehicles,
    isLoading,
    totalItems,
    availableVehicles,
    fetchAllVehicles,
    updateSingleVehicleInList,
    addNewVehicle,
    updateVehicle,
    deleteVehicle,
  };
});