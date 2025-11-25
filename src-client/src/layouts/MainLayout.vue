<template>
  <q-layout view="lHh LpR lFf" class="main-layout-container">
    
    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="app-sidebar"
      :width="260"
      :breakpoint="700"
    >
      <q-scroll-area class="fit">
        <div class="q-pa-md row items-center justify-center sidebar-header" style="height: 80px;">
          <img src="~assets/trucar-logo-dark.png" class="logo-light-theme" style="height: 32px; max-width: 100%;" alt="TruCar Logo">
          <img src="~assets/trucar-logo-white.png" class="logo-dark-theme" style="height: 32px; max-width: 100%;" alt="TruCar Logo">
        </div>
        
        <q-separator class="q-mb-md q-mx-md" />

        <q-list padding class="q-px-sm">
          <template v-for="category in menuStructure" :key="category.label">
            
            <q-expansion-item
              v-if="category.children.length > 0"
              :icon="category.icon"
              :label="category.label"
              expand-separator
              default-opened
              header-class="text-weight-medium text-grey-8 nav-header"
              class="q-mb-sm overflow-hidden rounded-borders"
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
                <q-item-section avatar style="min-width: 40px;">
                  <q-icon :name="link.icon" size="20px" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ link.title }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-expansion-item>

          </template>

          <div v-if="authStore.isSuperuser">
            <q-separator class="q-my-md" />
            <div class="text-caption text-grey-6 q-px-md q-mb-sm text-uppercase text-weight-bold">Sistema</div>
            <q-item clickable to="/admin" exact v-ripple class="nav-link" active-class="nav-link--active">
              <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
              <q-item-section>
                <q-item-label>Painel Admin</q-item-label>
                <q-item-label caption>Superusuário</q-item-label>
              </q-item-section>
            </q-item>
            <q-item clickable tag="a" to="/feedback">
              <q-item-section avatar>
                <q-icon name="feedback" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Feedback / Suporte</q-item-label>
                <q-item-label caption>Reportar erros</q-item-label>
              </q-item-section>
            </q-item>
          </div>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-header bordered class="main-header">
      <q-toolbar style="height: 64px;">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" class="lt-md text-grey-8" />
        
        <q-toolbar-title class="lt-md text-grey-8 text-weight-bold">
          TruCar
        </q-toolbar-title>

        <q-space />

        <div class="row q-gutter-sm items-center">
          <q-btn flat round dense icon="settings" to="/settings" class="text-grey-7">
            <q-tooltip>Configurações</q-tooltip>
          </q-btn>
          
          <q-btn v-if="authStore.isManager" flat round dense icon="notifications" class="text-grey-7 q-mr-sm">
            <q-badge v-if="notificationStore.unreadCount > 0" color="red" floating rounded>{{ notificationStore.unreadCount }}</q-badge>
            <q-menu @show="notificationStore.fetchNotifications()" fit anchor="bottom left" self="top right" :offset="[0, 10]" style="width: 350px; max-width: 90vw;">
              <div class="row no-wrap items-center q-pa-md  bb-1">
                <div class="text-subtitle1 text-weight-bold">Notificações</div>
                <q-space />
                <q-spinner v-if="notificationStore.isLoading" color="primary" size="1.2em" />
              </div>

              <q-scroll-area style="height: 300px;">
                <div v-if="!notificationStore.isLoading && notificationStore.notifications.length === 0" class="column flex-center q-pa-lg text-grey-5">
                  <q-icon name="notifications_none" size="4em" />
                  <div class="q-mt-sm">Tudo limpo por aqui!</div>
                </div>
                
                <q-list separator class="q-pa-none">
                  <q-item
                    v-for="notification in notificationStore.notifications"
                    :key="notification.id"
                    clickable
                    v-ripple
                    class="q-py-md"
                    :class="{ 'bg-blue-1': !notification.is_read }"
                    @click="handleNotificationClick(notification)"
                  >
                    <q-item-section avatar>
                      <q-avatar :icon="getNotificationIcon(notification.notification_type)" :color="notification.is_read ? 'grey-3' : 'white'" :text-color="notification.is_read ? 'grey-7' : 'primary'" size="md" />
                    </q-item-section>

                    <q-item-section>
                      <q-item-label class="text-body2">{{ notification.message }}</q-item-label>
                      <q-item-label caption class="q-mt-xs text-grey-6">{{ formatNotificationDate(notification.created_at) }}</q-item-label>
                    </q-item-section>

                    <q-item-section side top>
                      <div v-if="!notification.is_read" class="bg-primary rounded-borders" style="width: 8px; height: 8px; border-radius: 50%;"></div>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-scroll-area>
            </q-menu>
          </q-btn>

          <q-btn-dropdown flat no-caps class="text-grey-8 profile-btn" content-class="profile-menu">
            <template v-slot:label>
              <div class="row items-center no-wrap">
                <q-avatar size="36px" color="primary" text-color="white" class="q-mr-sm shadow-1">
                  {{ getUserInitials(authStore.user?.full_name) }}
                </q-avatar>
                <div class="text-left gt-xs">
                  <div class="text-weight-bold" style="line-height: 1.1;">{{ firstName(authStore.user?.full_name) }}</div>
                  <div class="text-caption text-grey-6" style="line-height: 1;">{{ roleLabel }}</div>
                </div>
              </div>
            </template>

            <div class="row no-wrap q-pa-md">
              <div class="column">
                <div class="text-h6 q-mb-xs">Conta</div>
                <q-list dense>
                  <q-item clickable v-close-popup :to="`/users/${authStore.user?.id}/stats`" v-if="authStore.isDriver">
                    <q-item-section avatar style="min-width: 30px;"><q-icon name="query_stats" size="xs" /></q-item-section>
                    <q-item-section>Minhas Estatísticas</q-item-section>
                  </q-item>
                  <q-item clickable v-close-popup to="/settings">
                    <q-item-section avatar style="min-width: 30px;"><q-icon name="settings" size="xs" /></q-item-section>
                    <q-item-section>Configurações</q-item-section>
                  </q-item>
                </q-list>
              </div>

              <q-separator vertical inset class="q-mx-lg" />

              <div class="column items-center justify-center">
                <q-avatar size="72px" color="primary" text-color="white" class="q-mb-sm">
                    {{ getUserInitials(authStore.user?.full_name) }}
                </q-avatar>
                <div class="text-subtitle1 q-mt-sm text-center">{{ authStore.user?.full_name }}</div>
                <div class="text-caption text-grey q-mb-sm">{{ authStore.user?.email }}</div>
                <q-btn
                  color="primary"
                  label="Sair"
                  push
                  size="sm"
                  v-close-popup
                  @click="handleLogout"
                />
              </div>
            </div>
          </q-btn-dropdown>
        </div>
      </q-toolbar>
      
      <q-banner v-if="authStore.isImpersonating" inline-actions class="bg-deep-orange text-white text-center shadow-2 dense">
         <template v-slot:avatar>
           <q-icon name="visibility" color="white" size="sm" />
         </template>
         <span class="text-weight-medium text-caption">
           Visualizando como: <strong>{{ authStore.user?.full_name }}</strong>
         </span>
         <template v-slot:action>
           <q-btn flat dense size="sm" label="Encerrar Sessão" @click="authStore.stopImpersonation()" />
         </template>
      </q-banner>
    </q-header>

    <q-page-container class="app-page-container">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/auth-store';
