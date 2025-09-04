<template>
  <q-layout view="lHh Lpr lFf">
    <!-- CABEÇALHO PRINCIPAL COM DUAS BARRAS -->
    <q-header elevated class="main-header">
      <!-- Barra Superior: Logo e Controles do Usuário -->
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" class="lt-md toolbar-icon-btn" />
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

        <q-btn flat round dense icon="settings" to="/settings" class="q-mr-xs toolbar-icon-btn">
          <q-tooltip>Configurações</q-tooltip>
        </q-btn>
        
        <q-btn v-if="authStore.isManager" flat round dense icon="notifications" class="q-mr-sm toolbar-icon-btn">
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

      <!-- Barra de Navegação Principal (Visível em telas grandes) -->
      <div class="navigation-bar gt-sm">
        <q-btn
          v-for="link in essentialLinks"
          :key="link.title"
          :to="link.to"
          :icon="link.icon"
          :label="link.title"
          no-caps
          flat
          class="nav-button"
          active-class="nav-button--active"
        />
        <!-- Link de Admin separado -->
         <q-btn
          v-if="authStore.isSuperuser"
          to="/admin"
          icon="admin_panel_settings"
          label="Painel Admin"
          no-caps
          flat
          class="nav-button"
          active-class="nav-button--active"
        />
      </div>

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

    <!-- MENU LATERAL (Corrigido: sem 'show-if-above' para não aparecer em telas grandes) -->
    <q-drawer v-model="leftDrawerOpen" bordered class="lt-md">
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

    <!-- CONTAINER DA PÁGINA (O conteúdo começa abaixo do header) -->
    <q-page-container>
       <!-- IDEIA 3: Animações de Entrada -->
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
.main-header {
  background: linear-gradient(to right, $primary, lighten($primary, 8%));
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); // Sombra mais suave e moderna
}

.navigation-bar {
  padding: 0 16px;
  display: flex;
  gap: 8px;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

// IDEIA 4 e 5: Novo Estilo de Botão e Microinterações
.nav-button {
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  margin: 4px 0;
  border-radius: 8px;
  position: relative; // Necessário para o pseudo-elemento ::after

  // Remove o sublinhado ao passar o rato, agora o fundo muda
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
  }

  // O novo estilo do botão ativo
  &.nav-button--active {
    color: white;
    font-weight: 700;

    // A linha colorida por baixo
    &::after {
      content: '';
      position: absolute;
      bottom: -1px;
      left: 10%;
      right: 10%;
      height: 3px;
      background-color: $accent; // Usando a cor de acento (verde)
      border-radius: 2px;
      animation: grow-underline 0.3s ease-out;
    }
  }
}

// Animação para a linha do botão ativo
@keyframes grow-underline {
  from { width: 0; left: 50%; }
  to { width: 80%; left: 10%; }
}


// IDEIA 5: Microinterações para os ícones da barra de ferramentas
.toolbar-icon-btn {
  transition: transform 0.2s ease, color 0.2s ease;
  &:hover {
    transform: scale(1.15);
  }
}


// Estilo original do seu drawer (agora para mobile)
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

// IDEIA 3: Estilos para a animação de transição de página
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

