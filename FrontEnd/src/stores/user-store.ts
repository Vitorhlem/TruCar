import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import type { User } from 'src/models/auth-models';
import type { UserCreate, UserUpdate, UserStats } from 'src/models/user-models';


export const useUserStore = defineStore('user', () => {
  const users = ref<User[]>([]);
  const isLoading = ref(false);
  const selectedUserStats = ref<UserStats | null>(null);

  // --- ACTIONS ---

    async function deleteUser(userId: number) {
    isLoading.value = true;
    try {
      await api.delete(`/users/${userId}`);
      // Remove o usuário da lista local para atualização instantânea da UI
      users.value = users.value.filter(u => u.id !== userId);
      Notify.create({ type: 'positive', message: 'Usuário excluído com sucesso!' });
    } catch (error: unknown) {
      console.error('Falha ao excluir usuário:', error);
      let message = 'Erro ao excluir usuário.';
      if (isAxiosError(error) && error.response?.data?.detail) {
        message = error.response.data.detail as string;
      }
      Notify.create({ type: 'negative', message });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchAllUsers() {
    isLoading.value = true;
    try {
      const response = await api.get<User[]>('/users/');
      users.value = response.data;
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Falha ao carregar usuários.' });
      console.error('Falha ao buscar usuários:', error);
    } finally {
      isLoading.value = false;
    }
  }

  async function addNewUser(userData: UserCreate) {
    isLoading.value = true;
    try {
      const response = await api.post<User>('/users/', userData);
      users.value.unshift(response.data);
      Notify.create({ type: 'positive', message: 'Usuário adicionado com sucesso!' });
    } catch (error: unknown) {
      console.error('Falha ao adicionar usuário:', error);
      let message = 'Erro ao criar usuário.';
      if (isAxiosError(error) && error.response?.data?.detail) {
        message = error.response.data.detail as string;
      }
      Notify.create({ type: 'negative', message });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateUser(userId: number, userData: UserUpdate) {
    isLoading.value = true;
    try {
      const response = await api.put<User>(`/users/${userId}`, userData);
      const index = users.value.findIndex(u => u.id === userId);
      if (index !== -1) {
        users.value[index] = response.data;
      }
      Notify.create({ type: 'positive', message: 'Usuário atualizado com sucesso!' });
    } catch (error: unknown) {
      console.error('Falha ao atualizar usuário:', error);
      Notify.create({ type: 'negative', message: 'Erro ao atualizar usuário.' });
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

   async function fetchUserStats(userId: number) {
    isLoading.value = true;
    try {
      const response = await api.get<UserStats>(`/users/${userId}/stats`);
      selectedUserStats.value = response.data;
    } catch {
      Notify.create({ type: 'negative', message: 'Falha ao carregar estatísticas do usuário.' });
    } finally {
      isLoading.value = false;
    }
  }

return {
    users,
    isLoading,
    selectedUserStats,
    fetchAllUsers,
    addNewUser,
    updateUser,
    deleteUser,
    fetchUserStats,
  };
});