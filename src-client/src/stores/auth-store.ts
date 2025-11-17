import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import { Notify } from 'quasar';
import { isAxiosError } from 'axios'; // <-- ADIÇÃO CRÍTICA PARA CORRIGIR O ERRO
import type { UserNotificationPrefsUpdate } from 'src/models/user-models';
import type {
  LoginForm,
  TokenData,
  User,
  UserSector,
  PasswordRecoveryRequest,
  PasswordResetRequest
} from 'src/models/auth-models';
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
  const isDriver = computed(() => user.value?.role === 'driver');
  const userSector = computed((): UserSector => user.value?.organization?.sector ?? null);
  const isSuperuser = computed(() => user.value?.is_superuser === true);
  const isDemo = computed(() => user.value?.role === 'cliente_demo');
  const isImpersonating = computed(() => !!originalUser.value);

  // --- AÇÕES ---
  async function login(loginForm: LoginForm): Promise<void> { // Mudança 1: O retorno agora é Promise<void>
    const params = new URLSearchParams();
    params.append('username', loginForm.email);
    params.append('password', loginForm.password);
    try {
      const response = await api.post<TokenData>('/login/token', params);
      _setSession(response.data.access_token, response.data.user);
      // Mudança 2: Não há mais 'return true'
    } catch (error) { // Mudança 3: Capturamos o erro
      console.error('Falha no login:', error);
      logout(); // Fazemos o cleanup da sessão
      throw error; // Mudança 4: Lançamos o erro para a página (LoginPage.vue)
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
  
  // --- AÇÕES DE RECUPERAÇÃO DE SENHA ---
  async function requestPasswordReset(payload: PasswordRecoveryRequest): Promise<void> {
    try {
      await api.post('/login/password-recovery', payload);
      Notify.create({
        type: 'positive',
        message: 'Se um usuário com este e-mail existir, um link para redefinição de senha será enviado.',
      });
    } catch (error) {
      console.error('Erro ao solicitar redefinição de senha:', error);
      // Por segurança, mostramos a mesma mensagem no erro para não revelar se um e-mail existe ou não.
      Notify.create({
        type: 'positive',
        message: 'Se um usuário com este e-mail existir, um link para redefinição de senha será enviado.',
      });
    }
  }

  async function resetPassword(payload: PasswordResetRequest): Promise<boolean> {
    try {
      await api.post('/login/reset-password', payload);
      Notify.create({
        type: 'positive',
        message: 'Senha redefinida com sucesso! Você já pode fazer o login.',
        icon: 'o_lock_reset'
      });
      return true;
    } catch (error: unknown) { // <-- CORRIGIDO AQUI
      console.error('Erro ao redefinir senha:', error);
      
      let detail = 'Ocorreu um erro. O token pode ser inválido ou ter expirado.';
      // <-- CORRIGIDO AQUI
      if (isAxiosError(error) && error.response?.data?.detail) {
        detail = error.response.data.detail;
      }

      Notify.create({
        type: 'negative',
        message: detail,
        icon: 'o_error'
      });
      return false;
    }
  }

  // --- FUNÇÕES AUXILIARES ---
  function _setSession(token: string, userData: User) {
    accessToken.value = token;
    user.value = userData;
    // --- CORRIGIDO AQUI ---
    if (userData.organization) {
      useTerminologyStore().setSector(userData.organization.sector);
    }
    // --- FIM DA CORREÇÃO ---
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
    isDriver,
    userSector,
    isSuperuser,
    isDemo,
    login,
    logout,
    isImpersonating,
    originalUser,
    startImpersonation,
    stopImpersonation,
    updateMyPreferences,
    requestPasswordReset,
    resetPassword
  };
});