import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import type { UserNotificationPrefsUpdate } from 'src/models/user-models';
import type { LoginForm, TokenData, User, UserSector } from 'src/models/auth-models';
import { useTerminologyStore } from './terminology-store';

function getFromLocalStorage<T>(key: string): T | null {
  const itemString = localStorage.getItem(key);
  if (!itemString || itemString === 'undefined') return null;
  try {
    return JSON.parse(itemString) as T;
  } catch (e) {
    console.error(`Falha ao interpretar '${key}' do localStorage.`, e);
    localStorage.removeItem(key);
    return null;
  }
}

export const useAuthStore = defineStore('auth', () => {
  // --- ESTADO PRINCIPAL ---
  const accessToken = ref<string | null>(localStorage.getItem('accessToken'));
  const user = ref<User | null>(getFromLocalStorage<User>('user'));

  // --- ESTADO PARA O LOGIN SOMBRA ---
  const originalUser = ref<User | null>(getFromLocalStorage<User>('original_user'));

  // --- PROPRIEDADES COMPUTADAS (GETTERS) ---
  const isAuthenticated = computed(() => !!accessToken.value);
  const isManager = computed(() => ['cliente_ativo', 'cliente_demo'].includes(user.value?.role ?? ''));
  const isDriver = computed(() => user.value?.role === 'driver'); // <-- ADICIONADO E CORRIGIDO
  const userSector = computed((): UserSector => user.value?.organization?.sector ?? null);
  const isSuperuser = computed(() => user.value?.is_superuser === true);
  const isDemo = computed(() => user.value?.role === 'cliente_demo');
  const isImpersonating = computed(() => !!originalUser.value);

  // --- AÇÕES ---
  async function login(loginForm: LoginForm): Promise<boolean> {
    const params = new URLSearchParams();
    params.append('username', loginForm.email);
    params.append('password', loginForm.password);
    try {
      const response = await api.post<TokenData>('/login/token', params);
      _setSession(response.data.access_token, response.data.user);
      return true;
    } catch {
      console.error('Falha no login:');
      logout();
      return false;
    }
  }

  async function updateMyPreferences(payload: UserNotificationPrefsUpdate) {
    try {
      const response = await api.put<User>('/users/me/preferences', payload);
      user.value = response.data;
      localStorage.setItem('user', JSON.stringify(response.data));
      Notify.create({ type: 'positive', message: 'Preferências salvas.' });
    } catch (error) {
      Notify.create({ type: 'negative', message: 'Erro ao salvar preferências.' });
      throw error;
    }
  }

  function logout() {
    console.log('Iniciando processo de logout e reset de todas as stores...');
    // A sua lógica de reset de outras stores viria aqui.

    accessToken.value = null;
    user.value = null;
    originalUser.value = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    localStorage.removeItem('original_accessToken');
    localStorage.removeItem('original_user');
    delete api.defaults.headers.common['Authorization'];
    console.log('Logout concluído.');
  }

  // --- AÇÕES DO LOGIN SOMBRA ---
  function startImpersonation(newToken: string, targetUser: User) {
    if (!user.value || !accessToken.value) {
      console.error('Não é possível iniciar a personificação sem um utilizador admin logado.');
      return;
    }
    localStorage.setItem('original_accessToken', accessToken.value);
    localStorage.setItem('original_user', JSON.stringify(user.value));
    originalUser.value = user.value;

    _setSession(newToken, targetUser);
    window.location.href = '/dashboard';
  }

  function stopImpersonation() {
    const originalToken = localStorage.getItem('original_accessToken');
    const originalAdminUser = getFromLocalStorage<User>('original_user');

    if (!originalToken || !originalAdminUser) {
      console.error('Não foi encontrada uma sessão original para restaurar. A fazer logout completo.');
      logout();
      window.location.href = '/auth/login';
      return;
    }

    _setSession(originalToken, originalAdminUser);
    localStorage.removeItem('original_accessToken');
    localStorage.removeItem('original_user');
    originalUser.value = null;
    window.location.href = '/admin';
  }

  // --- FUNÇÕES AUXILIARES ---
  function _setSession(token: string, userData: User) {
    accessToken.value = token;
    user.value = userData;
    useTerminologyStore().setSector(userData.organization.sector);
    localStorage.setItem('accessToken', token);
    localStorage.setItem('user', JSON.stringify(userData));
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  function init() {
    const token = accessToken.value;
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    useTerminologyStore().setSector(user.value?.organization?.sector ?? null);
  }

  init();

  return {
    accessToken,
    user,
    isAuthenticated,
    isManager,
    isDriver, // <-- EXPORTADO
    userSector,
    isSuperuser,
    isDemo,
    login,
    logout,
    isImpersonating,
    originalUser,
    startImpersonation,
    stopImpersonation,
    updateMyPreferences
  };
});

