import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Journey } from 'src/models/journey-models';

import type { FreightOrder, FreightOrderCreate, FreightOrderUpdate, FreightOrderClaim } from 'src/models/freight-order-models';

export const useFreightOrderStore = defineStore('freightOrder', () => {
  
  // --- STATE ---
  const freightOrders = ref<FreightOrder[]>([]);
  const myPendingOrders = ref<FreightOrder[]>([]);
  const openOrders = ref<FreightOrder[]>([]);
  const activeOrderDetails = ref<FreightOrder | null>(null);
  const isLoading = ref(false);
  const isDetailsLoading = ref(false);

  // --- GETTERS (Computed) ---
  const activeFreightOrder = computed(() => myPendingOrders.value.find(o => o.status === 'Em Trânsito') || null);
  const claimedFreightOrders = computed(() => myPendingOrders.value.filter(o => o.status === 'Atribuída'));

  // --- ACTIONS ---
  async function fetchAllFreightOrders() {
    isLoading.value = true;
    try {
      const response = await api.get<FreightOrder[]>('/freight-orders/');
      freightOrders.value = response.data;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao buscar ordens de frete.' });
    } finally { isLoading.value = false; }
  }

  async function fetchOpenOrders() {
    isLoading.value = true;
    try {
      const response = await api.get<FreightOrder[]>('/freight-orders/open');
      openOrders.value = response.data;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao buscar fretes abertos.' });
    } finally { isLoading.value = false; }
  }
  async function fetchMyPendingOrders() {
    isLoading.value = true;
    try {
      const response = await api.get<FreightOrder[]>('/freight-orders/my-pending');
      myPendingOrders.value = response.data;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao buscar suas tarefas.' });
    } finally { isLoading.value = false; }
  }

      async function fetchOrderDetails(orderId: number) {
    isDetailsLoading.value = true;
    try {
      const response = await api.get<FreightOrder>(`/freight-orders/${orderId}`);
      activeOrderDetails.value = response.data;
      // Também atualiza a instância na lista principal, para manter a reatividade da página.
      const index = myPendingOrders.value.findIndex(o => o.id === orderId);
      if (index !== -1) {
        myPendingOrders.value[index] = response.data;
      }
    } catch {
      Notify.create({ type: 'negative', message: 'Falha ao carregar detalhes do frete.' });
      activeOrderDetails.value = null;
    } finally {
      isDetailsLoading.value = false;
    }
  }

  async function claimFreightOrder(orderId: number, payload: FreightOrderClaim) {
    try {
      await api.put(`/freight-orders/${orderId}/claim`, payload);
      Notify.create({ type: 'positive', message: 'Frete atribuído a você!' });
      await Promise.all([fetchOpenOrders(), fetchMyPendingOrders()]);
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Não foi possível se atribuir a este frete.' });
      throw error;
    }
  }

    async function startJourneyForStop(orderId: number, stopPointId: number): Promise<Journey | null> {
    try {
      const response = await api.post<Journey>(`/freight-orders/${orderId}/start-leg/${stopPointId}`);
      Notify.create({ type: 'positive', message: 'Viagem iniciada!' });
      // Não recarregamos aqui para não causar loop, o componente vai gerenciar
      return response.data;
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao iniciar viagem.' });
      throw error;
    }
  }

    async function completeStop(orderId: number, stopPointId: number, journeyId: number, endMileage: number) {
    try {
      const payload = { journey_id: journeyId, end_mileage: endMileage };
      await api.put(`/freight-orders/${orderId}/complete-stop/${stopPointId}`, payload);
      Notify.create({ type: 'positive', message: 'Parada concluída!' });
      // Após concluir, a página principal irá recarregar os dados
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao concluir parada.' });
      throw error;
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
      if (activeOrderDetails.value && activeOrderDetails.value.id === id) {
        await fetchOrderDetails(id);
      }
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar ordem de frete.' });
      throw error;
    }
  }

  return {
    // State
    freightOrders, myPendingOrders, openOrders, activeOrderDetails,
    isLoading, isDetailsLoading,
    // Getters
    activeFreightOrder, claimedFreightOrders,
    // Actions
    fetchAllFreightOrders, fetchOpenOrders, fetchMyPendingOrders, fetchOrderDetails,
    claimFreightOrder, startJourneyForStop, completeStop,
    addFreightOrder, updateFreightOrder,
  };
});