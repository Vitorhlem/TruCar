import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Client, ClientCreate } from 'src/models/client-models';

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
  },
});