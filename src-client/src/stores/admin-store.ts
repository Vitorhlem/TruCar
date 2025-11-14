import { defineStore } from 'pinia';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios';
import type { User } from 'src/models/auth-models';
import type { Organization, OrganizationUpdate } from 'src/models/organization-models';
import { useAuthStore } from './auth-store'; // Importamos a authStore para o login sombra


export const useAdminStore = defineStore('admin', {
  state: () => ({
    demoUsers: [] as User[],
    organizations: [] as Organization[],
        allUsers: [] as User[], // <-- NOVO ESTADO para todos os utilizadores
    isLoading: false,
  }),


  
   actions: {
    async fetchDemoUsers() {
      this.isLoading = true;
      try {
        const response = await api.get<User[]>('/admin/users/demo');
        this.demoUsers = response.data;
      } catch (error) {
        let message = 'Falha ao carregar utilizadores demo.';
        if (isAxiosError(error) && error.response?.data?.detail) message = error.response.data.detail as string;
        Notify.create({ type: 'negative', message });
      } finally {
        this.isLoading = false;
      }
    },

     // --- NOVA AÇÃO ADICIONADA ---
    async fetchAllUsers() {
      this.isLoading = true;
      try {
        const response = await api.get<User[]>('/admin/users/all');
        this.allUsers = response.data;
      } catch (error) {
        let message = 'Falha ao carregar a lista de todos os utilizadores.';
        if (isAxiosError(error) && error.response?.data?.detail) message = error.response.data.detail as string;
        Notify.create({ type: 'negative', message });
      } finally {
        this.isLoading = false;
      }
    },

     async fetchOrganizations(status: string | null = null) {
      this.isLoading = true;
      try {
        const params = status ? { status } : {};
        const response = await api.get<Organization[]>('/admin/organizations/', { params });
        this.organizations = response.data;
      } catch {
        Notify.create({ type: 'negative', message: 'Falha ao carregar organizações.' });
      } finally {
        this.isLoading = false;
      }
    },

     async activateUser(userId: number) {
      try {
        await api.post(`/admin/users/${userId}/activate`);
        Notify.create({ type: 'positive', message: 'Utilizador ativado com sucesso!' });
        
        // --- CORRIGIDO ---
        // Agora, recarregamos as DUAS listas para manter a interface sincronizada
        await Promise.all([
          this.fetchDemoUsers(),
          this.fetchOrganizations()
        ]);
        // --- FIM DA CORREÇÃO ---

      } catch (error) {
        let message = 'Erro ao ativar utilizador.';
        if (isAxiosError(error) && error.response?.data?.detail) {
          message = error.response.data.detail as string;
        }
        Notify.create({ type: 'negative', message });
      }
    },

    // --- NOVA AÇÃO DE LOGIN SOMBRA ---
    async impersonateUser(targetUser: User) {
      try {
        const response = await api.post<{ access_token: string }>(`/admin/users/${targetUser.id}/impersonate`);
        const { access_token } = response.data;

        // Chamamos a authStore para gerir a troca de sessão
        const authStore = useAuthStore();
        authStore.startImpersonation(access_token, targetUser);

      } catch (error) {
        let message = 'Erro ao tentar entrar como este utilizador.';
        if (isAxiosError(error) && error.response?.data?.detail) {
          message = error.response.data.detail as string;
        }
        Notify.create({ type: 'negative', message });
      }
    },

    async updateOrganization(orgId: number, payload: OrganizationUpdate) {
      try {
        await api.put(`/admin/organizations/${orgId}`, payload);
        Notify.create({ type: 'positive', message: 'Organização atualizada com sucesso!' });
        await this.fetchOrganizations();
      } catch (error) {
        let message = 'Erro ao atualizar organização.';
        if (isAxiosError(error) && error.response?.data?.detail) {
          message = error.response.data.detail as string;
        }
        Notify.create({ type: 'negative', message });
        throw error;
      }
    },
  },
});