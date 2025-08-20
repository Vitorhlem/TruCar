// src/stores/auth-store.ts

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import type { LoginForm, TokenData, User } from 'src/models/auth-models';

// Função auxiliar para ler o utilizador do localStorage de forma segura
function getInitialUser(): User | null {
  const userString = localStorage.getItem('user');
  if (!userString || userString === 'undefined') {
    return null;
  }
  try {
    return JSON.parse(userString);
  } catch (e) {
    console.error("Falha ao interpretar o 'user' do localStorage.", e);
    localStorage.removeItem('user');
    return null;
  }
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('accessToken'));
  const user = ref<User | null>(getInitialUser());

  const isAuthenticated = computed(() => !!accessToken.value);
  const isManager = computed(() => user.value?.role === 'manager');
  const userSector = computed(() => user.value?.organization?.sector || null);

  async function login(loginForm: LoginForm): Promise<void> {
    const params = new URLSearchParams();
    params.append('username', loginForm.email);
    params.append('password', loginForm.password);

    const response = await api.post<TokenData>('/login/token', params);
    
    // --- A CORREÇÃO CRUCIAL ESTÁ AQUI ---
    // Extraímos os dados da nova estrutura aninhada
    const { user: userData, token } = response.data;
    const { access_token } = token;

    // O resto da lógica continua igual
    accessToken.value = access_token;
    user.value = userData;
    
    localStorage.setItem('accessToken', access_token);
    localStorage.setItem('user', JSON.stringify(userData));

    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
  }

  function logout() {
    accessToken.value = null;
    user.value = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
  }

  function init() {
    const token = accessToken.value;
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }
  
  init();

  return {
    accessToken,
    user,
    isAuthenticated,
    isManager,
    userSector,
    login,
    logout,
  };
});