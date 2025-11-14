import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { 
  MaintenanceRequest, MaintenanceRequestCreate, MaintenanceRequestUpdate, 
  MaintenanceComment, MaintenanceCommentCreate,
  ReplaceComponentPayload // <-- 1. IMPORTAR NOVO PAYLOAD
} from 'src/models/maintenance-models';
import { isAxiosError } from 'axios'; // <-- 2. IMPORTAR isAxiosError

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
        // --- CORREÇÃO AQUI ---
 await api.put<MaintenanceRequest>(`/maintenance/${requestId}/status`, payload);
        // --- FIM DA CORREÇÃO ---
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
    
    async replaceComponent(requestId: number, payload: ReplaceComponentPayload): Promise<boolean> {
      this.isLoading = true;
      try {
        // Usamos o novo endpoint
        await api.post(`/maintenance/${requestId}/replace-component`, payload);
        
        // Recarregar os dados é crucial
        // 1. Recarrega a lista principal (para pegar o novo comentário)
        await this.fetchMaintenanceRequests();
        // 2. Recarrega o chamado individual (caso a página de detalhes dependa disso)
        await this.fetchRequestById(requestId);

        return true;
      } catch (error) {
        const message = isAxiosError(error) 
          ? error.response?.data?.detail 
          : 'Erro ao substituir componente.';
        Notify.create({ type: 'negative', message: message as string });
        return false;
      } finally {
        this.isLoading = false;
      }
    },
    // --- FIM DA NOVA ACTION ---
  },
});