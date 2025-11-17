import { route } from 'quasar/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';

import routes from './routes';
import { useAuthStore } from 'stores/auth-store';

export default route(function ({ store  }) {
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


  Router.beforeEach((to, from, next) => {
    const authStore = useAuthStore(store);

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);


    if (requiresAuth && !authStore.isAuthenticated) {

      next({ name: 'login' });
    } 

    else if (to.name === 'login' && authStore.isAuthenticated) {

      next({ name: 'dashboard'});
    }

    else {
      next();
    }
  });


  return Router;
});