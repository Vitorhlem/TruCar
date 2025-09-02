import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';
import type { LoginForm, TokenData, User, UserSector } from 'src/models/auth-models';

// Importamos TODAS as outras stores que precisam de ser reiniciadas
import { useTerminologyStore } from './terminology-store';
import { useVehicleStore } from './vehicle-store';
import { useUserStore } from './user-store';
import { useJourneyStore } from './journey-store';
import { useFreightOrderStore } from './freight-order-store';
import { useDashboardStore } from './dashboard-store';
import { useDemoStore } from './demo-store';
import { useClientStore } from './client-store';
import { useFuelLogStore } from './fuel-log-store';
import { useImplementStore } from './implement-store';
import { useLeaderboardStore } from './leaderboard-store';
import { useMaintenanceStore } from './maintenance-store';
import { useNotificationStore } from './notification-store';
import { usePerformanceStore } from './performance-store';


function getInitialUser(): User | null {
  const userString = localStorage.getItem('user');
  if (!userString || userString === 'undefined') return null;
  try {
    return JSON.parse(userString) as User;
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
  
  const isManager = computed(() => 
    ['cliente_ativo', 'cliente_demo'].includes(user.value?.role ?? '')
  );

  const userSector = computed((): UserSector => {
    return user.value?.organization?.sector ?? null;
  });

  async function login(loginForm: LoginForm): Promise<boolean> {
    const params = new URLSearchParams();
    params.append('username', loginForm.email);
    params.append('password', loginForm.password);
    try {
      const response = await api.post<TokenData>('/login/token', params);
      const { access_token, user: userData } = response.data;
      accessToken.value = access_token;
      user.value = userData;

      const terminologyStore = useTerminologyStore();
      terminologyStore.setSector(userData.organization.sector);
      
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      return true;
    } catch (error) {
      console.error('Falha no login:', error);
      logout();
      return false;
    }
  }

  function logout() {
    // --- O RESET MESTRE ACONTECE AQUI ---
    // 1. Chamamos o reset de todas as outras stores
    useTerminologyStore().$reset();
    useVehicleStore().$reset();
    useUserStore().$reset();
    useJourneyStore().$reset();
    useFreightOrderStore().$reset();
    useDashboardStore().$reset();
    useDemoStore().$reset();
    useClientStore().$reset();
    useFuelLogStore().$reset();
    useImplementStore().$reset();
    useLeaderboardStore().$reset();
    useMaintenanceStore().$reset();
    useNotificationStore().$reset();
    usePerformanceStore().$reset();
    // (Adicione aqui o $reset de qualquer outra store que criar no futuro)

    // 2. Limpamos a própria store de autenticação
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
    const terminologyStore = useTerminologyStore();
    terminologyStore.setSector(user.value?.organization?.sector ?? null);
  }
  
  init();

  return { accessToken, user, isAuthenticated, isManager, userSector, login, logout };
});