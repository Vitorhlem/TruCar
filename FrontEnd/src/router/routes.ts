import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: () => import('pages/DashboardPage.vue') },
      { path: 'vehicles', name: 'vehicles', component: () => import('pages/VehiclesPage.vue') },
      { path: 'journeys', name: 'journeys', component: () => import('pages/JourneysPage.vue') },
      { path: 'users', name: 'users', component: () => import('pages/UsersPage.vue') },
      { path: 'users/:id/stats', name: 'user-stats', component: () => import('pages/UserDetailsPage.vue') },
      { path: 'maintenance', name: 'maintenance', component: () => import('pages/MaintenancePage.vue') },
      { path: 'map', name: 'map', component: () => import('pages/MapPage.vue') },
      { path: 'fuel-logs', name: 'fuel-logs', component: () => import('pages/FuelLogsPage.vue') },
      { path: 'performance', name: 'performance', component: () => import('pages/PerformancePage.vue') },
      { path: 'reports', name: 'reports', component: () => import('pages/ReportsPage.vue') },
      { path: 'implements', name: 'implements', component: () => import('pages/ImplementsPage.vue')},
      { path: 'live-map', component: () => import('pages/LiveMapPage.vue'),
      
        
        meta: { requiresAuth: true, requiredRole: 'manager' } // Apenas gestores
  },
    ],
  },
  {
    path: '/auth', // <-- Agrupamos as rotas de autenticação
    component: () => import('layouts/BlankLayout.vue'),
    children: [
      { path: 'login', name: 'login', component: () => import('pages/LoginPage.vue') },
      { path: 'register', name: 'register', component: () => import('pages/RegisterPage.vue') },
    ],
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;