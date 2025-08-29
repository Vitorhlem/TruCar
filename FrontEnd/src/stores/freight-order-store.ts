// ARQUIVO: src/stores/freight-order-store.ts

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { FreightOrder, FreightOrderCreate, FreightOrderUpdate } from 'src/models/freight-order-models';

export const useFreightOrderStore = defineStore('freightOrder', () => {
  const freightOrders = ref<FreightOrder[]>([]);
  const isLoading = ref(false);

  async function fetchAllFreightOrders() {
    isLoading.value = true;
    try {
      const response = await api.get<FreightOrder[]>('/freight-orders/');
      freightOrders.value = response.data;
    // --- INÍCIO DA CORREÇÃO ---
    // O comentário vem ANTES da linha com o erro
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
    // --- FIM DA CORREÇÃO ---
      Notify.create({ type: 'negative', message: 'Falha ao buscar ordens de frete.' });
    } finally {
      isLoading.value = false;
    }
  }

  async function addFreightOrder(payload: FreightOrderCreate) {
    try {
      await api.post('/freight-orders/', payload);
      Notify.create({ type: 'positive', message: 'Ordem de frete criada com sucesso!' });
      await fetchAllFreightOrders();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao criar ordem de frete.' });
      throw error;
    }
  }

  async function updateFreightOrder(id: number, payload: FreightOrderUpdate) {
    try {
      await api.put(`/freight-orders/${id}`, payload);
      Notify.create({ type: 'positive', message: 'Ordem de frete atualizada!' });
      await fetchAllFreightOrders();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar ordem de frete.' });
      throw error;
    }
  }

  return {
    freightOrders,
    isLoading,
    fetchAllFreightOrders,
    addFreightOrder,
    updateFreightOrder
  };
});