import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Journey, JourneyCreate, JourneyUpdate } from 'src/models/journey-models';
import type { Vehicle } from 'src/models/vehicle-models';
import { useAuthStore } from './auth-store';
import { useDashboardStore } from './dashboard-store';

interface JourneyFilters {
  driver_id?: number | null;
  vehicle_id?: number | null;
  date_from?: string | null;
  date_to?: string | null;
}

export const useJourneyStore = defineStore('journey', () => {
  const journeys = ref<Journey[]>([]);
  const isLoading = ref(false);
  const authStore = useAuthStore();

  const activeJourneys = computed(() => journeys.value.filter((j) => j.is_active));
  
  const currentUserActiveJourney = computed(() => {
    if (!authStore.user) return null;
    return activeJourneys.value.find((j) => j.driver.id === authStore.user?.id);
  });

  async function fetchAllJourneys(filters: JourneyFilters = {}) {
    isLoading.value = true;
    try {
      const cleanFilters: Record<string, string | number> = {};
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined) { cleanFilters[key] = value; }
      });
      const response = await api.get<Journey[]>('/journeys/', { params: cleanFilters });
      journeys.value = response.data;
    } catch {
      Notify.create({ type: 'negative', message: 'Falha ao buscar histórico de operações.' });
    } finally {
      isLoading.value = false;
    }
  }

   async function deleteJourney(journeyId: number) {
    isLoading.value = true;
    try {
      await api.delete(`/journeys/${journeyId}`);
      // Remove a viagem da lista local para atualização instantânea
      journeys.value = journeys.value.filter(j => j.id !== journeyId);
      Notify.create({ type: 'positive', message: 'Operação excluída com sucesso!' });

      // Atualiza a dashboard em tempo real
      const dashboardStore = useDashboardStore();
      await dashboardStore.fetchSummary();

    } catch (error: unknown) {
      console.error('Falha ao excluir operação:', error);
      Notify.create({ type: 'negative', message: 'Erro ao excluir operação.' });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function startJourney(journeyData: JourneyCreate): Promise<void> {
    isLoading.value = true;
    try {
      const response = await api.post<Journey>('/journeys/start', journeyData);
      journeys.value.unshift(response.data);
      const dashboardStore = useDashboardStore();
      await dashboardStore.fetchSummary();
    } finally {
      isLoading.value = false;
    }
  }

  async function endJourney(journeyId: number, journeyData: JourneyUpdate): Promise<Vehicle | null> {
    isLoading.value = true;
    try {
      const response = await api.put<{ journey: Journey, vehicle: Vehicle }>(
        `/journeys/${journeyId}/end`,
        journeyData
      );
      const index = journeys.value.findIndex(j => j.id === journeyId);
      if (index !== -1) {
        journeys.value[index] = response.data.journey;
      }
      const dashboardStore = useDashboardStore();
      await dashboardStore.fetchSummary();
      return response.data.vehicle;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    journeys,
    isLoading,
    activeJourneys,
    currentUserActiveJourney,
    fetchAllJourneys,
    startJourney,
    deleteJourney,
    endJourney,
  };
});