import { useNotificationStore } from 'stores/notification-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { useDemoStore } from 'stores/demo-store';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import type { Notification } from 'src/models/notification-models';

const leftDrawerOpen = ref(false);
const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const terminologyStore = useTerminologyStore();
const demoStore = useDemoStore();

let pollTimer: number;

function toggleLeftDrawer() { leftDrawerOpen.value = !leftDrawerOpen.value; }

function handleLogout() {
  if (authStore.isImpersonating) {
    authStore.stopImpersonation();
  } else {
    authStore.logout();
    void router.push('/auth/login');
  }
}

// Helpers de Interface
// --- CORREÇÃO DE TYPESCRIPT ---
function getUserInitials(name: string | undefined): string {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length === 0) return 'U';
    
    // Usamos verificação explícita em vez de acesso direto ao índice
    const first = parts[0];
    const last = parts[parts.length - 1];
    
    // Se tivermos primeiro e último, retornamos as iniciais
    if (first && last) {
        return (first.charAt(0) + last.charAt(0)).toUpperCase();
    }
    
    // Fallback se só tiver o primeiro
    if (first) {
        return first.substring(0, 2).toUpperCase();
    }
    
    return 'U';
}

function firstName(name: string | undefined) {
    return name ? name.split(' ')[0] : 'Usuário';
}

