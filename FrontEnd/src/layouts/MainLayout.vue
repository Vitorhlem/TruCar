<template>
  <q-layout view="lHh LpR fFf" class="bg-grey-2">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>
          <q-avatar><q-icon name="directions_car" /></q-avatar>
          TruCar
        </q-toolbar-title>
  
        

        
 <template v-if="authStore.isManager">
            <q-separator class="q-my-md" />
            <q-item-label header class="text-weight-bold text-uppercase">Gestão</q-item-label>
            <q-item
              v-for="link in managementLinks"
              :key="link.title"
              :to="link.route"
              clickable v-ripple exact class="menu-link"
            >
              <q-item-section avatar><q-icon :name="link.icon" /></q-item-section>
              <q-item-section>{{ link.title }}</q-item-section>
            </q-item>
          </template>

         <q-space />
        <q-btn v-if="authStore.isManager" flat round dense icon="notifications" class="q-mr-sm">
          <q-badge v-if="notificationStore.unreadCount > 0" color="red" floating>
            {{ notificationStore.unreadCount }}
          </q-badge>

          <q-menu @show="notificationStore.fetchNotifications()" style="width: 350px">
            <q-list bordered separator>
              <q-item-label header>Notificações</q-item-label>
              <q-item v-if="notificationStore.isLoading" class="flex-center"><q-spinner color="primary" size="2em" /></q-item>
              <q-item v-else-if="notificationStore.notifications.length === 0"><q-item-section><q-item-label class="text-center">Nenhuma notificação</q-item-label></q-item-section></q-item>
              <q-item
                v-else
                v-for="notif in notificationStore.notifications"
                :key="notif.id"
                clickable
                v-ripple
                @click="notificationStore.markAsRead(notif.id)"
                :class="!notif.is_read ? 'bg-blue-1' : ''"
              >
                <q-item-section>
                  <q-item-label>{{ notif.message }}</q-item-label>
                  <q-item-label caption>{{ new Date(notif.created_at).toLocaleString('pt-BR') }}</q-item-label>
                </q-item-section>
                 <q-item-section v-if="!notif.is_read" side>
                    <q-badge color="primary" label="Nova" />
                 </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>

        <div v-if="authStore.user" class="q-mr-md">
          Olá, {{ authStore.user.full_name }}
        </div>
        <q-btn
          @click="handleLogout"
          flat
          round
          dense
          icon="logout"
          aria-label="Sair do Sistema"
        />
      </q-toolbar>
    </q-header>

<q-drawer show-if-above v-model="leftDrawerOpen" side="left" bordered>
      <q-scroll-area class="fit">
        <q-list padding>
          <q-item-label header class="text-weight-bold text-uppercase">Navegação</q-item-label>
          
         

        
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-drawer show-if-above v-model="leftDrawerOpen" side="left" bordered>
      <q-scroll-area class="fit">
        <q-list padding>
          <!-- SEÇÃO OPERACIONAL -->
          <q-item-label header class="text-weight-bold text-uppercase">Navegação</q-item-label>
          <q-item
            v-for="link in operationalLinks"
            :key="link.title"
            :to="link.route"
            clickable v-ripple exact class="menu-link"
          >
            <q-item-section avatar><q-icon :name="link.icon" /></q-item-section>
            <q-item-section>{{ link.title }}</q-item-section>
          </q-item>
          </q-list>
          </q-scroll-area>
          </q-drawer>
    
    <q-page-container>
 <router-view v-slot="{ Component }">
        <transition
          appear
          enter-active-class="animated fadeIn"
          leave-active-class="animated fadeOut"
          mode="out-in"
        >
          <component :is="Component" />
        </transition>
      </router-view>

      <div class="text-center q-pa-md text-caption text-grey-99">
        &copy; {{ currentYear }} Vitor H. Lemes -
        <a href="https://vytruve.org/" target="_blank" class="text-primary" style="text-decoration: none;">
          vytruve.org
        </a>
      </div>
      </q-page-container>

      

    </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useAuthStore } from 'stores/auth-store';
import { useNotificationStore } from 'stores/notification-store';
import { useVehicleStore } from 'stores/vehicle-store';
import { useJourneyStore } from 'stores/journey-store';
import { useUserStore } from 'stores/user-store';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const vehicleStore = useVehicleStore();
const journeyStore = useJourneyStore();
const userStore = useUserStore();
const router = useRouter();
const leftDrawerOpen = ref(true);
let pollTimer: number;

const currentYear = computed(() => new Date().getFullYear());

function toggleLeftDrawer() { leftDrawerOpen.value = !leftDrawerOpen.value; }
async function handleLogout() { authStore.logout(); await router.push({ name: 'login' }); }

const operationalLinks = computed(() => {
  const baseLinks = [
    { title: 'Dashboard', icon: 'dashboard', route: { name: 'dashboard' } },
  ];
  const sector = authStore.user?.organization?.sector;

  if (sector === 'agronegocio') {
    return [
      ...baseLinks,
      { title: 'Maquinário', icon: 'agriculture', route: { name: 'vehicles' } },
      { title: 'Operações de Campo', icon: 'map', route: { name: 'journeys' } },
      // Adicione outros links específicos do agronegócio aqui
    ];
  }
  
  // Links Padrão
  return [
    ...baseLinks,
    { title: 'Veículos', icon: 'local_shipping', route: { name: 'vehicles' } },
    { title: 'Viagens', icon: 'map', route: { name: 'journeys' } },
    { title: 'Manutenção', icon: 'build', route: { name: 'maintenance' } },
    { title: 'Abastecimentos', icon: 'local_gas_station', route: { name: 'fuel-logs' } },
    { title: 'Mapa da Frota', icon: 'travel_explore', route: { name: 'map' } },
    { title: 'Performance', icon: 'leaderboard', route: { name: 'performance' } },
  ];
});

const managementLinks = ref([
  { title: 'Utilizadores', icon: 'group', route: { name: 'users' } },
  { title: 'Relatórios', icon: 'assessment', route: { name: 'reports' } },
]);

onMounted(() => {
  // Busca todos os dados essenciais uma única vez
  void vehicleStore.fetchAllVehicles();
  void journeyStore.fetchAllJourneys();

  if (authStore.isManager) {
    void userStore.fetchAllUsers();
    void notificationStore.fetchUnreadCount();
    pollTimer = window.setInterval(() => {
      void notificationStore.fetchUnreadCount();
    }, 60000);
  }
});

onUnmounted(() => { clearInterval(pollTimer); });
</script>

<style lang="scss" scoped>
/*
  Usamos um seletor mais específico (:deep) para garantir que nossa regra
  de cor de fundo seja aplicada corretamente sobre os estilos padrão do Quasar.
*/
:deep(.q-drawer) {
  background: #1a1616; /* Um cinza bem claro, como exemplo */
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