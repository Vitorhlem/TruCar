<template>
  <q-layout view="lHh LpR lFf" class="main-layout-container">
    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="app-sidebar"
      :width="280"
    >
      <q-scroll-area class="fit">
        <div class="q-pa-md text-center sidebar-header">
          <img src="~assets/trucar-logo-white.png" class="logo-dark-theme" style="height: 35px;" alt="TruCar Logo">
          <img src="~assets/trucar-logo-dark.png" class="logo-light-theme" style="height: 35px;" alt="TruCar Logo">
        </div>
        
        <q-list padding>
          <template v-for="category in menuStructure" :key="category.label">
            <q-expansion-item
              :icon="category.icon"
              :label="category.label"
              expand-separator
              default-opened
              header-class="text-weight-bold"
              class="nav-category"
            >
              <q-item
                v-for="link in category.children"
                :key="link.title"
                clickable
                :to="link.to"
                exact
                v-ripple
                class="nav-link"
                active-class="nav-link--active"
              >
                <q-item-section avatar><q-icon :name="link.icon" size="sm" /></q-item-section>
                <q-item-section><q-item-label>{{ link.title }}</q-item-label></q-item-section>
              </q-item>
            </q-expansion-item>
          </template>

          <div v-if="authStore.isSuperuser">
            <q-separator class="q-my-md" />
            <q-item clickable to="/admin" exact v-ripple class="nav-link" active-class="nav-link--active">
              <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
              <q-item-section>
                <q-item-label>Painel Admin</q-item-label>
                <q-item-label caption>Gerir sistema</q-item-label>
              </q-item-section>
            </q-item>
          </div>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-header bordered class="main-header">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" class="lt-md" />
        <q-space />

        <q-chip
          v-if="isDemo"
          clickable @click="showUpgradeDialog"
          color="amber" text-color="black"
          icon="workspace_premium" label="Plano Demo"
          class="q-mr-sm cursor-pointer" size="sm"
        >
          <q-tooltip class="bg-black text-body2" :offset="[10, 10]">
            <div>
              <div class="text-weight-bold">Limites do Plano de Demonstração</div>
              <q-list dense>
                <q-item class="q-pl-none">
                  <q-item-section avatar style="min-width: 30px"><q-icon name="local_shipping" /></q-item-section>
                  <q-item-section>Veículos: {{ stats?.vehicle_count ?? 0 }} / {{ formatLimit(authStore.user?.organization?.vehicle_limit) }}</q-item-section>
                </q-item>
                <q-item class="q-pl-none">
                  <q-item-section avatar style="min-width: 30px"><q-icon name="engineering" /></q-item-section>
                  <q-item-section>Motoristas: {{ stats?.driver_count ?? 0 }} / {{ formatLimit(authStore.user?.organization?.driver_limit) }}</q-item-section>
                </q-item>
                <q-item class="q-pl-none">
                  <q-item-section avatar style="min-width: 30px"><q-icon name="route" /></q-item-section>
                  <q-item-section>Jornadas este mês: {{ stats?.journey_count ?? 0 }} / {{ formatLimit(authStore.user?.organization?.freight_order_limit) }}</q-item-section>
                </q-item>
              </q-list>
              <div>Clique para saber mais sobre o plano completo.</div>
            </div>
          </q-tooltip>
        </q-chip>

        <q-btn flat round dense icon="settings" to="/settings" class="q-mr-xs toolbar-icon-btn">
          <q-tooltip>Configurações</q-tooltip>
        </q-btn>
        
        <q-btn v-if="authStore.isManager" flat round dense icon="notifications" class="q-mr-sm toolbar-icon-btn">
          <q-badge v-if="notificationStore.unreadCount > 0" color="red" floating>{{ notificationStore.unreadCount }}</q-badge>
          <q-menu @show="notificationStore.fetchNotifications()" style="width: 380px; max-height: 500px;">
            <q-list separator>
              <q-item-label header class="flex justify-between items-center">
                <span>Notificações</span>
                <q-spinner v-if="notificationStore.isLoading" color="primary" size="1.2em" />
              </q-item-label>

              <q-scroll-area style="height: 350px;">
                <div v-if="!notificationStore.isLoading && notificationStore.notifications.length === 0" class="text-center text-grey q-pa-lg">
                  <q-icon name="notifications_off" size="3em" />
                  <div>Nenhuma notificação por aqui.</div>
                </div>
                
                <q-item
                  v-for="notification in notificationStore.notifications"
                  :key="notification.id"
                  clickable
                  v-ripple
                  :class="{ 'bg-blue--1': !notification.is_read }"
                  @click="handleNotificationClick(notification)"
                >
                  <q-item-section avatar>
                    <q-avatar :icon="getNotificationIcon(notification.notification_type)" :color="notification.is_read ? 'grey-5' : 'primary'" text-color="white" size="md" />
                  </q-item-section>

                  <q-item-section>
                    <q-item-label lines="2">{{ notification.message }}</q-item-label>
                    <q-item-label caption>{{ formatNotificationDate(notification.created_at) }}</q-item-label>
                  </q-item-section>

                  <q-item-section side top>
                    <q-badge v-if="!notification.is_read" color="blue" label="Nova" rounded />
                  </q-item-section>
                </q-item>
              </q-scroll-area>
            </q-list>
          </q-menu>
        </q-btn>

        <q-btn-dropdown flat :label="authStore.user?.full_name || 'Usuário'">
          <q-list>
            <q-item clickable v-close-popup :to="`/users/${authStore.user?.id}/stats`" v-if="authStore.isDriver">
                <q-item-section avatar><q-icon name="query_stats" /></q-item-section>
                <q-item-section>Minhas Estatísticas</q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="handleLogout">
              <q-item-section avatar><q-icon name="logout" /></q-item-section>
              <q-item-section>Sair</q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
      
      <q-banner v-if="authStore.isImpersonating" inline-actions class="bg-deep-orange text-white text-center shadow-2">
         <template v-slot:avatar>
           <q-icon name="visibility_off" color="white" />
         </template>
         <div class="text-weight-medium">
           A visualizar como {{ authStore.user?.full_name }}. (Sessão de Administrador em pausa)
         </div>
         <template v-slot:action>
           <q-btn flat dense color="white" label="Voltar à minha conta" @click="authStore.stopImpersonation()" />
         </template>
      </q-banner>
    </q-header>

    <q-page-container class="app-page-container">
      <router-view v-slot="{ Component }">
        <transition name="route-transition" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { storeToRefs } from 'pinia';
