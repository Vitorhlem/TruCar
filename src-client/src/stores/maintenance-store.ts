import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type {
  MaintenanceRequest,
  MaintenanceRequestCreate,
  MaintenanceRequestUpdate,
  MaintenanceComment,
  MaintenanceCommentCreate,
  ReplaceComponentPayload,
  ReplaceComponentResponse,
} from 'src/models/maintenance-models';
import { isAxiosError } from 'axios';

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

 await api.put<MaintenanceRequest>(`/maintenance/${requestId}/status`, payload);

Notify.create({ type: 'positive', message: 'Status da solicitação atualizado!' });
 await this.fetchMaintenanceRequests();
 } catch (error) {
Notify.create({ type: 'negative', message: 'Erro ao atualizar solicitação.' });
 throw error;
}
},

    async addComment(requestId: number, payload: MaintenanceCommentCreate): Promise<void> {
      try {
        await api.post<MaintenanceComment>(`/maintenance/${requestId}/comments`, payload);


        await this.fetchMaintenanceRequests();
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao enviar comentário.' });
        throw error;
      }
    },

    async revertPartChange(requestId: number, changeId: number): Promise<boolean> {
      this.isLoading = true;
      try {

        const newComment = await api.post<MaintenanceComment>(
          `/maintenance/part-changes/${changeId}/revert`
        );


        const requestToUpdate = this.maintenances.find(
          (r) => r.id === requestId
        );
        
        if (requestToUpdate) {

          const logToUpdate = requestToUpdate.part_changes.find(
            (log) => log.id === changeId
          );
          if (logToUpdate) {
            logToUpdate.is_reverted = true;
          }
          

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

        const response = await api.post<ReplaceComponentResponse>(
          `/maintenance/${requestId}/replace-component`,
          payload
        );



        const requestToUpdate = this.maintenances.find(
          (r) => r.id === requestId
        );


        if (requestToUpdate) {
          const { new_comment, part_change_log } = response.data;


          requestToUpdate.comments.push(new_comment);


          if (!requestToUpdate.part_changes) {
            requestToUpdate.part_changes = [];
          }
          requestToUpdate.part_changes.push(part_change_log);
          
        } else {

          await this.fetchMaintenanceRequests();
          await this.fetchRequestById(requestId);
        }


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

  },
});