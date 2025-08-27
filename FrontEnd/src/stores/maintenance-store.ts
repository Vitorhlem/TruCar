import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { MaintenanceRequest, MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceComment, MaintenanceCommentCreate } from 'src/models/maintenance-models';

export const useMaintenanceStore = defineStore('maintenance', () => {
  const requests = ref<MaintenanceRequest[]>([]);
  const comments = ref<MaintenanceComment[]>([]); // Pode ser útil para um chamado específico
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
    isLoading.value = true;
    try {
      await api.post<MaintenanceRequest>('/maintenance/', payload);
      Notify.create({ type: 'positive', message: 'Solicitação enviada com sucesso!' });
      await fetchRequests(); // Recarrega a lista para mostrar o novo item
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao enviar solicitação.' });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateRequest(requestId: number, payload: MaintenanceRequestUpdate) {
    isLoading.value = true;
    try {
      await api.put<MaintenanceRequest>(`/maintenance/${requestId}`, payload);
      Notify.create({ type: 'positive', message: 'Status da solicitação atualizado!' });
      // Busca a versão completa para ter todos os dados atualizados
      await fetchRequestById(requestId);
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar solicitação.' });
      throw error;
    } finally {
      isLoading.value = false;
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
      // Após adicionar um comentário, busca o chamado completo para atualizar a lista de comentários
      await fetchRequestById(requestId);
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao enviar comentário.' });
      throw error;
    }
  }

  async function uploadAttachment(file: File): Promise<string | null> {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await api.post<{ file_url: string }>('/maintenance/upload-file', formData);
      return response.data.file_url;
    } catch {
      Notify.create({ type: 'negative', message: 'Falha no upload do anexo.' });
      return null;
    }
  }

  return {
    requests,
    comments,
    isLoading,
    fetchRequests,
    fetchRequestById,
    createRequest,
    updateRequest,
    uploadAttachment,
    addComment,
  };
});