const roleLabel = computed(() => {
    if (authStore.isManager) return 'Gestor';
    if (authStore.isDriver) return 'Motorista';
    if (authStore.isSuperuser) return 'Admin';
    return 'Colaborador';
});

const isDemo = computed(() => authStore.isDemo);

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
  // Roteamento inteligente
  const routes: Record<string, string> = {
      'maintenance_request': '/maintenance',
      'document_expiring': '/documents',
      'new_fine_registered': '/fines',
      'low_stock': '/inventory-items', 
      'journey_started': '/journeys',
      'journey_ended': '/journeys'
  };
  
  // CORREÇÃO: Garante que a chave é válida ou usa string vazia
  const targetKey = notification.related_entity_type || notification.notification_type;
  const target = routes[targetKey || ''];
  
  if (target) void router.push(target);
}

// --- Definição do Menu ---
const menuStructure = computed(() => {
    if (authStore.isManager) return getManagerMenu();
    if (authStore.isDriver) return getDriverMenu();
    return [];
});

interface MenuItem { title: string; icon: string; to: string; }
interface MenuCategory { label: string; icon: string; children: MenuItem[]; }

function getDriverMenu(): MenuCategory[] {
    const sector = authStore.userSector;
    const menu: MenuCategory[] = [
        {
            label: 'Meu Painel', icon: 'dashboard',
            children: [{ title: 'Visão Geral', icon: 'space_dashboard', to: '/dashboard' }]
        }
    ];

    // CORREÇÃO: Verificação de segurança ao acessar menu[0]
    if (sector === 'frete' && menu.length > 0) {
        menu[0].children.push({ title: 'Cockpit de Viagem', icon: 'airline_seat_recline_normal', to: '/driver-cockpit' });
    }

    menu.push({
        label: 'Minhas Operações', icon: 'work',
        children: [
            { title: terminologyStore.journeyPageTitle, icon: 'route', to: '/journeys' },
            { title: 'Abastecimentos', icon: 'local_gas_station', to: '/fuel-logs' },
            { title: 'Chamados', icon: 'build', to: '/maintenance' },
            { title: 'Multas', icon: 'receipt_long', to: '/fines' }
        ]
    });

    return menu;
}

