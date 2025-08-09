import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import type { LoginForm, AuthToken, User } from 'src/models/auth-models';

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('accessToken'));
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'));
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'));
  const isManager = computed(() => user.value?.role === 'manager');

  const isAuthenticated = computed(() => !!accessToken.value);

  async function login(loginForm: LoginForm): Promise<void> {
    const params = new URLSearchParams();
    params.append('username', loginForm.email);
    params.append('password', loginForm.password);

    const response = await api.post<AuthToken>('/login/token', params);
    const { access_token, refresh_token } = response.data;

    setTokens(access_token, refresh_token);
    await fetchUser();
  }

  function setTokens(newAccessToken: string, newRefreshToken: string) {
    accessToken.value = newAccessToken;
    refreshToken.value = newRefreshToken;
    localStorage.setItem('accessToken', newAccessToken);
    localStorage.setItem('refreshToken', newRefreshToken);
  }

  async function fetchUser() {
    if (!accessToken.value) return;
    try {
      const response = await api.get<User>('/users/me');
      user.value = response.data;
      localStorage.setItem('user', JSON.stringify(user.value));
    } catch (error) {
      console.error('Falha ao buscar dados do usuário, fazendo logout.', error);
      logout();
    }
  }

  // --- FUNÇÃO LOGOUT CORRIGIDA ---
  // A responsabilidade dela é apenas limpar o estado.
  function logout() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }

  return {
    accessToken,
    refreshToken,
     isManager,
    user,
    isAuthenticated,
    login,
    logout,
    fetchUser,
  };
});