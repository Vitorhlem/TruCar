import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { MaintenanceRequest, MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceComment, MaintenanceCommentCreate } from 'src/models/maintenance-models';

// Interface para os parâmetros de busca (estava em falta)
interface FetchMaintenanceParams {
  search?: string | null;
  vehicleId?: number;
  limit?: number;
}

export const useMaintenanceStore = defineStore('maintenance', {
  state: () => ({
    maintenances: [] as MaintenanceRequest[], // Nome correto
    isLoading: false,
  }),
  actions: {
    async fetchMaintenanceRequests(params: FetchMaintenanceParams = {}) { // Nome correto
      this.isLoading = true;
      try {
        const response = await api.get<MaintenanceRequest[]>('/maintenance/', { params });
        this.maintenances = response.data; // Nome correto
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
        // CORRIGIDO para .maintenances
        const index = this.maintenances.findIndex(r => r.id === requestId);
        if (index !== -1) {
          // CORRIGIDO para .maintenances
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
        await this.fetchMaintenanceRequests(); // CORRIGIDO para a nova função
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
        await this.fetchMaintenanceRequests(); // CORRIGIDO para a nova função
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao atualizar solicitação.' });
        throw error;
      }
    },
    
    async addComment(requestId: number, payload: MaintenanceCommentCreate): Promise<void> {
      try {
        await api.post<MaintenanceComment>(`/maintenance/${requestId}/comments`, payload);
        await this.fetchRequestById(requestId);
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao enviar comentário.' });
        throw error;
      }
    },
  },
});