import { useAuthStore } from 'stores/auth-store';
import { useNotificationStore } from 'stores/notification-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { useDemoStore } from 'stores/demo-store';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import type { Notification } from 'src/models/notification-models';

// --- Inicialização ---
const leftDrawerOpen = ref(false);
const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const terminologyStore = useTerminologyStore();
const demoStore = useDemoStore();

const { stats } = storeToRefs(demoStore);

let pollTimer: number;

// --- Tipos ---
interface MenuItem {
  title: string;
  icon: string;
  to: string;
} 

interface MenuCategory {
  label: string;
  icon: string;
  children: MenuItem[];
}

// --- Ações ---
function toggleLeftDrawer() { leftDrawerOpen.value = !leftDrawerOpen.value; }

function handleLogout() {
  if (authStore.isImpersonating) {
    authStore.stopImpersonation();
  } else {
    authStore.logout();
    void router.push('/auth/login');
  }
}

const isDemo = computed(() => authStore.isDemo);

function showUpgradeDialog() {
  $q.dialog({
    title: 'Desbloqueie o Potencial Máximo do TruCar',
    message: 'Para liberar recursos avançados como relatórios detalhados e cadastro ilimitado de veículos e motoristas, entre em contato com nossa equipe comercial.',
    ok: { label: 'Entendido', color: 'primary', unelevated: true },
    persistent: false
  });
}

// --- Formatadores ---
function formatLimit(limit: number | undefined | null): string {
  if (limit === undefined || limit === null) {
    return '--';
  }
  if (limit < 0) {
    return 'Ilimitado';
  }
  return limit.toString();
}

function formatNotificationDate(date: string) {
  return formatDistanceToNow(new Date(date), { addSuffix: true, locale: ptBR });
}

