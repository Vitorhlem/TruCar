import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import type { Journey } from 'src/models/journey-models';
import type { FreightOrder, FreightOrderCreate, FreightOrderUpdate, FreightOrderClaim } from 'src/models/freight-order-models';

const initialState = () => ({
  freightOrders: [] as FreightOrder[],
  myPendingOrders: [] as FreightOrder[],
  openOrders: [] as FreightOrder[],
  activeOrderDetails: null as FreightOrder | null,
  isLoading: false,
  isDetailsLoading: false,
});

export const useFreightOrderStore = defineStore('freightOrder', {
  state: initialState,
  getters: {
    activeFreightOrder: (state) => 
      state.myPendingOrders.find(o => o.status === 'Em Trânsito') || null,
    claimedFreightOrders: (state) => 
      state.myPendingOrders.filter(o => o.status === 'Atribuída'),
  },
  actions: {
    async fetchAllFreightOrders() {
      // (Esta função já estava correta, mas vou adicionar a melhoria de erro)
      this.isLoading = true;
      try {
        const response = await api.get<FreightOrder[]>('/freight-orders/');
        this.freightOrders = response.data;
      } catch (error) {
        let message = 'Falha ao buscar ordens de frete.';
        if (isAxiosError(error) && error.response?.data?.detail) message = error.response.data.detail as string;
        Notify.create({ type: 'negative', message });
      } finally { 
        this.isLoading = false; 
      }
    },


     async fetchOpenOrders() {
      this.isLoading = true;
      try {
        const response = await api.get<FreightOrder[]>('/freight-orders/open');
        this.openOrders = response.data;
      } catch (error) { // <-- CORRIGIDO
        let message = 'Falha ao buscar fretes abertos.';
        if (isAxiosError(error) && error.response?.data?.detail) message = error.response.data.detail as string;
        Notify.create({ type: 'negative', message });
      } finally { 
        this.isLoading = false; 
      }
    },

    async fetchMyPendingOrders() {
      this.isLoading = true;
      try {
        const response = await api.get<FreightOrder[]>('/freight-orders/my-pending');
        this.myPendingOrders = response.data;
      } catch (error) { // <-- CORRIGIDO
        let message = 'Falha ao buscar suas tarefas.';
        if (isAxiosError(error) && error.response?.data?.detail) message = error.response.data.detail as string;
        Notify.create({ type: 'negative', message });
      } finally { 
        this.isLoading = false; 
      }
    },
    

    async fetchOrderDetails(orderId: number) {
      this.isDetailsLoading = true;
      try {
        const response = await api.get<FreightOrder>(`/freight-orders/${orderId}`);
        this.activeOrderDetails = response.data;
        const index = this.myPendingOrders.findIndex(o => o.id === orderId);
        if (index !== -1) {
          this.myPendingOrders[index] = response.data;
        }
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar detalhes do frete.' });
        this.activeOrderDetails = null;
      } finally {
        this.isDetailsLoading = false;
      }
    },

    async claimFreightOrder(orderId: number, payload: FreightOrderClaim) {
      try {
        await api.put(`/freight-orders/${orderId}/claim`, payload);
        Notify.create({ type: 'positive', message: 'Frete atribuído a você!' });
        await Promise.all([this.fetchOpenOrders(), this.fetchMyPendingOrders()]);
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Não foi possível se atribuir a este frete.' });
        throw error;
      }
    },

    async startJourneyForStop(orderId: number, stopPointId: number): Promise<Journey | null> {
      try {
        const response = await api.post<Journey>(`/freight-orders/${orderId}/start-leg/${stopPointId}`);
        Notify.create({ type: 'positive', message: 'Viagem iniciada!' });
        return response.data;
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Falha ao iniciar viagem.' });
        throw error;
      }
    },

    async completeStop(orderId: number, stopPointId: number, journeyId: number, endMileage: number) {
      try {
        const payload = { journey_id: journeyId, end_mileage: endMileage };
        await api.put(`/freight-orders/${orderId}/complete-stop/${stopPointId}`, payload);
        Notify.create({ type: 'positive', message: 'Parada concluída!' });
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Falha ao concluir parada.' });
        throw error;
      }
    },

    async addFreightOrder(payload: FreightOrderCreate) {
      try {
        await api.post('/freight-orders/', payload);
        Notify.create({ type: 'positive', message: 'Ordem de frete criada com sucesso!' });
        await this.fetchAllFreightOrders();
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Erro ao criar ordem de frete.' });
        throw error;
      }
    },

    async updateFreightOrder(id: number, payload: FreightOrderUpdate) {
      try {
        await api.put(`/freight-orders/${id}`, payload);
        Notify.create({ type: 'positive', message: 'Ordem de frete atualizada!' });
        await this.fetchAllFreightOrders();
        if (this.activeOrderDetails && this.activeOrderDetails.id === id) {
          await this.fetchOrderDetails(id);
        }
      } catch {
        Notify.create({ type: 'negative', message: 'Erro ao atualizar ordem de frete.' });
      
      }
    },
  },
});