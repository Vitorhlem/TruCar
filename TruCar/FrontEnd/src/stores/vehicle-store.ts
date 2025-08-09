import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import { type Vehicle, VehicleStatus, type VehicleCreate, type VehicleUpdate } from 'src/models/vehicle-models';

export const useVehicleStore = defineStore('vehicle', () => {
  const vehicles = ref<Vehicle[]>([]);
  const isLoading = ref(false);

  
  const totalCount = computed(() => vehicles.value.length);
  const availableCount = computed(() => vehicles.value.filter(v => v.status === VehicleStatus.AVAILABLE).length);
  const inUseCount = computed(() => vehicles.value.filter(v => v.status === VehicleStatus.IN_USE).length);
  const maintenanceCount = computed(() => vehicles.value.filter(v => v.status === VehicleStatus.MAINTENANCE).length);
  const availableVehicles = computed(() => vehicles.value.filter(v => v.status === VehicleStatus.AVAILABLE));

  async function fetchAllVehicles() {
    isLoading.value = true;
    try {
      const response = await api.get<Vehicle[]>('/vehicles');
      vehicles.value = response.data;
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao carregar veículos.' });
      console.error('Falha ao buscar veículos:', error);
    } finally {
      isLoading.value = false;
    }
  }

  async function addNewVehicle(vehicleData: VehicleCreate) {
    isLoading.value = true;
    try {
      const response = await api.post<Vehicle>('/vehicles', vehicleData);
      vehicles.value.unshift(response.data);
      Notify.create({ type: 'positive', message: 'Veículo adicionado com sucesso!' });
    } catch (error: unknown) {
      console.error('Falha ao adicionar veículo:', error);
      let message = 'Erro ao criar veículo. Verifique os dados.';
      if (isAxiosError(error) && error.response?.data?.detail) {
        message = error.response.data.detail as string;
      }
      Notify.create({ type: 'negative', message: message });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  // --- NOVA ACTION PARA ATUALIZAR VEÍCULO ---
  async function updateVehicle(vehicleId: number, vehicleData: VehicleUpdate) {
    isLoading.value = true;
    try {
      const response = await api.put<Vehicle>(`/vehicles/${vehicleId}`, vehicleData);
      const index = vehicles.value.findIndex(v => v.id === vehicleId);
      if (index !== -1) {
        vehicles.value[index] = response.data;
      }
      Notify.create({ type: 'positive', message: 'Veículo atualizado com sucesso!' });
    } catch (error: unknown) {
      console.error('Falha ao atualizar veículo:', error);
      Notify.create({ type: 'negative', message: 'Erro ao atualizar veículo.' });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  // --- NOVA ACTION PARA DELETAR VEÍCULO ---
  async function deleteVehicle(vehicleId: number) {
    isLoading.value = true;
    try {
      await api.delete(`/vehicles/${vehicleId}`);
      vehicles.value = vehicles.value.filter(v => v.id !== vehicleId);
      Notify.create({ type: 'positive', message: 'Veículo excluído com sucesso!' });
    } catch (error: unknown) {
      console.error('Falha ao excluir veículo:', error);
      Notify.create({ type: 'negative', message: 'Erro ao excluir veículo.' });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    vehicles,
    isLoading,
    totalCount,
    availableCount,
    availableVehicles,
    inUseCount,
    maintenanceCount,
    fetchAllVehicles,
    addNewVehicle,
    updateVehicle, // <-- Expondo as novas actions
    deleteVehicle,   // <-- Expondo as novas actions
  };
});