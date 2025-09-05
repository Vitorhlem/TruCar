import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Journey, JourneyCreate, JourneyUpdate } from 'src/models/journey-models';
import type { Vehicle } from 'src/models/vehicle-models';
import { useAuthStore } from './auth-store';
import { useDashboardStore } from './dashboard-store';
import { useDemoStore } from './demo-store';

interface JourneyFilters {
  driver_id?: number | null;
  vehicle_id?: number | null;
  date_from?: string | null;
  date_to?: string | null;
}

// --- FUNÇÃO AUXILIAR PARA CORRIGIR O PROBLEMA ---
// Esta função encapsula a lógica de qual dashboard recarregar.
async function refreshDashboardData() {
  const dashboardStore = useDashboardStore();
  const authStore = useAuthStore();

  if (authStore.isManager) {
    // Para gestores, buscamos o dashboard de gestão.
    await dashboardStore.fetchManagerDashboard();
  } else if (authStore.isDriver) {
    // Para motoristas, buscamos o dashboard de motorista.
    await dashboardStore.fetchDriverDashboard();
  }
}


export const useJourneyStore = defineStore('journey', {
  state: () => ({
    journeys: [] as Journey[],
    isLoading: false,
  }),

  getters: {
    activeJourneys: (state) => state.journeys.filter((j) => j.is_active),

    currentUserActiveJourney(): Journey | null {
      const authStore = useAuthStore();
      if (!authStore.user) return null;
      return this.activeJourneys.find((j) => j.driver.id === authStore.user?.id) || null;
    },
  },

  actions: {
    async fetchAllJourneys(filters: JourneyFilters = {}) {
      this.isLoading = true;
      try {
        const cleanFilters: Record<string, string | number> = {};
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== null && value !== undefined) { cleanFilters[key] = value; }
        });
        const response = await api.get<Journey[]>('/journeys/', { params: cleanFilters });
        this.journeys = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao buscar histórico de operações.' });
      } finally {
        this.isLoading = false;
      }
    },

    async deleteJourney(journeyId: number) {
      this.isLoading = true;
      try {
        await api.delete(`/journeys/${journeyId}`);
        this.journeys = this.journeys.filter(j => j.id !== journeyId);
        Notify.create({ type: 'positive', message: 'Operação excluída com sucesso!' });

        await refreshDashboardData();

        const authStore = useAuthStore();
        if (authStore.isDemo) {
          await useDemoStore().fetchDemoStats(true);
        }
      } catch (error: unknown) {
        console.error('Falha ao excluir operação:', error);
        Notify.create({ type: 'negative', message: 'Erro ao excluir operação.' });
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async startJourney(journeyData: JourneyCreate): Promise<void> {
      this.isLoading = true;
      try {
        const response = await api.post<Journey>('/journeys/start', journeyData);
        this.journeys.unshift(response.data);
        await refreshDashboardData();

        const authStore = useAuthStore();
        if (authStore.isDemo) {
          await useDemoStore().fetchDemoStats(true);
        }
      } finally {
        this.isLoading = false;
      }
    },

    async endJourney(journeyId: number, journeyData: JourneyUpdate): Promise<Vehicle | null> {
      this.isLoading = true;
      try {
        const response = await api.put<{ journey: Journey, vehicle: Vehicle }>(
          `/journeys/${journeyId}/end`,
          journeyData
        );
        const index = this.journeys.findIndex(j => j.id === journeyId);
        if (index !== -1) {
          this.journeys[index] = response.data.journey;
        }
        await refreshDashboardData();
        return response.data.vehicle;
      } finally {
        this.isLoading = false;
      }
    },
  },
});