function getNotificationIcon(type: string): string {
  const iconMap: Record<string, string> = {
    'maintenance_due_date': 'event_busy',
    'maintenance_due_km': 'speed',
    'maintenance_request_new': 'build',
    'new_fine_registered': 'receipt_long',
    'document_expiring': 'badge',
    'low_stock': 'inventory_2',
    'journey_started': 'play_arrow',
    'journey_ended': 'stop',
  };
  return iconMap[type] || 'notifications';
}

async function handleNotificationClick(notification: Notification) {
  if (!notification.is_read) {
    await notificationStore.markAsRead(notification.id);
  }
  
  if (notification.related_entity_type === 'maintenance_request') {
    void router.push('/maintenance');
  } 
  else if (notification.notification_type === 'document_expiring') {
      void router.push('/documents');
  }
  else if (notification.notification_type === 'new_fine_registered') {
      void router.push('/fines');
  }
  else if (notification.notification_type === 'low_stock') {
      void router.push('/parts');
  }
  // --- ADICIONADO: Tratamento para jornadas ---
  else if (['journey_started', 'journey_ended'].includes(notification.notification_type)) {
      void router.push('/journeys');
  }
  // ------------------------------------------
  else {
      console.log('Notificação sem rota específica:', notification.notification_type);
      // Fallback opcional: void router.push('/dashboard');
  }
}

// --- Estrutura do Menu ---
const menuStructure = computed(() => {
    if (authStore.isManager) {
        return getManagerMenu();
    }
    if (authStore.isDriver) {
        return getDriverMenu();
    }
    return [];
});

function getDriverMenu(): MenuCategory[] {
    const sector = authStore.userSector;
    const menu: MenuCategory[] = [];

    const general: MenuCategory = {
        label: 'Principal',
        icon: 'dashboard',
        children: [
            { title: 'Dashboard', icon: 'dashboard', to: '/dashboard' },
            { title: 'Mapa em Tempo Real', icon: 'public', to: '/live-map' },
        ],
    };
    if (sector === 'frete') {
        general.children.push({ title: 'Minha Rota', icon: 'explore', to: '/driver-cockpit' });
    }
    menu.push(general);

    const operations: MenuCategory = {
        label: 'Minhas Atividades',
        icon: 'work_history',
        children: [
            { title: terminologyStore.journeyPageTitle, icon: 'route', to: '/journeys' },
            { title: 'Abastecimentos', icon: 'local_gas_station', to: '/fuel-logs' },
            { title: 'Minhas Multas', icon: 'receipt_long', to: '/fines' },
            { title: 'Manutenções', icon: 'build', to: '/maintenance' },
        ],
    };
    menu.push(operations);

    const fleet: MenuCategory = {
        label: 'Frota',
        icon: 'local_shipping',
        children: [
            { title: terminologyStore.vehiclePageTitle, icon: 'local_shipping', to: '/vehicles' }
        ]
    };
    menu.push(fleet);

    return menu;
}

