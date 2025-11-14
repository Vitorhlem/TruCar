import { route } from 'quasar/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';

import routes from './routes';
import { useAuthStore } from 'stores/auth-store'; // <-- IMPORTE NOSSA STORE

export default route(function ({ store /*, ssrContext */ }) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
    ? createWebHistory
    : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  // --- NOSSO GUARDA DE NAVEGAÇÃO ---
  Router.beforeEach((to, from, next) => {
    const authStore = useAuthStore(store);

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

    // Se a rota exige autenticação E o usuário não está logado...
    if (requiresAuth && !authStore.isAuthenticated) {
      // ...redireciona para o login.
      next({ name: 'login' });
    } 
    // Se a rota NÃO exige auth (ex: login) E o usuário JÁ está logado...
    else if (to.name === 'login' && authStore.isAuthenticated) {
      // ...redireciona para o dashboard.
      next({ name: 'dashboard'});
    }
    // Caso contrário, permite a navegação.
    else {
      next();
    }
  });
  // --- FIM DO GUARDA ---

  return Router;
});