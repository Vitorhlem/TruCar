import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Journey, JourneyCreate, JourneyUpdate } from 'src/models/journey-models';
import { type Vehicle } from 'src/models/vehicle-models'; // <-- ADICIONE ESTE IMPORT
import { useAuthStore } from './auth-store';
import { useDashboardStore } from './dashboard-store';


export const useJourneyStore = defineStore('journey', () => {
  const journeys = ref<Journey[]>([]);
  const isLoading = ref(false);

  const activeJourneys = computed(() => journeys.value.filter((j) => j.is_active));

  const currentUserActiveJourney = computed(() => {
    const authStore = useAuthStore();
    if (!authStore.user) return null;
    return activeJourneys.value.find((j) => j.driver.id === authStore.user?.id);
  });

  async function fetchAllJourneys(filters: {
    driver_id?: number | null,
    vehicle_id?: number | null,
    date_from?: string | null,
    date_to?: string | null
  } = {}) {
    isLoading.value = true;
    try {
      const params = new URLSearchParams();
      if (filters.driver_id) params.append('driver_id', String(filters.driver_id));
      if (filters.vehicle_id) params.append('vehicle_id', String(filters.vehicle_id));
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      
      const response = await api.get<Journey[]>('/journeys/', { params });
      journeys.value = response.data;
    } catch {
      Notify.create({ type: 'negative', message: 'Falha ao buscar histórico de viagens.' });
    } finally {
      isLoading.value = false;
    }
  }

 async function startJourney(journeyData: JourneyCreate) {
    isLoading.value = true;
    try {
      const response = await api.post<Journey>('/journeys/start', journeyData);
      journeys.value.unshift(response.data);
      // ATUALIZAÇÃO EM TEMPO REAL
      const dashboardStore = useDashboardStore();
      await dashboardStore.fetchSummary();
      // NÃO HÁ NOTIFICAÇÃO AQUI
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
      // ATUALIZAÇÃO EM TEMPO REAL
      const dashboardStore = useDashboardStore();
      await dashboardStore.fetchSummary();
      return response.data.vehicle;
    } finally {
      isLoading.value = false;
    }
  }
  
  async function deleteJourney(journeyId: number) {
    isLoading.value = true;
    try {
      await api.delete(`/journeys/${journeyId}`);
      journeys.value = journeys.value.filter(j => j.id !== journeyId);
      Notify.create({ type: 'positive', message: 'Viagem excluída com sucesso!' });
    } catch (error: unknown) {
      console.error('Falha ao excluir viagem:', error);
      Notify.create({ type: 'negative', message: 'Erro ao excluir viagem.' });
      throw error;
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
    // fetchActiveJourneys foi removido para evitar duplicidade,
    // o Dashboard também usará fetchAllJourneys e o getter activeJourneys
    startJourney,
    endJourney,
    deleteJourney,
  };
});