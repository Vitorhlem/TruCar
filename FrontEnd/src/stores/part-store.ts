import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import type { Part } from 'src/models/part-models';
// NOVOS IMPORTS
import type { InventoryTransaction, TransactionCreate } from 'src/models/inventory-transaction-models';

export interface PartCreatePayload extends Partial<Part> {
  photo_file?: File | null;
}

export const usePartStore = defineStore('part', {
  state: () => ({
    parts: [] as Part[],
    // NOVO: Estado para o histórico da peça selecionada
    selectedPartHistory: [] as InventoryTransaction[],
    isLoading: false,
    isHistoryLoading: false, // NOVO: Loading específico para o histórico
  }),

  actions: {
    async fetchParts(searchQuery: string | null = null) {
      this.isLoading = true;
      try {
        const params = searchQuery ? { search: searchQuery } : {};
        const response = await api.get<Part[]>('/parts/', { params });
        this.parts = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar as peças do inventário.' });
      } finally {
        this.isLoading = false;
      }
    },

    async createPart(payload: PartCreatePayload): Promise<boolean> {
        this.isLoading = true;
        try {
            const formData = new FormData();
            Object.entries(payload).forEach(([key, value]) => {
                if (key !== 'photo_file' && value !== null && value !== undefined) {
                    formData.append(key, String(value));
                }
            });
            if (payload.photo_file) {
                formData.append('file', payload.photo_file);
            }
            await api.post('/parts/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            Notify.create({ type: 'positive', message: 'Peça adicionada com sucesso!' });
            await this.fetchParts();
            return true;
        } catch (error) {
            const message = isAxiosError(error) ? error.response?.data?.detail : 'Erro ao adicionar peça.';
            Notify.create({ type: 'negative', message: message as string });
            return false;
        } finally {
            this.isLoading = false;
        }
    },

    async updatePart(id: number, payload: PartCreatePayload): Promise<boolean> {
        this.isLoading = true;
        try {
            const formData = new FormData();
            Object.entries(payload).forEach(([key, value]) => {
                if (key !== 'photo_file' && value !== null && value !== undefined) {
                    formData.append(key, String(value));
                }
            });
            if (payload.photo_file) {
                formData.append('file', payload.photo_file);
            }
            await api.put(`/parts/${id}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            Notify.create({ type: 'positive', message: 'Peça atualizada com sucesso!' });
            await this.fetchParts();
            return true;
        } catch (error) {
            const message = isAxiosError(error) ? error.response?.data?.detail : 'Erro ao atualizar peça.';
            Notify.create({ type: 'negative', message: message as string });
            return false;
        } finally {
            this.isLoading = false;
        }
    },

    async deletePart(id: number) {
      this.isLoading = true;
      try {
        await api.delete(`/parts/${id}`);
        Notify.create({ type: 'positive', message: 'Peça removida com sucesso.' });
        await this.fetchParts();
      } catch {
        Notify.create({ type: 'negative', message: 'Erro ao remover a peça.' });
      } finally {
        this.isLoading = false;
      }
    },

    // --- NOVAS AÇÕES ---
    async addTransaction(partId: number, payload: TransactionCreate): Promise<boolean> {
      this.isLoading = true;
      try {
        await api.post(`/parts/${partId}/transaction`, payload);
        Notify.create({ type: 'positive', message: 'Movimentação de estoque registrada com sucesso!' });
        // Atualiza a lista principal para refletir o novo estoque
        await this.fetchParts();
        return true;
      } catch (error) {
        const message = isAxiosError(error) ? error.response?.data?.detail : 'Erro ao registrar movimentação.';
        Notify.create({ type: 'negative', message: message as string });
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchHistory(partId: number) {
      this.isHistoryLoading = true;
      this.selectedPartHistory = [];
      try {
        const response = await api.get<InventoryTransaction[]>(`/parts/${partId}/history`);
        this.selectedPartHistory = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar o histórico do item.' });
      } finally {
        this.isHistoryLoading = false;
      }
    },
  },
});