function getManagerMenu(): MenuCategory[] {
  const sector = authStore.userSector;
  const menu: MenuCategory[] = [];

  const general: MenuCategory = {
    label: 'Geral', icon: 'dashboard',
    children: [
      { title: 'Dashboard', icon: 'dashboard', to: '/dashboard' },
      { title: 'Mapa em Tempo Real', icon: 'map', to: '/live-map' },
    ]
  };
  menu.push(general);

  const operations: MenuCategory = { label: 'Operações', icon: 'alt_route', children: [] as MenuItem[] };
  if (sector === 'agronegocio' || sector === 'servicos') {
    operations.children.push({ title: terminologyStore.journeyPageTitle, icon: 'route', to: '/journeys' });
  }
  if (sector === 'frete') {
    operations.children.push({ title: 'Ordens de Frete', icon: 'list_alt', to: '/freight-orders' });
  }
  if (operations.children.length > 0) {
    menu.push(operations);
  }

  const management: MenuCategory = { label: 'Gestão', icon: 'settings_suggest', children: [] as MenuItem[] };
  if (sector === 'agronegocio' || sector === 'servicos' || sector === 'frete') {
    management.children.push({ title: terminologyStore.vehiclePageTitle, icon: 'local_shipping', to: '/vehicles' });
  }
  if (sector === 'agronegocio') {
    management.children.push({ title: 'Implementos', icon: 'precision_manufacturing', to: '/implements' });
  }
  if (sector === 'frete') {
    management.children.push({ title: 'Clientes', icon: 'groups', to: '/clients' });
  }
  management.children.push({ title: 'Gestão de Utilizadores', icon: 'manage_accounts', to: '/users' });
  management.children.push({ title: 'Inventário', icon: 'inventory_2', to: '/parts' });
  management.children.push({ title: 'Rastreabilidade', icon: 'manage_search', to: '/inventory-items' });

  management.children.push({ title: 'Gestão de Custos', icon: 'monetization_on', to: '/costs' });
  management.children.push({ title: 'Abastecimentos', icon: 'local_gas_station', to: '/fuel-logs' });
  management.children.push({ title: 'Documentos', icon: 'folder_shared', to: '/documents' });
  
  if (management.children.length > 0) {
    menu.push(management);
  }

  const analysis: MenuCategory = {
  label: 'Análise', icon: 'analytics',
  children: [
    { title: 'Ranking de Motoristas', icon: 'leaderboard', to: '/performance' },
    { title: 'Relatórios', icon: 'summarize', to: '/reports' },
    { title: 'Manutenções', icon: 'build', to: '/maintenance' },
    { title: 'Gestão de Multas', icon: 'receipt_long', to: '/fines' },
  ]
  };
  menu.push(analysis);

  return menu;
}

// --- Lifecycle ---
onMounted(() => {
  if (isDemo.value) {
    void demoStore.fetchDemoStats();
  }
  if (authStore.isManager) {
    void notificationStore.fetchUnreadCount();
    pollTimer = window.setInterval(() => { void notificationStore.fetchUnreadCount(); }, 60000);
  }
});

onUnmounted(() => { clearInterval(pollTimer); });
</script>

<style lang="scss" scoped>
.main-layout-container {
  background-color: #f4f6f9;
  
  .body--dark & {
    background-color: #121212;
  }
}

.app-sidebar {
  background-color: #ffffff;
  border-right: 1px solid #e0e0e0;

  .sidebar-header {
    .logo-dark-theme { display: none; }
    .logo-light-theme { display: block; }
  }

  .nav-category {
    .q-item__section--avatar { color: $grey-7; }
    .q-item__label {
      color: $grey-9;
      font-weight: 500;
    }
  }

  .nav-link {
    color: #333333;
    margin: 4px 12px;
    border-radius: 8px;
    transition: all 0.2s ease-in-out;
    font-weight: 500;

    .q-item__section--avatar { color: $grey-8; }

    &--active {
      background-color: rgba($primary, 0.1);
      color: $primary;
      font-weight: 600;

      .q-item__section--avatar { color: $primary; }
    }

    &:hover:not(.nav-link--active) {
      background-color: rgba(0, 0, 0, 0.05);
    }
  }
}

.body--dark .app-sidebar {
  background-color: #1d2d35;
  border-right-color: #2d3748;
  color: #aeb9c6;

  .sidebar-header {
    .logo-dark-theme { display: block; }
    .logo-light-theme { display: none; }
  }

  .nav-category {
    .q-item__section--avatar { color: #9ca3af; }
    .q-item__label { color: white; }
  }
  
  .nav-link {
    color: #d1d5db;

    &--active {
      background-color: $primary;
      color: white;
      box-shadow: 0 4px 10px rgba($primary, 0.3);

      .q-item__section--avatar { color: white; }
    }

    &:hover:not(.nav-link--active) {
      background-color: rgba(255, 255, 255, 0.05);
    }
  }
}

.main-header {
  background-color: white;
  color: $grey-9;

  .body--dark & {
    background-color: #1d2d35;
    border-bottom: 1px solid #2d3748;
    color: white;
  }
}

.app-page-container {
  background-color: #f4f6f9;

  .body--dark & {
    background-color: #121212;
  }
}

.route-transition-enter-active,
.route-transition-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.route-transition-enter-from,
.route-transition-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>  