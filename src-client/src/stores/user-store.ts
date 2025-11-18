import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import type { User } from 'src/models/auth-models';
import type { UserCreate, UserUpdate, UserStats } from 'src/models/user-models';
import { useAuthStore } from './auth-store'; 
import { useDemoStore } from './demo-store';

const initialState = () => ({
  users: [] as User[],
  isLoading: false,
  selectedUserStats: null as UserStats | null,
  selectedUser: null as User | null,
});

export const useUserStore = defineStore('user', {
  state: initialState,

  actions: {
    async fetchAllUsers() {
      this.isLoading = true;
      try {
        // --- CORREÇÃO: Removida a barra final ---
        const response = await api.get<User[]>('/users');
        // ----------------------------------------
        this.users = response.data;
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Falha ao carregar usuários.' });
        console.error('Falha ao buscar usuários:', error);
      } finally {
        this.isLoading = false;
      }
    },

    async addNewUser(userData: UserCreate) {
      this.isLoading = true;
      try {
        // --- CORREÇÃO: Removida a barra final ---
        const response = await api.post<User>('/users', userData);
        // ----------------------------------------
        this.users.unshift(response.data);
        Notify.create({ type: 'positive', message: 'Usuário adicionado com sucesso!' });

        const authStore = useAuthStore();
        if (authStore.isDemo) {
          await useDemoStore().fetchDemoStats(true);
        }

      } catch (error: unknown) {
        let message = 'Erro ao criar usuário.';
        if (isAxiosError(error) && error.response?.data?.detail) {
          message = error.response.data.detail as string;
        }
        Notify.create({ type: 'negative', message });
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // ... (restante do arquivo: updateUser, deleteUser, etc. permanecem iguais)
    async updateUser(userId: number, userData: UserUpdate) {
      this.isLoading = true;
      try {
        const response = await api.put<User>(`/users/${userId}`, userData);
        const index = this.users.findIndex(u => u.id === userId);
        if (index !== -1) {
          this.users[index] = response.data;
        }
        Notify.create({ type: 'positive', message: 'Usuário atualizado com sucesso!' });
      } catch (error: unknown) {
        Notify.create({ type: 'negative', message: 'Erro ao atualizar usuário.' });
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteUser(userId: number) {
      this.isLoading = true;
      try {
        await api.delete(`/users/${userId}`);
        this.users = this.users.filter(u => u.id !== userId);
        Notify.create({ type: 'positive', message: 'Usuário excluído com sucesso!' });

        const authStore = useAuthStore();
        if (authStore.isDemo) {
          await useDemoStore().fetchDemoStats(true);
        }

      } catch (error: unknown) {
        let message = 'Erro ao excluir usuário.';
        if (isAxiosError(error) && error.response?.data?.detail) {
          message = error.response.data.detail as string;
        }
        Notify.create({ type: 'negative', message });
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUserStats(userId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<UserStats>(`/users/${userId}/stats`);
        this.selectedUserStats = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar estatísticas do usuário.' });
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUserById(userId: number) {
      this.isLoading = true;
      try {
        const response = await api.get<User>(`/users/${userId}`);
        this.selectedUser = response.data;
      } catch (error) {
        Notify.create({ type: 'negative', message: 'Falha ao carregar dados do usuário.' });
        console.error(`Falha ao buscar usuário ${userId}:`, error);
      } finally {
        this.isLoading = false;
      }
    },
  },
});