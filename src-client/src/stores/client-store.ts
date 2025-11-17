import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Client, ClientCreate } from 'src/models/client-models';

export const useClientStore = defineStore('client', {

  state: () => ({
    clients: [] as Client[],
    isLoading: false,
  }),


  actions: {
    async fetchAllClients() {
      this.isLoading = true;
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
        await this.fetchAllClients();
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao adicionar cliente.' });
        throw error;
      }
    },
  },
});