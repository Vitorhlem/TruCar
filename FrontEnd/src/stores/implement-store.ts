// src/stores/implement-store.ts

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { Implement, ImplementCreate, ImplementUpdate } from 'src/models/implement-models';

export const useImplementStore = defineStore('implement', () => {
  // VOLTANDO A USAR implementList, pois 'implements' é uma palavra reservada.
  const implementList = ref<Implement[]>([]);
  const isLoading = ref(false);

  const availableImplements = computed(() =>
    // Usando a variável com o nome correto
    implementList.value.filter((i) => i.status === 'available')
  );

  async function fetchAllImplements() {
    isLoading.value = true;
    try {
      const response = await api.get<Implement[]>('/implements/');
      // Usando a variável com o nome correto
      implementList.value = response.data;
    } catch (error) {
      console.error('Falha ao buscar implementos:', error);
      Notify.create({ type: 'negative', message: 'Falha ao buscar implementos.' });
    } finally {
      isLoading.value = false;
    }
  }

  async function addImplement(payload: ImplementCreate) {
    try {
      await api.post('/implements/', payload);
      Notify.create({ type: 'positive', message: 'Implemento adicionado com sucesso!' });
      await fetchAllImplements();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao adicionar implemento.' });
      throw error;
    }
  }

  async function updateImplement(id: number, payload: ImplementUpdate) {
    try {
      await api.put(`/implements/${id}`, payload);
      Notify.create({ type: 'positive', message: 'Implemento atualizado com sucesso!' });
      await fetchAllImplements();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao atualizar implemento.' });
      throw error;
    }
  }

  async function deleteImplement(id: number) {
    try {
      await api.delete(`/implements/${id}`);
      Notify.create({ type: 'positive', message: 'Implemento excluído com sucesso.' });
      await fetchAllImplements();
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao excluir implemento.' });
      throw error;
    }
  }

  return {
    // Exportando o nome correto
    implementList,
    isLoading,
    availableImplements,
    fetchAllImplements,
    addImplement,
    updateImplement,
    deleteImplement,
  };
});