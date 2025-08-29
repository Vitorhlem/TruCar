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
import { useAuthStore } from 'stores/auth-store';
// import { useTerminologyStore } from 'stores/terminology-store'; // Removido pois não é usado no script
import { useNotificationStore } from 'stores/notification-store';

const leftDrawerOpen = ref(false);
const router = useRouter();
const authStore = useAuthStore();
// const terminologyStore = useTerminologyStore(); // Removido
const notificationStore = useNotificationStore();

let pollTimer: number;

function toggleLeftDrawer() { leftDrawerOpen.value = !leftDrawerOpen.value; }
function handleLogout() { authStore.logout(); void router.push('/auth/login'); }

const essentialLinks = computed(() => {
  const baseLinks = [{ title: 'Dashboard', icon: 'dashboard', to: '/dashboard' }, { title: 'Mapa em Tempo Real', icon: 'map', to: '/live-map' }];
  const sectorLinks = [];
  const sector = authStore.userSector;
  if (sector === 'agronegocio') {
    sectorLinks.push(
      { title: 'Gerenciamento de Maquinário', icon: 'agriculture', to: '/vehicles' },
      { title: 'Registro de Operações', icon: 'route', to: '/journeys' },
      { title: 'Implementos', icon: 'precision_manufacturing', to: '/implements' }
    );
  } else if (sector === 'frete') {
    sectorLinks.push(
      { title: 'Gerenciamento de Veículos', icon: 'local_shipping', to: '/vehicles' },
      { title: 'Ordens de Frete', icon: 'list_alt', to: '/freight-orders' },
      { title: 'Clientes', icon: 'groups', to: '/clients' }
    );
  } else {
    sectorLinks.push(
      { title: 'Gerenciamento de Veículos', icon: 'local_shipping', to: '/vehicles' },
      { title: 'Registro de Viagens', icon: 'route', to: '/journeys' }
    );
  }
  const commonLinks = [{ title: 'Ranking de Motoristas', icon: 'leaderboard', to: '/performance' }, { title: 'Manutenções', icon: 'build', to: '/maintenance' }];
  const managerLinks = [];
  if (authStore.isManager) {
    managerLinks.push({ title: 'Gestão de Utilizadores', icon: 'manage_accounts', to: '/users' });
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