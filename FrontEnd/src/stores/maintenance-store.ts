import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { MaintenanceRequest, MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceComment, MaintenanceCommentCreate } from 'src/models/maintenance-models';

export const useMaintenanceStore = defineStore('maintenance', () => {
  const requests = ref<MaintenanceRequest[]>([]);
  const isLoading = ref(false);

  /**
   * Busca a lista principal de solicitações do backend.
   * Esta é a nossa "fonte da verdade" para a tela de listagem.
   */
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

  /**
   * Busca os detalhes de UMA ÚNICA solicitação.
   * Útil para páginas de detalhes ou para atualizar um item sem recarregar a lista inteira.
   */
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

  /**
   * Cria uma nova solicitação e RECARREGA A LISTA COMPLETA.
   */
  async function createRequest(payload: MaintenanceRequestCreate) {
    try {
      await api.post<MaintenanceRequest>('/maintenance/', payload);
      Notify.create({ type: 'positive', message: 'Solicitação enviada com sucesso!' });
      // Após criar, busca a lista atualizada para refletir a adição.
      await fetchRequests();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao enviar solicitação.' });
      throw error;
    }
  }

  /**
   * Atualiza uma solicitação e RECARREGA A LISTA COMPLETA.
   */
  async function updateRequest(requestId: number, payload: MaintenanceRequestUpdate) {
    try {
      await api.put<MaintenanceRequest>(`/maintenance/${requestId}`, payload);
      Notify.create({ type: 'positive', message: 'Status da solicitação atualizado!' });

      // --- INÍCIO DA CORREÇÃO ---
      // Em vez de buscar apenas o item, recarregamos a lista inteira
      // para garantir que a ordenação e os dados estejam corretos na tela de listagem.
      await fetchRequests();
      // --- FIM DA CORREÇÃO ---

    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar solicitação.' });
      throw error;
    }
  }

  /**
   * Adiciona um comentário e RECARREGA A LISTA COMPLETA.
   */
  async function addComment(requestId: number, payload: MaintenanceCommentCreate) {
    try {
      await api.post<MaintenanceComment>(`/maintenance/${requestId}/comments`, payload);
      
      // --- INÍCIO DA CORREÇÃO ---
      // Também recarregamos a lista principal. Isso garante que se a lista for
      // ordenada por "última atividade", a solicitação comentada suba para o topo.
      await fetchRequests();
      // --- FIM DA CORREÇÃO ---

    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao enviar comentário.' });
      throw error;
    }
  }

  return {
    requests,
    isLoading,
    fetchRequests,
    fetchRequestById, // Mantemos a função caso seja útil em uma página de detalhes no futuro
    createRequest,
    updateRequest,
    addComment,
  };
});