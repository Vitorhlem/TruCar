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
        <q-list padding>
          <q-item-label header>Menu Principal</q-item-label>
          
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

// A LÓGICA "INTELIGENTE" E UNIFICADA DO MENU
const essentialLinks = computed(() => {
  // Links visíveis para TODOS os utilizadores logados
  const links = [
    {
      title: 'Dashboard',
      icon: 'dashboard',
      to: '/dashboard',
    },
    {
      title: terminologyStore.vehiclePageTitle, // Título dinâmico (Veículos vs Maquinário)
      icon: authStore.userSector === 'agronegocio' ? 'agriculture' : 'local_shipping', // Ícone dinâmico
      to: '/vehicles',
    },
    {
      title: terminologyStore.journeyPageTitle, // Título dinâmico (Viagens vs Operações)
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
      icon: 'precision_manufacturing', // Ícone de exemplo
      to: '/implements',
    },
  ];

  // Links visíveis APENAS para gestores (isManager === true)
  if (authStore.isManager) {
    links.push(
      
      {
        title: 'Gestão de Utilizadores',
        icon: 'manage_accounts',
        to: '/users',
      }
    );
  }

  return links;
});

// Busca as notificações não lidas para o gestor
onMounted(() => {
  if (authStore.isManager) {
    void notificationStore.fetchUnreadCount();
    // Verifica por novas notificações a cada 60 segundos
    pollTimer = window.setInterval(() => {
      void notificationStore.fetchUnreadCount();
    }, 60000);
  }
});

// Limpa o timer quando o componente é destruído
onUnmounted(() => {
  clearInterval(pollTimer);
});
</script>

<style lang="scss" scoped>


/*

  Usamos um seletor mais específico (:deep) para garantir que nossa regra
  de cor de fundo seja aplicada corretamente sobre os estilos padrão do Quasar.
*/
:deep(.q-drawer) {
  background: #1a1616; /* Um cinza bem claro, como exemplo */
}

.q-drawer {
  .q-list {
    .q-item {
      color: $grey-2; // Cor padrão do texto e ícone
      .q-item__section--avatar {
        color: $grey-2;
      }
    }
    .q-item.q-router-link--active {
      color: $primary; // Cor do texto e ícone quando a rota está ativa
      font-weight: 600;
      background-color: rgba($primary, 0.1);
      border-left: 4px solid $primary;

      .q-item__section--avatar {
        color: $primary;
      }
    }
  }
}

/* DEFINE A COR PADRÃO DOS ÍCONES E TEXTO DOS LINKS */
.menu-link {
  color: rgb(255, 255, 255); /* Texto e ícone com um branco semi-transparente */

  .q-item__section--avatar {
    color: rgb(255, 255, 255);
  }
}

/* O resto dos seus estilos para o link ativo, etc. */
.q-item.q-router-link--active, .q-item--active {
  background-color: rgba($primary, 0.1);
  color: $primary;
  border-left: 4px solid $primary;
}
.menu-link .q-item__section--avatar {
  color: $grey-7;
}
.q-item.q-router-link--active .q-item__section--avatar {
  color: $primary;

}

.q-item.q-router-link--active, .q-item--active {
  background-color: rgba($primary, 0.2);
  color: #ffffff; /* Texto do item ativo fica BRANCO PURO */
  font-weight: 600;
  border-left: 4px solid $primary;

  .q-item__section--avatar {
    color: rgb(255, 255, 255); /* Ícone do item ativo também fica BRANCO PURO */
  }
}


</style>