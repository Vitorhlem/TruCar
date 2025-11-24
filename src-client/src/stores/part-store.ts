import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import type { Part, PartCreate } from 'src/models/part-models';
import type { InventoryTransaction } from 'src/models/inventory-transaction-models';
// --- 1. IMPORTAR O NOVO MODELO ---
import type { 
  InventoryItem, 
  InventoryItemDetails, 
  InventoryItemPage, // <-- Adicionado
  InventoryItemRow  // <-- Adicionado
} from 'src/models/inventory-item-models';
import { InventoryItemStatus } from 'src/models/inventory-item-models';


export interface PartCreatePayload extends PartCreate {
  photo_file?: File | null;
  invoice_file?: File | null;
}

export const usePartStore = defineStore('part', {
  state: () => ({
    parts: [] as Part[],
    selectedPartHistory: [] as InventoryTransaction[],
    availableItems: [] as InventoryItem[], 
    
    // --- 2. NOVO STATE PARA A PÁGINA ---
    selectedItemDetails: null as InventoryItemDetails | null,
    isItemDetailsLoading: false,
    // --- FIM DO NOVO STATE ---
    
    masterItemList: [] as InventoryItemRow[],
    isMasterListLoading: false,
    masterListTotal: 0,

    isLoading: false,
    isHistoryLoading: false,
    isItemsLoading: false,
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


    async fetchMasterItems(options: { 
      page: number, 
      rowsPerPage: number, 
      status?: InventoryItemStatus | null,
      partId?: number | null,
      vehicleId?: number | null,
      search?: string | null 
    }) {
      this.isMasterListLoading = true;
      try {
        const params = {
          skip: (options.page - 1) * options.rowsPerPage,
          limit: options.rowsPerPage,
          status: options.status || undefined,
          part_id: options.partId || undefined,
          vehicle_id: options.vehicleId || undefined,
          search: options.search || undefined,
        };
    
        const response = await api.get<InventoryItemPage>('/parts/inventory/items/', { params });
        
        this.masterItemList = response.data.items;
        this.masterListTotal = response.data.total;
        
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Falha ao carregar itens de inventário.' });
        console.error(error);
      } finally {
        this.isMasterListLoading = false;
      }
    },

    async createPart(payload: PartCreatePayload): Promise<boolean> {
      this.isLoading = true;
      try {
          const formData = new FormData();
          Object.entries(payload).forEach(([key, value]) => {
              if (key !== 'photo_file' && key !== 'invoice_file' && key !== 'stock' && value !== null && value !== undefined) {
                  formData.append(key, String(value));
              }
          });
          
          // --- CORREÇÃO: Anexar os arquivos ao FormData ---
          if (payload.photo_file) {
              formData.append('file', payload.photo_file);
          }
          if (payload.invoice_file) {
              formData.append('invoice_file', payload.invoice_file);
          }
          // ------------------------------------------------
          
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
              if (key !== 'photo_file' && key !== 'invoice_file' && key !== 'stock' && value !== null && value !== undefined) {
                  formData.append(key, String(value));
              }
          });
          if (payload.photo_file) {
              formData.append('file', payload.photo_file);
          }
          if (payload.invoice_file) {
              formData.append('invoice_file', payload.invoice_file);
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
      } catch (error) {
        // --- CORREÇÃO AQUI ---
        // Capturamos a mensagem específica do 409 enviada pelo backend
        const message = isAxiosError(error) && error.response?.data?.detail 
          ? error.response.data.detail 
          : 'Erro ao remover a peça.';
          
        Notify.create({ 
          type: 'negative', 
          message: message as string,
          timeout: 5000 // Tempo maior para ler a mensagem longa
        });
      } finally {
        this.isLoading = false;
      }
    },

    async addItems(partId: number, quantity: number, notes?: string): Promise<boolean> {
      this.isLoading = true;
      try {
        const payload = { quantity, notes };
        await api.post(`/parts/${partId}/add-items`, payload);
        
        // Recarregar a lista do zero
        await this.fetchParts();

        Notify.create({ type: 'positive', message: `${quantity} itens adicionados com sucesso!` });
        return true;
      } catch (error) {
        const message = isAxiosError(error) ? error.response?.data?.detail : 'Erro ao adicionar itens.';
        Notify.create({ type: 'negative', message: message as string });
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async setItemStatus(partId: number, itemId: number, newStatus: InventoryItemStatus, vehicleId?: number, notes?: string): Promise<boolean> {
      this.isLoading = true;
      try {
        const payload = { new_status: newStatus, related_vehicle_id: vehicleId, notes };
        await api.put(`/parts/items/${itemId}/set-status`, payload);
        
        Notify.create({ type: 'positive', message: 'Status do item atualizado com sucesso!' });
        return true;
      } catch (error) {
        const message = isAxiosError(error) ? error.response?.data?.detail : 'Erro ao mudar status do item.';
        Notify.create({ type: 'negative', message: message as string });
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // --- 3. NOVA ACTION PARA BUSCAR OS DETALHES ---
    async fetchItemDetails(itemId: number) {
      this.isItemDetailsLoading = true;
      this.selectedItemDetails = null;
      try {
        // Usamos o novo endpoint e o novo modelo
        const response = await api.get<InventoryItemDetails>(`/parts/items/${itemId}`);
        this.selectedItemDetails = response.data;
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Falha ao carregar os detalhes do item.' });
        console.error(error);
      } finally {
        this.isItemDetailsLoading = false;
      }
    },
    // --- FIM DA NOVA ACTION ---

    async fetchAvailableItems(partId: number) {
      this.isItemsLoading = true;
      this.availableItems = [];
      try {
        const response = await api.get<InventoryItem[]>(`/parts/${partId}/items`, {
          params: { 
            // Substitua a string hardcoded pelo Enum
            status: InventoryItemStatus.DISPONIVEL 
          }
        });
        this.availableItems = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar itens disponíveis.' });
      } finally {
        this.isItemsLoading = false;
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
