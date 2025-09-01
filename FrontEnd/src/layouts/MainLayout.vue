<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>TruCar</q-toolbar-title>
        
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
    </q-header>

    <!-- ===== BANNER DO PLANO DEMO ADICIONADO ===== -->
    <q-banner v-if="isDemoPlan" inline-actions class="bg-primary text-white shadow-2">
      <template v-slot:avatar>
        <q-icon name="workspace_premium" color="white" />
      </template>
      <div class="text-weight-medium">Você está no Plano Demo.</div>
      <template v-slot:action>
        <q-btn flat dense color="white" label="Desbloquear todos os recursos" @click="showUpgradeDialog" />
      </template>
    </q-banner>
    <!-- ===== FIM DA ADIÇÃO ===== -->

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-scroll-area class="fit">
        <q-list padding>
          <q-item-label header>Menu Principal</q-item-label>
          <q-item v-for="link in essentialLinks" :key="link.title" clickable :to="link.to" exact v-ripple>
            <q-item-section avatar><q-icon :name="link.icon" /></q-item-section>
            <q-item-section><q-item-label>{{ link.title }}</q-item-label></q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-page-container><router-view /></q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar'; // <-- ADICIONADO
import { useAuthStore } from 'stores/auth-store';
import { useNotificationStore } from 'stores/notification-store';
import { useTerminologyStore } from 'stores/terminology-store';

const leftDrawerOpen = ref(false);
const router = useRouter();
const $q = useQuasar(); // <-- ADICIONADO
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const terminologyStore = useTerminologyStore();

let pollTimer: number;

function toggleLeftDrawer() { leftDrawerOpen.value = !leftDrawerOpen.value; }
function handleLogout() { authStore.logout(); void router.push('/auth/login'); }

// --- LÓGICA DO PLANO DEMO ADICIONADA ---
const isDemoPlan = computed(() => authStore.user?.organization?.plan_status === 'demo');

function showUpgradeDialog() {
  $q.dialog({
    title: 'Desbloqueie o Potencial Máximo do TruCar',
    message: 'Para liberar recursos avançados como relatórios detalhados e cadastro ilimitado de veículos e motoristas, entre em contato com nossa equipe comercial.',
    ok: {
      label: 'Entendido',
      color: 'primary',
      unelevated: true
    },
    persistent: true
  });
}
// --- FIM DA ADIÇÃO ---

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
  if (authStore.isManager) {
    void notificationStore.fetchUnreadCount();
    pollTimer = window.setInterval(() => { void notificationStore.fetchUnreadCount(); }, 60000);
  }
});

onUnmounted(() => { clearInterval(pollTimer); });
</script>

<style lang="scss" scoped>
// Seus estilos permanecem os mesmos
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
