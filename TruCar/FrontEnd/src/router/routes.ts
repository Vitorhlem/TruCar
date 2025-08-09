import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('pages/DashboardPage.vue'),
      },
      {
        path: 'vehicles',
        name: 'vehicles',
        component: () => import('pages/VehiclesPage.vue'),
      },
      {
        path: 'journeys',
        name: 'journeys',
        component: () => import('pages/JourneysPage.vue'),
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('pages/UsersPage.vue'),
      },
// ...
    ],
  }, // <-- VÍRGULA FALTANTE CORRIGIDA AQUI
  {
    path: '/login',
    component: () => import('layouts/BlankLayout.vue'),
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('pages/LoginPage.vue'),
      },
    ],
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;