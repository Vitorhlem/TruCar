// ARQUIVO: src/stores/implement-store.ts

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Implement, ImplementCreate, ImplementUpdate } from 'src/models/implement-models';

export const useImplementStore = defineStore('implement', () => {
  // --- STATE ---
  // A lista principal que armazena os implementos. Será populada por diferentes funções.
  const implementList = ref<Implement[]>([]);
  const isLoading = ref(false);

  // --- GETTERS (Computed) ---
  // Uma propriedade reativa que SEMPRE retorna apenas os implementos disponíveis.
  // Perfeita para usar nos formulários de seleção, como o de "Iniciar Operação".
  const availableImplements = computed(() =>
    implementList.value.filter((i) => i.status === 'available')
  );

  // --- ACTIONS (Functions) ---

  /**
   * Ação #1: Busca TODOS os implementos, sem filtro de status.
   * USAR NA PÁGINA DE GERENCIAMENTO DE IMPLEMENTOS.
   */
  async function fetchAllImplementsForManagement() {
    isLoading.value = true;
    try {
      // Chama o endpoint de gerenciamento que não filtra por status
      const response = await api.get<Implement[]>('/implements/management-list');
      implementList.value = response.data;
    } catch (error) {
      console.error('Falha ao buscar implementos para gerenciamento:', error);
      Notify.create({ type: 'negative', message: 'Falha ao buscar lista de implementos.' });
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Ação #2: Busca APENAS os implementos com status "available".
   * USAR NO FORMULÁRIO DE "INICIAR OPERAÇÃO".
   */
  async function fetchAvailableImplements() {
    isLoading.value = true;
    try {
      // Chama o endpoint original, que já tem o filtro no backend
      const response = await api.get<Implement[]>('/implements/');
      // Esta computed property 'availableImplements' não é necessária aqui,
      // mas populamos a lista principal para consistência.
      implementList.value = response.data;
    } catch (error) {
      console.error('Falha ao buscar implementos disponíveis:', error);
      Notify.create({ type: 'negative', message: 'Falha ao buscar implementos disponíveis.' });
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Ações CRUD: Adicionar, Atualizar, Deletar.
   * Após cada ação, a lista COMPLETA de gerenciamento é recarregada.
   */
  async function addImplement(payload: ImplementCreate) {
    try {
      await api.post('/implements/', payload);
      Notify.create({ type: 'positive', message: 'Implemento adicionado com sucesso!' });
      // Recarrega a lista completa para refletir a adição na tela de gerenciamento
      await fetchAllImplementsForManagement();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao adicionar implemento.' });
      throw error;
    }
  }

  async function updateImplement(id: number, payload: ImplementUpdate) {
    try {
      await api.put(`/implements/${id}`, payload);
      Notify.create({ type: 'positive', message: 'Implemento atualizado com sucesso!' });
      // Recarrega a lista completa para refletir a atualização
      await fetchAllImplementsForManagement();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar implemento.' });
      throw error;
    }
  }

  async function deleteImplement(id: number) {
    try {
      await api.delete(`/implements/${id}`);
      Notify.create({ type: 'positive', message: 'Implemento excluído com sucesso.' });
      // Recarrega a lista completa para refletir a exclusão
      await fetchAllImplementsForManagement();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao excluir implemento.' });
      throw error;
    }
  }

  // --- EXPORTS ---
  // Tudo que será usado pelos componentes Vue
  return {
    implementList,
    isLoading,
    availableImplements,
    fetchAvailableImplements,         // Para o formulário de Jornada
    fetchAllImplementsForManagement,  // Para a página de Gerenciamento
    addImplement,
    updateImplement,
    deleteImplement,
  };
});