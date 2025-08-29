// ARQUIVO: src/stores/freight-order-store.ts

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { FreightOrder, FreightOrderCreate, FreightOrderUpdate, FreightOrderClaim } from 'src/models/freight-order-models';

export const useFreightOrderStore = defineStore('freightOrder', () => {
  
  // --- STATE ---
  const freightOrders = ref<FreightOrder[]>([]);       // Lista principal para a visão do GESTOR
  const myPendingOrders = ref<FreightOrder[]>([]);       // Lista de tarefas ativas do MOTORISTA
  const openOrders = ref<FreightOrder[]>([]);          // Mural de fretes abertos para o MOTORISTA
  const activeDriverOrder = ref<FreightOrder | null>(null); // Ordem selecionada pelo motorista para uma ação
  
  const isLoading = ref(false);
  const isLoadingDetails = ref(false); // Para o diálogo de detalhes do gestor

  // --- ACTIONS ---

  // Para a visão do GESTOR (Kanban)
  async function fetchAllFreightOrders() {
    isLoading.value = true;
    try {
      const response = await api.get<FreightOrder[]>('/freight-orders/');
      freightOrders.value = response.data;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao buscar ordens de frete.' });
    } finally {
      isLoading.value = false;
    }
  }

  // Para a visão do MOTORISTA (Mural de Fretes)
  async function fetchOpenOrders() {
    isLoading.value = true;
    try {
      const response = await api.get<FreightOrder[]>('/freight-orders/open');
      openOrders.value = response.data;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao buscar fretes abertos.' });
    } finally {
      isLoading.value = false;
    }
  }

  // Para a visão do MOTORISTA (Minhas Tarefas)
  async function fetchMyPendingOrders() {
    isLoading.value = true;
    try {
      const response = await api.get<FreightOrder[]>('/freight-orders/my-pending');
      myPendingOrders.value = response.data;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao buscar seus fretes.' });
    } finally {
      isLoading.value = false;
    }
  }

  // Ação do MOTORISTA: se atribuir a um frete
  async function claimFreightOrder(orderId: number, payload: FreightOrderClaim) {
    try {
      await api.put(`/freight-orders/${orderId}/claim`, payload);
      Notify.create({ type: 'positive', message: 'Frete atribuído a você com sucesso!' });
      // Após se atribuir, recarrega o mural e as tarefas
      await Promise.all([fetchOpenOrders(), fetchMyPendingOrders()]);
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Não foi possível se atribuir a este frete.' });
      throw error;
    }
  }

  // Ação do MOTORISTA: iniciar um trecho
  async function startJourneyForStop(orderId: number, stopPointId: number) {
    try {
      await api.post(`/freight-orders/${orderId}/start-leg/${stopPointId}`);
      Notify.create({ type: 'positive', message: 'Viagem iniciada!' });
      await fetchMyPendingOrders();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao iniciar viagem.' });
      throw error;
    }
  }

  // Ação do MOTORISTA: completar uma parada
  async function completeStop(orderId: number, stopPointId: number, endMileage: number) {
    try {
      await api.put(`/freight-orders/${orderId}/complete-stop/${stopPointId}?end_mileage=${endMileage}`);
      Notify.create({ type: 'positive', message: 'Parada concluída com sucesso!' });
      await fetchMyPendingOrders();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao concluir parada.' });
      throw error;
    }
  }

  // Ação do GESTOR: criar um frete
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

  // Ação do GESTOR: atualizar um frete
  async function updateFreightOrder(id: number, payload: FreightOrderUpdate) {
    try {
      await api.put(`/freight-orders/${id}`, payload);
      Notify.create({ type: 'positive', message: 'Ordem de frete atualizada!' });
      await fetchAllFreightOrders();
      if (activeDriverOrder.value && activeDriverOrder.value.id === id) {
        await fetchOrderDetails(id);
      }
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar ordem de frete.' });
      throw error;
    }
  }

  // Ação do GESTOR: ver detalhes de um frete
  async function fetchOrderDetails(orderId: number) {
    isLoadingDetails.value = true;
    try {
      const response = await api.get<FreightOrder>(`/freight-orders/${orderId}`);
      activeDriverOrder.value = response.data; // Reutiliza a mesma ref
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao buscar detalhes da ordem de frete.' });
      activeDriverOrder.value = null;
    } finally {
      isLoadingDetails.value = false;
    }
  }

  return {
    // State
    freightOrders,
    myPendingOrders,
    openOrders,
    activeDriverOrder,
    isLoading,
    isLoadingDetails,
    // Actions
    fetchAllFreightOrders,
    fetchMyPendingOrders,
    fetchOpenOrders,
    fetchOrderDetails,
    addFreightOrder,
    updateFreightOrder,
    claimFreightOrder,
    startJourneyForStop,
    completeStop,
  };
});