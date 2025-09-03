import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { MaintenanceRequest, MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceComment, MaintenanceCommentCreate } from 'src/models/maintenance-models';

export const useMaintenanceStore = defineStore('maintenance', {
  state: () => ({
    requests: [] as MaintenanceRequest[],
    isLoading: false,
  }),

  actions: {
    async fetchRequests(search: string | null = null) {
      this.isLoading = true;
      try {
        const params = search ? { search } : {};
        const response = await api.get<MaintenanceRequest[]>('/maintenance', { params });
        this.requests = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar solicitações.' });
      } finally {
        this.isLoading = false;
      }
    },

    async fetchRequestById(requestId: number) {
      try {
        const response = await api.get<MaintenanceRequest>(`/maintenance/${requestId}`);
        const index = this.requests.findIndex(r => r.id === requestId);
        if (index !== -1) {
          this.requests[index] = response.data;
        }
      } catch (error) {
        console.error('Falha ao buscar detalhes do chamado:', error);
      }
    },

    async createRequest(payload: MaintenanceRequestCreate) {
      try {
        await api.post<MaintenanceRequest>('/maintenance/', payload);
        Notify.create({ type: 'positive', message: 'Solicitação enviada com sucesso!' });
        await this.fetchRequests();
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao enviar solicitação.' });
        throw error;
      }
    },

    async updateRequest(requestId: number, payload: MaintenanceRequestUpdate) {
      try {
        await api.put<MaintenanceRequest>(`/maintenance/${requestId}`, payload);
        Notify.create({ type: 'positive', message: 'Status da solicitação atualizado!' });
        await this.fetchRequests();
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao atualizar solicitação.' });
        throw error;
      }
    },

    async addComment(requestId: number, payload: MaintenanceCommentCreate) {
      try {
        await api.post<MaintenanceComment>(`/maintenance/${requestId}/comments`, payload);
        await this.fetchRequests();
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao enviar comentário.' });
        throw error;
      }
    },
  },
});