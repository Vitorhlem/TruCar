<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />
        <q-toolbar-title>
          TruCar
        </q-toolbar-title>
        
        <q-btn v-if="authStore.isManager" flat round dense icon="notifications" class="q-mr-sm">
          <q-badge v-if="notificationStore.unreadCount > 0" color="red" floating>
            {{ notificationStore.unreadCount }}
          </q-badge>
          <q-menu @show="notificationStore.fetchNotifications()" style="width: 350px">
            <q-list bordered separator>
              <q-item-label header>Notificações</q-item-label>
              <!-- Lógica de notificações aqui -->
            </q-list>
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

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-scroll-area class="fit">
        <!-- O erro de sintaxe foi removido daqui -->
        <q-list padding>
          <q-item-label header>Menu Principal</q-item-label>
          
          <!-- O v-for agora renderizará todos os links, incluindo o mapa -->
          <q-item
            v-for="link in essentialLinks"
            :key="link.title"
            clickable
            :to="link.to"
            exact
            v-ripple
          >
            <q-item-section avatar>
              <q-icon :name="link.icon" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ link.title }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import { useNotificationStore } from 'stores/notification-store';

const leftDrawerOpen = ref(false);
const router = useRouter();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();
const notificationStore = useNotificationStore();

let pollTimer: number;

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function handleLogout() {
  authStore.logout();
  void router.push('/auth/login');
}

const essentialLinks = computed(() => {
  const links = [
    {
      title: 'Dashboard',
      icon: 'dashboard',
      to: '/dashboard',
    },
    // --- INÍCIO DA CORREÇÃO ---
    // Adicionamos o "Mapa em Tempo Real" aqui, na lista dinâmica.
    {
      title: 'Mapa em Tempo Real',
      icon: 'map',
      to: '/live-map',
    },
    // --- FIM DA CORREÇÃO ---
    {
      title: terminologyStore.vehiclePageTitle,
      icon: authStore.userSector === 'agronegocio' ? 'agriculture' : 'local_shipping',
      to: '/vehicles',
    },
    {
      title: terminologyStore.journeyPageTitle,
      icon: 'route',
      to: '/journeys',
    },
    {
      title: 'Ranking de Motoristas',
      icon: 'leaderboard',
      to: '/performance',
    },
    {
      title: 'Manutenções',
      icon: 'build',
      to: '/maintenance',
    },
    {
      title: 'Implementos',
      icon: 'precision_manufacturing',
      to: '/implements',
    },
  ];

  if (authStore.isManager) {
    links.push({
      title: 'Gestão de Utilizadores',
      icon: 'manage_accounts',
      to: '/users',
    });
  }

  return links;
});

onMounted(() => {
  if (authStore.isManager) {
    void notificationStore.fetchUnreadCount();
    pollTimer = window.setInterval(() => {
      void notificationStore.fetchUnreadCount();
    }, 60000);
  }
});

onUnmounted(() => {
  clearInterval(pollTimer);
});
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