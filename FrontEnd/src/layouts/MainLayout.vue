<template>
  <q-layout view="lHh LpR lFf">
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

      <!-- ===== NOVA BARRA DE NAVEGAÇÃO COM MENUS EXPANSÍVEIS ===== -->
      <div class="navigation-bar gt-sm">
        <template v-for="category in menuStructure" :key="category.label">
          <!-- Se a categoria só tiver um item, mostra um botão simples -->
          
<q-btn
  v-if="category.children.length === 1"
  :to="category.children[0]!.to"
  :icon="category.children[0]!.icon"
  :label="category.children[0]!.title"
  no-caps flat class="nav-button" active-class="nav-button--active"
/>
          <!-- Se tiver múltiplos itens, mostra um menu expansível -->
          <q-btn-dropdown
            v-else
            :label="category.label"
            :icon="category.icon"
            no-caps flat
            class="nav-button"
            content-class="bg-primary-dark-menu"
          >
            <q-list dense>
              <q-item
                v-for="link in category.children"
                :key="link.title"
                :to="link.to"
                clickable v-close-popup
                class="nav-dropdown-item"
              >
                <q-item-section avatar><q-icon :name="link.icon" size="xs" /></q-item-section>
                <q-item-section><q-item-label>{{ link.title }}</q-item-label></q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
        </template>
        
        <!-- Link de Admin separado -->
         <q-btn v-if="authStore.isSuperuser" to="/admin" icon="admin_panel_settings" label="Painel Admin" no-caps flat class="nav-button" active-class="nav-button--active" />
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

    <!-- MENU LATERAL PARA TELAS PEQUENAS (lt-md) -->
    <q-drawer v-model="leftDrawerOpen" bordered class="lt-md">
      <q-scroll-area class="fit">
        <q-list padding>
          <q-item-label header>Menu</q-item-label>
          <!-- O menu lateral agora usa a nova estrutura de dados também -->
          <template v-for="category in menuStructure" :key="category.label + '-mobile'">
            <q-expansion-item
              :icon="category.icon"
              :label="category.label"
              expand-separator
              default-opened
            >
              <q-item v-for="link in category.children" :key="link.title" clickable :to="link.to" exact v-ripple class="q-pl-lg">
                <q-item-section avatar><q-icon :name="link.icon" /></q-item-section>
                <q-item-section><q-item-label>{{ link.title }}</q-item-label></q-item-section>
              </q-item>
            </q-expansion-item>
          </template>
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

    <q-page-container>
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

interface MenuItem {
  title: string;
  icon: string;
  to: string;
} 

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
    persistent: true
  });
}

// --- NOVA ESTRUTURA DE MENU ORGANIZADA ---
const menuStructure = computed(() => {
  const sector = authStore.userSector;
  const isManager = authStore.isManager;
  const menu = [];

  // --- Categoria: Geral ---
  const general = {
    label: 'Geral', icon: 'home',
    children: [
      { title: 'Dashboard', icon: 'dashboard', to: '/dashboard' },
      { title: 'Mapa em Tempo Real', icon: 'map', to: '/live-map' },
    ]
  };
  menu.push(general);

  // --- Categoria: Operações (Condicional) ---
const operations = { label: 'Operações', icon: 'alt_route', children: [] as MenuItem[] };
  if (sector === 'agronegocio' || sector === 'servicos') {
    operations.children.push({ title: terminologyStore.journeyPageTitle, icon: 'route', to: '/journeys' });
  }
  if (sector === 'frete' && isManager) {
    operations.children.push({ title: 'Ordens de Frete', icon: 'list_alt', to: '/freight-orders' });
  }
  if (sector === 'frete' && !isManager) { // Este é o 'driver'
    operations.children.push({ title: 'Minha Rota', icon: 'explore', to: '/driver-cockpit' });
  }
  if (operations.children.length > 0) {
    menu.push(operations);
  }

  // --- Categoria: Gestão (Apenas Gestores) ---
  if (isManager) {
const management = { label: 'Gestão', icon: 'settings_suggest', children: [] as MenuItem[] };
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
    
    // --- NOVOS LINKS ADICIONADOS ---
    management.children.push({ title: 'Gestão de Custos', icon: 'monetization_on', to: '/costs' });
    // --- LINK PARA ABASTECIMENTOS ADICIONADO AQUI ---
    management.children.push({ title: 'Registros de Abastecimento', icon: 'local_gas_station', to: '/fuel-logs' });
    management.children.push({ title: 'Gestão de Documentos', icon: 'folder_shared', to: '/documents' });
    // --- FIM DA ADIÇÃO ---

    if (management.children.length > 0) {
      menu.push(management);
    }
  }

  // --- Categoria: Análise (Apenas Gestores) ---
  if (isManager) {
    const analysis = {
      label: 'Análise', icon: 'analytics',
      children: [
        { title: 'Ranking de Motoristas', icon: 'leaderboard', to: '/performance' },
        { title: 'Relatórios', icon: 'summarize', to: '/reports' },
        { title: 'Manutenções', icon: 'build', to: '/maintenance' },
      ]
    };
    menu.push(analysis);
  }
  
  return menu;
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
.nav-dropdown-item {
  // A cor do texto agora é branca, com uma leve transparência para o estado normal
  color: rgba(168, 86, 86, 0.8);

  &.q-router-link--active,
  &:hover {
    color: rgb(56, 20, 20); // Cor sólida no hover e quando ativo
    background-color: rgba(rgb(121, 37, 37), 0.1);
    font-weight: 600;
  }
}
// O fundo do menu continua escuro em ambos os temas para garantir o contraste
.bg-primary-dark-menu {
  background-color: #2c3e50;
}

.main-header {
  background: linear-gradient(to right, $primary, lighten($primary, 8%));
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.navigation-bar {
  padding: 0 16px;
  display: flex;
  gap: 8px;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-button {
  transition: all 0.3s ease;
  color: rgb(255, 254, 254);
  font-weight: 500;
  margin: 4px 0;
  border-radius: 8px;
  position: relative;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
  }

  &.nav-button--active,
  &.q-btn-dropdown--current { // Para o dropdown ficar ativo
    color: white;
    font-weight: 700;
    background-color: rgba(0, 0, 0, 0.15);
  }
}

.nav-dropdown-item {
  // Cor padrão para o TEMA CLARO (texto escuro)
  color: $grey-9;

  // Estilo para o link ATIVO (página atual)
  &.q-router-link--active {
    color: $primary;
    background-color: rgba($primary, 0.1);
    font-weight: 600;
  }

  // Estilo para o HOVER (mouse sobre o item)
  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
}

// --- REGRAS PARA O TEMA ESCURO ---
.body--dark {
  .nav-dropdown-item {
    // Cor do texto para o TEMA ESCURO (texto claro)
    color: $grey-3;

    // Ajuste do hover para o tema escuro
    &:hover {
      background-color: rgba(255, 255, 255, 0.08);
    }
  }
}


.bg-primary-dark-menu {
  background-color: #3f658a;
}

.toolbar-icon-btn {
  transition: transform 0.2s ease, color 0.2s ease;
  &:hover {
    transform: scale(1.15);
  }
}

.q-drawer {
  background: #1a1616;
}
.q-drawer .q-list .q-item {
  color: $grey-2;
  .q-item__section--avatar { color: $grey-2; }
}
.q-drawer .q-list .q-item.q-router-link--active {
  color: $primary;
  font-weight: 600;
  background-color: rgba($primary, 0.1);
  border-left: 4px solid $primary;
  .q-item__section--avatar { color: $primary; }
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

