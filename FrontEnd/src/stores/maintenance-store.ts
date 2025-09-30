import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { MaintenanceRequest, MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceComment, MaintenanceCommentCreate } from 'src/models/maintenance-models';

// Interface para os parâmetros de busca
interface FetchMaintenanceParams {
  search?: string | null;
  vehicleId?: number;
  limit?: number;
}

export const useMaintenanceStore = defineStore('maintenance', {
  state: () => ({
    maintenances: [] as MaintenanceRequest[],
    isLoading: false,
  }),
  actions: {
    // ... (fetchMaintenanceRequests, fetchRequestById, createRequest, updateRequest permanecem iguais) ...
    async fetchMaintenanceRequests(params: FetchMaintenanceParams = {}) {
      this.isLoading = true;
      try {
        const response = await api.get<MaintenanceRequest[]>('/maintenance/', { params });
        this.maintenances = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar manutenções.' });
      } finally {
        this.isLoading = false;
      }
    },

    async fetchRequestById(requestId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<MaintenanceRequest>(`/maintenance/${requestId}`);
        const index = this.maintenances.findIndex(r => r.id === requestId);
        if (index !== -1) {
          this.maintenances[index] = response.data;
        }
      } catch (error) {
        console.error('Falha ao buscar detalhes do chamado:', error);
      } finally {
        this.isLoading = false;
      }
    },

    async createRequest(payload: MaintenanceRequestCreate): Promise<boolean> {
      try {
        await api.post<MaintenanceRequest>('/maintenance/', payload);
        Notify.create({ type: 'positive', message: 'Solicitação enviada com sucesso!' });
        await this.fetchMaintenanceRequests();
        return true;
      } catch {
        Notify.create({ type: 'negative', message: 'Erro ao enviar solicitação.' });
        return false;
      }
    },

    async updateRequest(requestId: number, payload: MaintenanceRequestUpdate): Promise<void> {
      try {
        await api.put<MaintenanceRequest>(`/maintenance/${requestId}`, payload);
        Notify.create({ type: 'positive', message: 'Status da solicitação atualizado!' });
        await this.fetchMaintenanceRequests();
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao atualizar solicitação.' });
        throw error;
      }
    },
    
    // --- FUNÇÃO CORRIGIDA ---
    async addComment(requestId: number, payload: MaintenanceCommentCreate): Promise<void> {
      try {
        await api.post<MaintenanceComment>(`/maintenance/${requestId}/comments`, payload);
        // Em vez de buscar apenas um, buscamos a lista inteira.
        // Isto força a reatividade em todos os componentes que dependem da lista.
        await this.fetchMaintenanceRequests();
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao enviar comentário.' });
        throw error;
      }
    },
  },
});