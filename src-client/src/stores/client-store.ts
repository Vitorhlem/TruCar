import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Client, ClientCreate, ClientUpdate } from 'src/models/client-models';

export const useClientStore = defineStore('client', {
  // 1. As variáveis ('refs') agora vivem dentro do 'state'
  state: () => ({
    clients: [] as Client[],
    isLoading: false,
  }),

  // 2. As funções agora vivem dentro de 'actions'
  actions: {
    async fetchAllClients() {
      this.isLoading = true; // 3. Usamos 'this' em vez de '.value'
      try {
        const response = await api.get<Client[]>('/clients/');
        this.clients = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao buscar clientes.' });
      } finally {
        this.isLoading = false;
      }
    },

    async addClient(payload: ClientCreate) {
      try {
        await api.post('/clients/', payload);
        Notify.create({ type: 'positive', message: 'Cliente adicionado com sucesso!' });
        await this.fetchAllClients(); // 3. Usamos 'this' para chamar outra action
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao adicionar cliente.' });
        throw error;
      }
    },
    async updateClient(id: number, payload: ClientUpdate) {
      this.isLoading = true;
      try {
        await api.put(`/clients/${id}`, payload);
        Notify.create({ type: 'positive', message: 'Cliente atualizado com sucesso!' });
        await this.fetchAllClients();
      } catch (error) {
        console.error(error);
        Notify.create({ type: 'negative', message: 'Erro ao atualizar cliente.' });
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteClient(id: number) {
      this.isLoading = true;
      try {
        await api.delete(`/clients/${id}`);
        Notify.create({ type: 'positive', message: 'Cliente excluído com sucesso!' });
        // Remove localmente para agilizar a UI
        this.clients = this.clients.filter(c => c.id !== id);
      } catch (error) {
        console.error(error);
        Notify.create({ type: 'negative', message: 'Erro ao excluir cliente.' });
        throw error;
      } finally {
        this.isLoading = false;
      }
    }
  },
});