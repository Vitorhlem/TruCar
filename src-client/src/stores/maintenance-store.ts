import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type {
  MaintenanceRequest,
  MaintenanceRequestCreate,
  MaintenanceRequestUpdate,
  MaintenanceComment,
  MaintenanceCommentCreate,
  ReplaceComponentPayload, // <-- 1. Importa o payload atualizado
  ReplaceComponentResponse, // <-- 2. Importa a resposta atualizada
} from 'src/models/maintenance-models';
import { isAxiosError } from 'axios';
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
        // 1. Captura a resposta da API, que contém o comentário criado (com ID, Data, Usuário, etc.)
        const response = await api.post<MaintenanceComment>(`/maintenance/${requestId}/comments`, payload);
        
        // 2. Encontra o chamado específico na memória (state)
        const request = this.maintenances.find(r => r.id === requestId);
        
        // 3. Adiciona o novo comentário diretamente à lista de comentários desse chamado
        // Isso garante que o Vue detecte a mudança e atualize o chat na hora, sem precisar recarregar a página.
        if (request) {
           // Garante que o array existe
           if (!request.comments) {
             request.comments = [];
           }
           request.comments.push(response.data);
        }
        
        // Observação: Removemos o 'await this.fetchMaintenanceRequests()' pois ele substituía 
        // a lista inteira e podia quebrar a referência do objeto que o diálogo estava usando.

      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao enviar comentário.' });
        throw error;
      }
    },
    async revertPartChange(requestId: number, changeId: number): Promise<boolean> {
      this.isLoading = true;
      try {
        // 1. Chama o novo endpoint. A resposta é o novo comentário de log
        const newComment = await api.post<MaintenanceComment>(
          `/maintenance/part-changes/${changeId}/revert`
        );

        // 2. Atualiza o state local
        const requestToUpdate = this.maintenances.find(
          (r) => r.id === requestId
        );
        
        if (requestToUpdate) {
          // 3. Encontra o log da troca e marca como revertido
          const logToUpdate = requestToUpdate.part_changes.find(
            (log) => log.id === changeId
          );
          if (logToUpdate) {
            logToUpdate.is_reverted = true;
          }
          
          // 4. Adiciona o novo comentário de reversão ao chat
          requestToUpdate.comments.push(newComment.data);
        }

        Notify.create({
          type: 'positive',
          message: 'Troca revertida com sucesso! O item retornou ao estoque.',
        });
        return true;

      } catch (error) {
         const message = isAxiosError(error) 
          ? error.response?.data?.detail 
          : 'Erro ao reverter a troca.';
        Notify.create({ type: 'negative', message: message as string });
        return false;
      } finally {
        this.isLoading = false;
      }
    },
    
    async replaceComponent(
      requestId: number,
      payload: ReplaceComponentPayload
    ): Promise<boolean> {
      this.isLoading = true;
      try {
        // 1. Chama o endpoint com o novo payload
        const response = await api.post<ReplaceComponentResponse>(
          `/maintenance/${requestId}/replace-component`,
          payload
        );

        // --- CORREÇÃO AQUI: Usando .find() ---
        // 2. Acha o objeto do chamado DIRETAMENTE
        const requestToUpdate = this.maintenances.find(
          (r) => r.id === requestId
        );

        // 3. Verifica se o objeto existe ANTES de usá-lo
        if (requestToUpdate) {
          const { new_comment, part_change_log } = response.data;

          // Agora é seguro, pois 'requestToUpdate' é o objeto
          requestToUpdate.comments.push(new_comment);

          // Adiciona o novo log de troca ao histórico
          if (!requestToUpdate.part_changes) {
            requestToUpdate.part_changes = [];
          }
          requestToUpdate.part_changes.push(part_change_log);
          
        } else {
          // Fallback: se não achar o chamado no state, busca tudo de novo
          await this.fetchMaintenanceRequests();
          await this.fetchRequestById(requestId);
        }
        // --- FIM DA CORREÇÃO ---

        Notify.create({
          type: 'positive',
          message: 'Componente substituído com sucesso!',
        });
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