import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { MaintenanceRequest, MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceComment, MaintenanceCommentCreate } from 'src/models/maintenance-models';

export const useMaintenanceStore = defineStore('maintenance', () => {
  const requests = ref<MaintenanceRequest[]>([]);
  const comments = ref<MaintenanceComment[]>([]);
  const isLoading = ref(false);


    async function fetchRequests(search: string | null = null) {
    isLoading.value = true;
    try {
      const params = new URLSearchParams();
      if (search) {
        params.append('search', search);
      }
      const response = await api.get<MaintenanceRequest[]>('/maintenance/', { params });
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
      const response = await api.post<MaintenanceRequest>('/maintenance/', payload);
      requests.value.unshift(response.data);
      Notify.create({ type: 'positive', message: 'Solicitação enviada com sucesso!' });
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
      const response = await api.put<MaintenanceRequest>(`/maintenance/${requestId}`, payload);
      const index = requests.value.findIndex(r => r.id === requestId);
      if (index !== -1) {
        requests.value[index] = response.data;
      }
      Notify.create({ type: 'positive', message: 'Status da solicitação atualizado!' });
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar solicitação.' });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchComments(requestId: number) {
    try {
      const response = await api.get<MaintenanceComment[]>(`/maintenance/${requestId}/comments`);
      comments.value = response.data;
    } catch (error) {
      console.error('Falha ao buscar comentários', error);
      comments.value = []; // Limpa em caso de erro
    }
  }

    async function addComment(requestId: number, payload: MaintenanceCommentCreate) {
    try {
      const response = await api.post<MaintenanceComment>(`/maintenance/${requestId}/comments`, payload);
      comments.value.push(response.data); // Adiciona o novo comentário à lista local
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao enviar comentário.' });
      throw error;
    }
  }

  async function uploadAttachment(file: File): Promise<string | null> {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await api.post<{ file_url: string }>('/maintenance/upload-file', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
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
    createRequest,
    updateRequest,
    uploadAttachment,
    addComment,
    fetchComments,
  };
});