import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Fine, FineCreate, FineUpdate } from 'src/models/fine-models';

export const useFineStore = defineStore('fine', {
  state: () => ({
    fines: [] as Fine[],
    isLoading: false,
  }),
  actions: {
    async fetchFines() {
      this.isLoading = true;
      try {
        const response = await api.get<Fine[]>('/fines/');
        this.fines = response.data;
      } catch  {
        Notify.create({ type: 'negative', message: 'Falha ao carregar multas.' });
      } finally {
        this.isLoading = false;
      }
    },
    async createFine(payload: FineCreate): Promise<boolean> {
      this.isLoading = true;
      try {
        await api.post('/fines/', payload);
        Notify.create({ type: 'positive', message: 'Multa registrada com sucesso!' });
        await this.fetchFines();
        return true;
      } catch {
        Notify.create({ type: 'negative', message: 'Erro ao registrar multa.' });
        return false;
      } finally {
        this.isLoading = false;
      }
    },
      async updateFine(id: number, payload: FineUpdate): Promise<boolean> {
      this.isLoading = true;
      try {
        await api.put(`/fines/${id}`, payload);
        Notify.create({ type: 'positive', message: 'Multa atualizada com sucesso!' });
        await this.fetchFines();
        return true;
      } catch {
        Notify.create({ type: 'negative', message: 'Erro ao atualizar multa.' });
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteFine(id: number): Promise<boolean> {
      this.isLoading = true;
      try {
        await api.delete(`/fines/${id}`);
        Notify.create({ type: 'positive', message: 'Multa excluída com sucesso!' });

        const index = this.fines.findIndex(f => f.id === id);
        if (index > -1) {
          this.fines.splice(index, 1);
        }
        return true;
      } catch  {
        Notify.create({ type: 'negative', message: 'Erro ao excluir multa.' });
        return false;
      } finally {
        this.isLoading = false;
      }
    },
  },
});