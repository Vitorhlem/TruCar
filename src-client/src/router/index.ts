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
    const isLoggedIn = !!authStore.accessToken;
    const userRole = authStore.user?.role;

    // 1. Rota requer autenticação?
    if (to.matched.some((record) => record.meta.requiresAuth)) {
      if (!isLoggedIn) {
        // Não logado -> Manda para Login
        return next({ name: 'login', query: { next: to.fullPath } });
      }

      // 2. Rota requer permissão (roles)?
      if (to.meta.roles && Array.isArray(to.meta.roles)) {
        
        // Admin ignora restrições
        const isAdmin = userRole === 'admin';
        
        // Se o usuário NÃO tem a role necessária
        if (userRole && !isAdmin && !to.meta.roles.includes(userRole)) {
          console.warn(`Acesso negado: Usuário ${userRole} tentou acessar ${to.path}`);
          
          // --- CORREÇÃO DO LOOP INFINITO ---
          
          // Se for motorista, mandamos para a rota DELE (driver-cockpit ou home)
          // E verificamos se ele JÁ NÃO ESTÁ tentando ir pra lá
          if (userRole === 'driver') {
             if (to.name === 'driver-cockpit') {
                 return next(); // Deixa passar se já for o destino certo
             }
             return next({ name: 'driver-cockpit' }); // Redireciona para a área do motorista
          }

          // Para outros usuários, se tentarem acessar algo proibido e o dashboard também for proibido,
          // precisamos garantir que não estamos criando um loop.
          if (to.name !== 'dashboard') {
             return next({ name: 'dashboard' });
          }
          
          // Se chegou aqui, o usuário está tentando acessar o 'dashboard', não tem permissão,
          // e estamos tentando redirecioná-lo para o próprio dashboard.
          // Solução: Abortar navegação ou mandar para Login.
          console.error('Loop de redirecionamento detectado. Forçando logout.');
          authStore.logout();
          return next({ name: 'login' });
        }
      }
    }

    // 3. Usuário logado tentando acessar Login/Register?
    if (isLoggedIn && (to.name === 'login' || to.name === 'register')) {
      // Se for motorista, manda pro cockpit, senão dashboard
      if (userRole === 'driver') {
          return next({ name: 'driver-cockpit' });
      }
      return next({ name: 'dashboard' });
    }

    next();
  });

  return Router;
});