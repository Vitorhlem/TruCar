import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { MaintenanceRequest, MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceComment, MaintenanceCommentCreate } from 'src/models/maintenance-models';

export const useMaintenanceStore = defineStore('maintenance', () => {
  const requests = ref<MaintenanceRequest[]>([]);
  const isLoading = ref(false);

  async function fetchRequests(search: string | null = null) {
    isLoading.value = true;
    try {
      const params = search ? { search } : {};
      const response = await api.get<MaintenanceRequest[]>('/maintenance', { params });
      requests.value = response.data;
    } catch {
      Notify.create({ type: 'negative', message: 'Falha ao carregar solicitações.' });
    } finally {
      isLoading.value = false;
    }
  }
  
  async function createRequest(payload: MaintenanceRequestCreate) {
    try {
      await api.post<MaintenanceRequest>('/maintenance/', payload);
      Notify.create({ type: 'positive', message: 'Solicitação enviada com sucesso!' });
      await fetchRequests();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao enviar solicitação.' });
      throw error;
    }
  }

  async function updateRequest(requestId: number, payload: MaintenanceRequestUpdate) {
    try {
      await api.put<MaintenanceRequest>(`/maintenance/${requestId}`, payload);
      Notify.create({ type: 'positive', message: 'Status da solicitação atualizado!' });
      await fetchRequestById(requestId);
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar solicitação.' });
      throw error;
    }
  }

  async function fetchRequestById(requestId: number) {
    try {
        const response = await api.get<MaintenanceRequest>(`/maintenance/${requestId}`);
        const index = requests.value.findIndex(r => r.id === requestId);
        if (index !== -1) {
            requests.value[index] = response.data;
        }
    } catch (error) {
        console.error('Falha ao buscar detalhes do chamado:', error);
    }
  }

  async function addComment(requestId: number, payload: MaintenanceCommentCreate) {
    try {
      await api.post<MaintenanceComment>(`/maintenance/${requestId}/comments`, payload);
      // A CORREÇÃO CRUCIAL: Após adicionar, busca o chamado completo novamente.
      await fetchRequestById(requestId);
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao enviar comentário.' });
      throw error;
    }
  }

  return {
    requests,
    isLoading,
    fetchRequests,
    fetchRequestById,
    createRequest,
    updateRequest,
    addComment,
  };
});