function getManagerMenu(): MenuCategory[] {
  const sector = authStore.userSector;
  const menu: MenuCategory[] = [];

  // 1. Visão Geral
  menu.push({
    label: 'Monitoramento', icon: 'monitor',
    children: [
      { title: 'Dashboard', icon: 'space_dashboard', to: '/dashboard' },
      { title: 'Mapa em Tempo Real', icon: 'map', to: '/live-map' },
    ]
  });

  // 2. Operacional (Depende do Setor)
  const ops: MenuItem[] = [];
  // CORREÇÃO: Verifica se sector não é nulo antes de usar includes
  if (sector && ['agronegocio', 'servicos'].includes(sector)) {
    ops.push({ title: terminologyStore.journeyPageTitle, icon: 'route', to: '/journeys' });
  }
  if (sector === 'frete') {
    ops.push({ title: 'Ordens de Frete', icon: 'assignment', to: '/freight-orders' });
    ops.push({ title: 'Clientes', icon: 'groups', to: '/clients' });
  }
  
  if (ops.length > 0) {
      menu.push({ label: 'Operações', icon: 'alt_route', children: ops });
  }

  // 3. Gestão de Ativos (Frota, Peças)
  const assets: MenuItem[] = [
      { title: terminologyStore.vehiclePageTitle, icon: 'local_shipping', to: '/vehicles' }
  ];
  
  if (sector === 'agronegocio') {
      assets.push({ title: 'Implementos', icon: 'agriculture', to: '/implements' });
  }
  
  assets.push({ title: 'Inventário', icon: 'inventory_2', to: '/parts' });
  assets.push({ title: 'Rastreabilidade ', icon: 'qr_code', to: '/inventory-items' }); 
  
  menu.push({ label: 'Gestão de Ativos', icon: 'garage', children: assets });

  // 4. Financeiro e Administrativo
  menu.push({
      label: 'Administrativo', icon: 'people',
      children: [
          { title: 'Gestão de Custos', icon: 'attach_money', to: '/costs' },
          { title: 'Abastecimentos', icon: 'local_gas_station', to: '/fuel-logs' },
          { title: 'Documentos', icon: 'description', to: '/documents' },
          { title: 'Multas', icon: 'gavel', to: '/fines' },
          { title: 'Gestão de Usuários', icon: 'people', to: '/users' },
      ]
  });

  // 5. Inteligência
  menu.push({
      label: 'Inteligência', icon: 'analytics',
      children: [
        { title: 'Performance', icon: 'leaderboard', to: '/performance' },
        { title: 'Manutenções', icon: 'handyman', to: '/maintenance' },
        { title: 'Relatórios', icon: 'summarize', to: '/reports' },
        { title: 'feedback', icon: 'feedback', to: '/feedback' }
      ]
  });

  return menu;
}

onMounted(() => {
  if (isDemo.value) void demoStore.fetchDemoStats();
  if (authStore.isManager) {
    void notificationStore.fetchUnreadCount();
    pollTimer = window.setInterval(() => { void notificationStore.fetchUnreadCount(); }, 60000);
  }
});

onUnmounted(() => { clearInterval(pollTimer); });
</script>

<style lang="scss" scoped>
.main-layout-container {
  background-color: #f8fafc;
  .body--dark & { background-color: #0f172a; }
}

.app-sidebar {
  background-color: white;
  
  .sidebar-header {
    .logo-dark-theme { display: none; }
    .logo-light-theme { display: block; }
  }

  .nav-link {
    color: #475569;
    margin: 4px 8px;
    border-radius: 8px;
    font-size: 0.9rem;
    transition: all 0.2s ease;

    &--active {
      background-color: #eff6ff;
      color: $primary;
      font-weight: 600;
      box-shadow: inset 4px 0 0 0 $primary;
    }

    &:hover:not(.nav-link--active) {
      background-color: #f1f5f9;
      color: #1e293b;
    }
  }
}

/* Ajustes Dark Mode */
.body--dark {
  .app-sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;

    .sidebar-header {
      .logo-dark-theme { display: block; }
      .logo-light-theme { display: none; }
    }

    .nav-header { color: #94a3b8 !important; }

    .nav-link {
      color: #cbd5e1;
      &--active {
        background-color: rgba($primary, 0.2);
        color: #60a5fa;
        box-shadow: inset 4px 0 0 0 #60a5fa;
      }
      &:hover:not(.nav-link--active) {
        background-color: rgba(255, 255, 255, 0.473);
      }
    }
  }
  
  .main-header {
    background-color: #1e293b !important;
    border-bottom: 1px solid #334155;
    color: #e2e8f0 !important;
  }
}

.main-header {
  background-color: white;
  color: #334155;
  border-bottom: 1px solid #e2e8f0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.bb-1 { border-bottom: 1px solid #e0e0e0; }
</style>