// ARQUIVO: src/stores/client-store.ts

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Client, ClientCreate } from 'src/models/client-models';

export const useClientStore = defineStore('client', () => {
  const clients = ref<Client[]>([]);
  const isLoading = ref(false);

  async function fetchAllClients() {
    isLoading.value = true;
    try {
      const response = await api.get<Client[]>('/clients/');
      clients.value = response.data;
    // --- INÍCIO DA CORREÇÃO ---
    // O comentário vem ANTES da linha com o erro
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
    // --- FIM DA CORREÇÃO ---
      Notify.create({ type: 'negative', message: 'Falha ao buscar clientes.' });
    } finally {
      isLoading.value = false;
    }
  }

  async function addClient(payload: ClientCreate) {
    try {
      await api.post('/clients/', payload);
      Notify.create({ type: 'positive', message: 'Cliente adicionado com sucesso!' });
      await fetchAllClients();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao adicionar cliente.' });
      throw error;
    }
  }

  return { clients, isLoading, fetchAllClients, addClient };
});