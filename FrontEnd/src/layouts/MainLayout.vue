<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>TruCar</q-toolbar-title>
        
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
                <q-item class="q-pl-none"><q-item-section avatar style="min-width: 30px"><q-icon name="local_shipping" /></q-item-section><q-item-section>Veículos: {{ demoStore.stats?.vehicle_count }} / {{ demoStore.stats?.vehicle_limit }}</q-item-section></q-item>
                <q-item class="q-pl-none"><q-item-section avatar style="min-width: 30px"><q-icon name="engineering" /></q-item-section><q-item-section>Motoristas: {{ demoStore.stats?.driver_count }} / {{ demoStore.stats?.driver_limit }}</q-item-section></q-item>
                <q-item class="q-pl-none"><q-item-section avatar style="min-width: 30px"><q-icon name="route" /></q-item-section><q-item-section>Jornadas este mês: {{ demoStore.stats?.journey_count }} / {{ demoStore.stats?.journey_limit }}</q-item-section></q-item>
              </q-list>
              <div>Clique para saber mais sobre o plano completo.</div>
            </div>
          </q-tooltip>
        </q-chip>

        <q-btn flat round dense icon="settings" to="/settings" class="q-mr-xs">
          <q-tooltip>Configurações</q-tooltip>
        </q-btn>
        
        <q-btn v-if="authStore.isManager" flat round dense icon="notifications" class="q-mr-sm">
          <q-badge v-if="notificationStore.unreadCount > 0" color="red" floating>{{ notificationStore.unreadCount }}</q-badge>
          <q-menu @show="notificationStore.fetchNotifications()" style="width: 350px">
            <q-list bordered separator><q-item-label header>Notificações</q-item-label></q-list>
          </q-menu>
        </q-btn>
        
        <q-btn-dropdown flat :label="authStore.user?.full_name || 'Usuário'">
          <q-list>
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

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-scroll-area class="fit">
        <q-list padding>
          <q-item-label header>Menu Principal</q-item-label>
          <q-item v-for="link in essentialLinks" :key="link.title" clickable :to="link.to" exact v-ripple>
            <q-item-section avatar><q-icon :name="link.icon" /></q-item-section>
            <q-item-section><q-item-label>{{ link.title }}</q-item-label></q-item-section>
          </q-item>
          <div v-if="authStore.isSuperuser">
            <q-separator class="q-my-md" />
            <q-item-label header>Administração</q-item-label>
            <q-item clickable to="/admin" exact v-ripple>
              <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
              <q-item-section><q-item-label>Painel Admin</q-item-label></q-item-section>
            </q-item>
          </div>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-page-container><router-view /></q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'stores/auth-store';
import { useNotificationStore } from 'stores/notification-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { useDemoStore } from 'stores/demo-store';

const leftDrawerOpen = ref(false);
const router = useRouter();
const $q = useQuasar();
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

const isDemo = computed(() => authStore.user?.role === 'cliente_demo');

function showUpgradeDialog() {
  $q.dialog({
    title: 'Desbloqueie o Potencial Máximo do TruCar',
    message: 'Para liberar recursos avançados como relatórios detalhados e cadastro ilimitado de veículos e motoristas, entre em contato com nossa equipe comercial.',
    ok: { label: 'Entendido', color: 'primary', unelevated: true },
    persistent: true
  });
}

const essentialLinks = computed(() => {
  const baseLinks = [
    { title: 'Dashboard', icon: 'dashboard', to: '/dashboard' },
    { title: 'Mapa em Tempo Real', icon: 'map', to: '/live-map' },
  ];

  const sectorLinks = [];
  const sector = authStore.userSector;
  const isManager = authStore.isManager;

  if (sector === 'agronegocio' || sector === 'servicos') {
    sectorLinks.push(
      { title: terminologyStore.vehiclePageTitle, icon: sector === 'agronegocio' ? 'agriculture' : 'local_shipping', to: '/vehicles' },
      { title: terminologyStore.journeyPageTitle, icon: 'route', to: '/journeys' }
    );
    if (sector === 'agronegocio') {
      sectorLinks.push({ title: 'Implementos', icon: 'precision_manufacturing', to: '/implements' });
    }
  } 
  else if (sector === 'frete') {
    if (isManager) {
      sectorLinks.push(
        { title: 'Ordens de Frete', icon: 'list_alt', to: '/freight-orders' },
        { title: 'Gerenciamento de Frota', icon: 'local_shipping', to: '/vehicles' },
        { title: 'Clientes', icon: 'groups', to: '/clients' }
      );
    } else {
      sectorLinks.push(
        { title: 'Minha Rota', icon: 'explore', to: '/driver-cockpit' }
      );
    }
  }

  const commonLinks = [
    { title: 'Ranking de Motoristas', icon: 'leaderboard', to: '/performance' },
    { title: 'Relatórios', icon: 'summarize', to: '/reports' },
    { title: 'Manutenções', icon: 'build', to: '/maintenance' },
  ];

  const managerLinks = [];
  if (isManager) {
    managerLinks.push({
      title: 'Gestão de Utilizadores',
      icon: 'manage_accounts',
      to: '/users',
    });
  }

  return [...baseLinks, ...sectorLinks, ...commonLinks, ...managerLinks];
});

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
:deep(.q-drawer) {
  background: #1a1616;
}
.q-drawer .q-list .q-item {
  color: $grey-2;
  .q-item__section--avatar {
    color: $grey-2;
  }
}
.q-drawer .q-list .q-item.q-router-link--active {
  color: $primary;
  font-weight: 600;
  background-color: rgba($primary, 0.1);
  border-left: 4px solid $primary;
  .q-item__section--avatar {
    color: $primary;
  }
}
</style>