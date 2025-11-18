import { route } from 'quasar/wrappers';
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from 'vue-router';
import routes from './routes';
import { useAuthStore } from 'stores/auth-store';

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory);

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  // --- GUARDA DE NAVEGAÇÃO (SECURITY GUARD) ---
  Router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    const isLoggedIn = !!authStore.accessToken; // Verifica se tem token
    const userRole = authStore.user?.role;

    // 1. Rota requer autenticação?
    if (to.matched.some((record) => record.meta.requiresAuth)) {
      if (!isLoggedIn) {
        // Não logado -> Manda para Login
        return next({ name: 'login', query: { next: to.fullPath } });
      }

      // 2. Rota requer permissão (roles)?
      // Verifica se a rota tem 'meta.roles' e se o papel do usuário está incluso
      if (to.meta.roles && Array.isArray(to.meta.roles)) {
        if (userRole && !to.meta.roles.includes(userRole)) {
          // Logado, mas sem permissão -> Redireciona para Dashboard ou 403
          console.warn(`Acesso negado: Usuário ${userRole} tentou acessar ${to.path}`);
          
          // Se for motorista tentando acessar área de gestão, joga pro cockpit/dashboard
          if (userRole === 'driver') {
             return next({ name: 'dashboard' });
          }
          return next({ name: 'dashboard' }); // Fallback seguro
        }
      }
    }

    // 3. Usuário logado tentando acessar Login/Register?
    if (isLoggedIn && (to.name === 'login' || to.name === 'register')) {
      return next({ name: 'dashboard' });
    }

    next();
  });

  return Router;
});