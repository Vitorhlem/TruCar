import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      
      // --- 1. DASHBOARD (Ponto de entrada comum) ---
      { 
        path: 'dashboard', 
        name: 'dashboard', 
        component: () => import('pages/DashboardPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo', 'driver'] }
      },
      
      // --- 2. ROTAS DE MOTORISTA (Operacionais) ---
      { 
        path: 'driver-cockpit', 
        name: 'driver-cockpit',
        component: () => import('pages/DriverCockpitPage.vue'),
        meta: { roles: ['driver'] } 
      },
      { 
        path: 'maintenance', 
        name: 'maintenance', 
        component: () => import('pages/MaintenancePage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo', 'driver'] }
      },
      { 
        path: 'fuel-logs', 
        name: 'fuel-logs', 
        component: () => import('pages/FuelLogsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo', 'driver'] }
      },
      {
        path: 'fines',
        name: 'fines',
        component: () => import('pages/FinesPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo', 'driver'] }
      },
      { 
        path: 'vehicles', 
        name: 'vehicles', 
        component: () => import('pages/VehiclesPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo', 'driver'] }
      },
      { 
        path: 'documents', 
        name: 'documents', 
        component: () => import('pages/DocumentPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo', 'driver'] }
      },
      // Perfil Pessoal (Motorista vê o seu)
      { 
        path: 'users/:id/stats', 
        name: 'user-stats', 
        component: () => import('pages/UserDetailsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo', 'driver'] }
      },
      { 
        path: 'journeys', 
        name: 'journeys', 
        component: () => import('pages/JourneysPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo', 'driver'] }
      },
      { path: 'audit-logs', name: 'audit-logs', component: () => import('pages/AuditLogsPage.vue'), meta: { requiresAuth: true, roles: ['admin', 'cliente_ativo', 'cliente_demo'] } },
      // --- 3. ROTAS DE GESTÃO (Bloqueadas para Driver) ---
      // O Admin terá acesso a tudo isso graças à alteração no index.ts
      
      // Detalhes de Veículo
      { 
        path: 'vehicles/:id', 
        name: 'vehicle-details', 
        component: () => import('pages/VehicleDetailsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      
      { 
        path: 'users', 
        name: 'users', 
        component: () => import('pages/UsersPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      { 
        path: 'map', 
        name: 'map', 
        component: () => import('pages/MapPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      { 
        path: 'performance', 
        name: 'performance', 
        component: () => import('pages/PerformancePage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      { 
        path: 'reports', 
        name: 'reports', 
        component: () => import('pages/ReportsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      {
        path: 'costs',
        name: 'costs',
        component: () => import('pages/CostsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      {
        path: 'parts',
        name: 'parts',
        component: () => import('pages/PartsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      {
        path: 'inventory-items',
        name: 'inventory-items',
        component: () => import('pages/InventoryItemsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      { 
       path: 'feedback', 
       name: 'feedback', 
       component: () => import('pages/FeedbackPage.vue'),
        meta: { requiresAuth: true, roles: ['admin', 'cliente_demo', 'cliente_ativo'] } 

      },
      { 
        path: 'inventory/item/:id', 
        name: 'item-details', 
        component: () => import('pages/ItemDetailsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      {
        path: 'implements',
        name: 'implements',
        component: () => import('pages/ImplementsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      { 
        path: 'live-map', 
        component: () => import('pages/LiveMapPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      { 
        path: 'freight-orders', 
        component: () => import('pages/FreightOrdersPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      { 
        path: 'clients', 
        component: () => import('pages/ClientsPage.vue'),
        meta: { roles: ['cliente_ativo', 'cliente_demo'] }
      },
      { 
        path: 'settings', 
        name: 'settings', 
        component: () => import('pages/SettingsPage.vue'),
        // Corrigido para 'admin' minúsculo
        meta: { roles: ['cliente_ativo', 'cliente_demo', 'admin', 'driver'] } 
      },
      {
        path: 'admin',
        name: 'admin',
        component: () => import('pages/AdminPage.vue'),
        // Corrigido para 'admin' minúsculo
        meta: { requiresAuth: true, roles: ['admin'] } 
      },
    ],
  },
  {
    path: '/auth',
    component: () => import('layouts/BlankLayout.vue'),
    children: [
      { path: 'login', name: 'login', component: () => import('pages/LoginPage.vue') },
      { path: 'register', name: 'register', component: () => import('pages/RegisterPage.vue') },
      { 
        path: 'forgot-password', 
        name: 'forgot-password', 
        component: () => import('pages/ForgotPasswordPage.vue') 
      },
      { 
        path: 'reset-password', 
        name: 'reset-password', 
        component: () => import('pages/ResetPasswordPage.vue') 
      }
    ],
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;